from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.db import transaction
from django.contrib.auth.models import User

from .models import (
    Workspace,
    WorkspaceMember,
    Document,
    DocumentVersion,
    Comment,
    Tag,
    AuditLog,
)
from .serializers import (
    UserSerializer,
    WorkspaceSerializer,
    WorkspaceMemberSerializer,
    DocumentSerializer,
    DocumentVersionSerializer,
    CommentSerializer,
    TagSerializer,
    AuditLogSerializer,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint 1-2: User management
    GET /api/users/me/ - current user profile
    GET /api/users/{id}/ - user details
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    Endpoints 3-8: Workspace management
    POST /api/workspaces/ - create (add owner as member)
    GET /api/workspaces/ - list
    GET /api/workspaces/{id}/ - detail
    PUT /api/workspaces/{id}/ - update
    DELETE /api/workspaces/{id}/ - delete
    POST /api/workspaces/{id}/invite/ - add member
    """
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.select_related('owner').filter(
            Q(owner=self.request.user) | Q(members__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        """Create workspace and add owner as admin member"""
        workspace = serializer.save(owner=self.request.user)
        # Add owner as admin member
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=self.request.user,
            role=WorkspaceMember.RoleChoices.ADMIN,
        )

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite a user to workspace"""
        workspace = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', WorkspaceMember.RoleChoices.MEMBER)

        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            return Response({'error': 'User is already a member'}, status=status.HTTP_400_BAD_REQUEST)

        member = WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role=role,
        )
        serializer = WorkspaceMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Endpoints 9-15: Document management
    POST /api/documents/ - create (atomic + version)
    GET /api/documents/ - list with filtering
    GET /api/documents/{id}/ - detail
    PUT /api/documents/{id}/ - update (atomic + version)
    DELETE /api/documents/{id}/ - delete
    GET /api/documents/{id}/versions/ - list versions
    POST /api/documents/{id}/tags/ - assign tags
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter documents by workspace membership and apply search filters"""
        user = self.request.user
        queryset = Document.objects.select_related(
            'created_by',
            'workspace',
            'workspace__owner'
        ).prefetch_related('tags').annotate(
            version_count=Count('versions'),
            comment_count=Count('comments'),
        ).filter(
            Q(workspace__owner=user) | Q(workspace__members__user=user)
        ).distinct()

        # Apply search filters
        title = self.request.query_params.get('title')
        status = self.request.query_params.get('status')
        workspace = self.request.query_params.get('workspace')
        tag = self.request.query_params.get('tag')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if status:
            queryset = queryset.filter(status=status)
        if workspace:
            queryset = queryset.filter(workspace__id=workspace)
        if tag:
            queryset = queryset.filter(tags__id=tag)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        """Create document atomically with version"""
        document = serializer.save(created_by=self.request.user)

    @transaction.atomic
    def perform_update(self, serializer):
        """Update document atomically with version"""
        document = serializer.save()

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of a document"""
        document = self.get_object()
        versions = document.versions.all().order_by('-version_number')
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def tags(self, request, pk=None):
        """Assign tags to a document"""
        document = self.get_object()
        tag_ids = request.data.get('tag_ids', [])

        try:
            tags = Tag.objects.filter(id__in=tag_ids)
            document.tags.set(tags)
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Endpoints 16-17: Comment management
    POST /api/comments/ - create
    GET /api/comments/?document_id=X - list by document
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter comments by document and exclude replies from main list"""
        queryset = Comment.objects.select_related('author', 'document').prefetch_related('replies')

        document_id = self.request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(document__id=document_id, parent__isnull=True)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Create comment with current user as author"""
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint 18: Tag management
    GET /api/tags/ - list all tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint 19: Audit logging
    GET /api/audit-logs/ - list (admin only)
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only allow admins to view audit logs"""
        if not self.request.user.is_staff:
            return AuditLog.objects.none()
        return AuditLog.objects.select_related('actor').order_by('-timestamp')
