from django.contrib import admin
from .models import ListingRequest, ListingResult



@admin.register(ListingRequest)
class ListingRequestAdmin(admin.ModelAdmin):
    list_display = ("item_name", "platform", "condition", "tone", "created_at")
    list_filter = ("platform", "condition", "tone")
    search_fields = ("item_name", "brand", "category")
    
@admin.register(ListingResult)
class ListingResultAdmin(admin.ModelAdmin):

    list_display = (
        "request",
        "quick_sale_price",
        "fair_price",
        "premium_price",
        "created_at",
    )