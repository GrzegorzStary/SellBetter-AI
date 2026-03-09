from django.shortcuts import render

from .forms import ListingRequestForm, ImageAnalysisForm
from .ai_engine import generate_listing_result, detect_product_from_image


def generate_listing_view(request):
    result = None
    detected_data = None

    if request.method == "POST":
        if "analyze_image" in request.POST:
            image_form = ImageAnalysisForm(request.POST, request.FILES)
            form = ListingRequestForm()

            if image_form.is_valid():
                detected_data = detect_product_from_image(
                    image_form.cleaned_data["image"]
                )

                form = ListingRequestForm(initial={
                    "item_name": detected_data.get("item_name", ""),
                    "category": detected_data.get("category", ""),
                    "color": detected_data.get("color", ""),
                    "material": detected_data.get("material", ""),
                    "raw_notes": detected_data.get("raw_notes", ""),
                    "platform": "ebay",
                    "condition": "good",
                    "tone": "simple",
                })
        else:
            form = ListingRequestForm(request.POST, request.FILES)
            image_form = ImageAnalysisForm()

            if form.is_valid():
                listing_request = form.save()
                result = generate_listing_result(listing_request)
    else:
        form = ListingRequestForm()
        image_form = ImageAnalysisForm()

    return render(
        request,
        "listings/generator.html",
        {
            "form": form,
            "image_form": image_form,
            "result": result,
            "detected_data": detected_data,
        },
    )