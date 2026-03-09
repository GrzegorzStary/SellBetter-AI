from django.urls import path
from .views import generate_listing_view


urlpatterns = [
    path("generate/", generate_listing_view, name="generate_listing"),
]