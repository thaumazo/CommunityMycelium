from django import forms
from django.contrib.auth import get_user_model


def attach_creator_field(form, user, instance=None):
    """Let superadmins reassign the 'created_by' owner of an item being edited."""
    if not (user and user.is_authenticated and user.is_superuser):
        return
    if instance is None:
        instance = getattr(form, "instance", None)
    if not instance or not getattr(instance, "pk", None) or not hasattr(instance, "created_by"):
        return

    User = get_user_model()
    form.fields["created_by"] = forms.ModelChoiceField(
        queryset=User.objects.order_by("username"),
        required=True,
        initial=instance.created_by_id,
        label="Creator",
        help_text="Superadmin only: reassign who is listed as the creator of this item.",
    )


def apply_creator_field(form, user, instance):
    """Persist a superadmin-edited 'created_by' selection after form.save()."""
    if not (user and user.is_authenticated and user.is_superuser):
        return
    new_creator = getattr(form, "cleaned_data", {}).get("created_by")
    if new_creator and getattr(instance, "created_by_id", None) != new_creator.pk:
        instance.created_by = new_creator
        instance.save(update_fields=["created_by"])
