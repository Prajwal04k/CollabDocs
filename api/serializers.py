from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Count
from .models import (
    Workspace,
    WorkspaceMember,
    Document,
    DocumentVersion,
    Comment,
    Tag,
    AuditLog,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ['id', 'workspace', 'user', 'user_id', 'role', 'created_at']
        read_only_fields = ['id', 'workspace', 'created_at']

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in WorkspaceMember.RoleChoices.choices]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Invalid role. Must be one of {valid_roles}")
        return value

    def validate(self, attrs):
        workspace = self.context.get('workspace')
        user_id = attrs.get('user_id')
        if workspace and user_id:
            if WorkspaceMember.objects.filter(workspace=workspace, user_id=user_id).exists():
                raise serializers.ValidationError("User is already a member of this workspace")
        return attrs


class WorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'owner', 'is_active', 'members', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

    def get_members(self, obj):
        members = WorkspaceMember.objects.filter(workspace=obj)
        return WorkspaceMemberSerializer(members, many=True).data


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = DocumentVersion
        fields = ['id', 'document', 'content', 'version_number', 'created_by', 'created_at']
        read_only_fields = ['id', 'document', 'version_number', 'created_by', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'document', 'author', 'text', 'parent', 'replies', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class DocumentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    version_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'content',
            'status',
            'workspace',
            'created_by',
            'tags',
            'tag_ids',
            'version_count',
            'comment_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Document.StatusChoices.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of {valid_statuses}")
        return value

    def get_version_count(self, obj):
        return obj.versions.count()

    def get_comment_count(self, obj):
        return obj.comments.count()


class AuditLogSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'actor', 'action', 'model_name', 'object_id', 'timestamp']
        read_only_fields = ['id', 'actor', 'timestamp']
