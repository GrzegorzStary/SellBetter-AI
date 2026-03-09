from django.db import models


class ListingRequest(models.Model):
    PLATFORM_CHOICES = [
        ("facebook", "Facebook Marketplace"),
        ("ebay", "eBay"),
        ("vinted", "Vinted"),
    ]

    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("very_good", "Very Good"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("parts", "For Parts / Repair"),
    ]

    TONE_CHOICES = [
        ("simple", "Simple"),
        ("premium", "Premium"),
        ("fast_sale", "Fast Sale"),
    ]

    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)

    brand = models.CharField(max_length=100, blank=True)
    size_details = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=100, blank=True)
    flaws = models.TextField(blank=True)
    raw_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} ({self.platform})"
    
class ListingResult(models.Model):
    request = models.ForeignKey(
        ListingRequest,
        on_delete=models.CASCADE,
        related_name="results"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    bullet_points = models.TextField()
    tags = models.CharField(max_length=255, blank=True)

    quick_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    fair_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    premium_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Result for {self.request.item_name}"