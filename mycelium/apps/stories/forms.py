from django import forms
from .models import Story, StoryMedia, StoryLink
from apps.locations.models import Location


class StoryForm(forms.ModelForm):
    view_members = forms.BooleanField(
        required=False,
        initial=False,
        label="View Members",
        help_text="Check if authenticated members can view this story.",
    )

    view_public = forms.BooleanField(
        required=False,
        initial=False,
        label="View Public",
        help_text="Check if public (unauthenticated) users can view this story.",
    )

    attachment_targets = forms.CharField(
        required=False,
        label="Attach To (multiple)",
        help_text="One per line: app_label.model_name:id (example: projects.project:12)",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "projects.project:12\nbioregions.bioregion:2"}),
    )

    geo_pins_input = forms.CharField(
        required=False,
        label="Geo Pins (multiple)",
        help_text="One per line: latitude,longitude,label(optional),radius_m(optional)",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "49.282700,-123.120700,Origin,500\n49.250000,-122.900000,Impact zone,2500"}),
    )

    linked_story_ids = forms.CharField(
        required=False,
        label="Linked Story IDs",
        help_text="Comma-separated story IDs to link from this story.",
        widget=forms.TextInput(attrs={"placeholder": "14, 27, 31"}),
    )

    story_link_relation = forms.ChoiceField(
        required=False,
        choices=StoryLink.RELATION_CHOICES,
        label="Link Relation",
        initial=StoryLink.RELATION_CONTINUATION,
    )

    primary_location = forms.ModelChoiceField(
        queryset=Location.objects.all().order_by("title"),
        required=False,
        label="Primary Location",
        help_text="Primary map location for this story.",
    )

    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all().order_by("title"),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "w-full"}),
        label="Locations",
        help_text="Locations connected to this story.",
    )
    
    class Meta:
        model = Story
        fields = [
            "title",
            "text_content",
            "youtube_url",
            "primary_location",
            "locations",
            "view_members",
            "view_public",
            "time_precision",
            "event_start_at",
            "event_end_at",
        ]
        widgets = {
            "text_content": forms.Textarea(attrs={"rows": 8}),
            "youtube_url": forms.URLInput(attrs={"placeholder": "https://www.youtube.com/watch?v=..."}),
            "event_start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "event_end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            attachment_lines = []
            for attachment in instance.attachments.all():
                attachment_lines.append(
                    f"{attachment.content_type.app_label}.{attachment.content_type.model}:{attachment.object_id}"
                )
            self.fields["attachment_targets"].initial = "\n".join(attachment_lines)

            pin_lines = []
            for pin in instance.geo_pins.all():
                parts = [str(pin.latitude), str(pin.longitude)]
                if pin.label:
                    parts.append(pin.label)
                if pin.radius_m is not None:
                    if not pin.label:
                        parts.append("")
                    parts.append(str(pin.radius_m))
                pin_lines.append(",".join(parts))
            self.fields["geo_pins_input"].initial = "\n".join(pin_lines)

            linked_ids = [str(link.to_story_id) for link in instance.outbound_links.all()]
            self.fields["linked_story_ids"].initial = ", ".join(linked_ids)
            first_link = instance.outbound_links.first()
            if first_link:
                self.fields["story_link_relation"].initial = first_link.relation_type

    def clean(self):
        cleaned = super().clean()
        time_precision = cleaned.get("time_precision")
        event_start_at = cleaned.get("event_start_at")
        event_end_at = cleaned.get("event_end_at")

        if time_precision == Story.TIME_PRECISION_POINT:
            if not event_start_at:
                self.add_error("event_start_at", "Point-in-time stories require event_start_at.")
            cleaned["event_end_at"] = None

        if time_precision == Story.TIME_PRECISION_RANGE:
            if not event_start_at:
                self.add_error("event_start_at", "Range stories require event_start_at.")
            if not event_end_at:
                self.add_error("event_end_at", "Range stories require event_end_at.")

        if time_precision == Story.TIME_PRECISION_NONE:
            cleaned["event_start_at"] = None
            cleaned["event_end_at"] = None

        primary_location = cleaned.get("primary_location")
        locations = cleaned.get("locations")
        if primary_location and locations is not None and primary_location not in locations:
            cleaned["locations"] = locations | Location.objects.filter(pk=primary_location.pk)

        return cleaned


class StoryMediaForm(forms.ModelForm):
    class Meta:
        model = StoryMedia
        fields = ["media_type", "file", "url", "caption", "order"]
        widgets = {
            "caption": forms.Textarea(attrs={"rows": 3}),
        }
