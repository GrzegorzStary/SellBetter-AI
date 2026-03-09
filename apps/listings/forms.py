from django import forms
from .models import ListingRequest


class ListingRequestForm(forms.ModelForm):

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
        ]