from django import forms
from .models import ListingRequest


class ListingRequestForm(forms.ModelForm):
    """
    Form used to generate the final listing after AI analysis.
    """

    class Meta:
        model = ListingRequest
        fields = [
            "item_name",
            "category",
            "platform",
            "condition",
            "tone",
            "brand",
            "size_details",
            "color",
            "material",
            "flaws",
            "raw_notes",
            "image",
        ]


class MultipleFileInput(forms.ClearableFileInput):
    """
    Allows selecting multiple files in the input.
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    Custom field to support multiple uploaded files.
    """
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []

        for file in data:
            cleaned_files.append(super().clean(file, initial))

        return cleaned_files


class ImageAnalysisForm(forms.Form):
    """
    Form used for AI image analysis.
    Allows uploading up to 10 images.
    """

    images = MultipleFileField(
        required=True,
        help_text="Upload up to 10 images for better AI analysis.",
    )

    def clean_images(self):
        images = self.files.getlist("images")

        if not images:
            raise forms.ValidationError("Please upload at least one image.")

        if len(images) > 10:
            raise forms.ValidationError("You can upload a maximum of 10 images.")

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        max_size = 10 * 1024 * 1024  # 10MB

        for image in images:

            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    f"{image.name} is not a supported format. Use JPG, PNG or WEBP."
                )

            if image.size > max_size:
                raise forms.ValidationError(
                    f"{image.name} is too large. Maximum file size is 10MB."
                )

        return images