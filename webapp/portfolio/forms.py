from django import forms

from .source import TEXT_FIELDS


class ProjectImportForm(forms.Form):
    source_fingerprint = forms.CharField(widget=forms.HiddenInput)
    project_revision = forms.CharField(required=False, widget=forms.HiddenInput)
    apply_fields = forms.MultipleChoiceField(
        label="Fields to apply",
        required=False,
        choices=[(name, name.replace("_", " ").capitalize()) for name in TEXT_FIELDS],
        widget=forms.CheckboxSelectMultiple,
    )
    title = forms.CharField(max_length=255)
    category = forms.CharField(max_length=100, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    image_description = forms.CharField(max_length=255, required=False)
    website_url = forms.URLField(required=False)
    record_url = forms.URLField(required=False)
    import_image = forms.BooleanField(
        required=False, label="Import the source screenshot into Wagtail images"
    )

    def clean(self):
        data = super().clean()
        if not data.get("apply_fields") and not data.get("import_image"):
            raise forms.ValidationError(
                "Select at least one field or the screenshot to apply."
            )
        return data
