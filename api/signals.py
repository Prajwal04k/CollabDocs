from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AnonymousUser
from .models import Document, DocumentVersion, AuditLog


@receiver(post_save, sender=Document)
def create_document_version_and_audit_log(sender, instance, created, **kwargs):
    """
    Create a DocumentVersion and AuditLog entry when a Document is created or updated.
    This signal runs after a Document is saved.
    """
    # Determine if this is a create or update
    is_creating = created

    # Create DocumentVersion
    version_number = instance.versions.count() + 1
    DocumentVersion.objects.create(
        document=instance,
        content=instance.content,
        version_number=version_number,
        created_by=instance.created_by,
    )

    # Create AuditLog
    action = 'created' if is_creating else 'updated'
    actor = instance.created_by if isinstance(instance.created_by, type(instance._state)) or instance.created_by else None

    AuditLog.objects.create(
        actor=actor,
        action=action,
        model_name='Document',
        object_id=str(instance.id),
    )
