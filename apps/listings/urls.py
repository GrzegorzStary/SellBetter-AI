from django.urls import path
from .views import index_view, generate_listing_view

urlpatterns = [
    path("", index_view, name="home"),
    path("generate/", generate_listing_view, name="generate"),
]