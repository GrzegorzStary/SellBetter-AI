from django.shortcuts import render

from .forms import ListingRequestForm, ImageAnalysisForm
from .ai_engine import generate_listing_result, detect_product_from_images


def index_view(request):
    return render(request, "index.html")


def generate_listing_view(request):
    result = None
    detected_data = None

    if request.method == "POST":
        if "analyze_image" in request.POST:
            image_form = ImageAnalysisForm(request.POST, request.FILES)
            form = ListingRequestForm()

            if image_form.is_valid():
                images = request.FILES.getlist("images")

                try:
                    detected_data = detect_product_from_images(images)
                except ValueError as e:
                    image_form.add_error("images", str(e))
                except Exception:
                    image_form.add_error(
                        "images",
                        "Image analysis failed. Please try different images."
                    )
                else:
                    form = ListingRequestForm(
                        initial={
                            "item_name": detected_data.get("item_name", ""),
                            "category": detected_data.get("category", ""),
                            "platform": detected_data.get("platform", "ebay"),
                            "condition": detected_data.get("condition", "good"),
                            "tone": detected_data.get("tone", "simple"),
                            "brand": detected_data.get("brand", ""),
                            "size_details": detected_data.get("size_details", ""),
                            "color": detected_data.get("color", ""),
                            "material": detected_data.get("material", ""),
                            "flaws": detected_data.get("flaws", ""),
                            "raw_notes": detected_data.get("raw_notes", ""),
                        }
                    )

        else:
            form = ListingRequestForm(request.POST, request.FILES)
            image_form = ImageAnalysisForm()

            if form.is_valid():
                try:
                    listing_request = form.save()
                    result = generate_listing_result(listing_request)
                except Exception:
                    form.add_error(
                        None,
                        "Listing generation failed. Please review your details and try again."
                    )

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