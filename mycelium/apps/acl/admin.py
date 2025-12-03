from django.contrib import admin
from django import forms
from .models import ModelPermission, ObjectPermission


class ModelPermissionForm(forms.ModelForm):
    actions = forms.MultipleChoiceField(
        choices=ModelPermission.ACTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Actions',
        help_text='Select all permissions to grant for this model type'
    )
    
    class Meta:
        model = ModelPermission
        fields = ['user', 'content_type', 'actions']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing, populate with current action
        if self.instance.pk:
            self.fields['actions'].initial = [self.instance.action]
    
    def save(self, commit=True):
        # We'll handle creating multiple ModelPermission objects
        # This is a bit of a workaround since we're storing one action per record
        user = self.cleaned_data['user']
        content_type = self.cleaned_data['content_type']
        actions = self.cleaned_data['actions']
        
        if self.instance.pk:
            # If editing, delete the old one and create new ones
            self.instance.delete()
        
        # Create a ModelPermission for each selected action
        instances = []
        for action in actions:
            instance = ModelPermission.objects.create(
                user=user,
                content_type=content_type,
                action=action
            )
            instances.append(instance)
        
        # Return the first one (admin expects a single instance)
        return instances[0] if instances else self.instance
    
    def save_m2m(self):
        # No many-to-many fields to save, but admin expects this method
        pass


@admin.register(ModelPermission)
class ModelPermissionAdmin(admin.ModelAdmin):
    form = ModelPermissionForm
    list_display = ['user', 'action', 'content_type']
    list_filter = ['action', 'content_type']
    search_fields = ['user__username', 'user__email']


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'content_type', 'object_id', 'content_object']
    list_filter = ['action', 'content_type']
    search_fields = ['user__username', 'user__email']
