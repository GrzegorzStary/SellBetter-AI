from django.shortcuts import render

from .forms import ListingRequestForm
from .ai_engine import generate_listing_result


def generate_listing_view(request):

    result = None

    if request.method == "POST":
        form = ListingRequestForm(request.POST)

        if form.is_valid():

            listing_request = form.save()

            result = generate_listing_result(listing_request)

    else:
        form = ListingRequestForm()

    return render(
        request,
        "listings/generator.html",
        {
            "form": form,
            "result": result,
        },
    )