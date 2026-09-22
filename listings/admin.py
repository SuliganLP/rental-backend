from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "owner",
        "city",
        "price",
        "property_type",
        "is_active",
        "created_at"
    )

    list_filter = ("property_type", "is_active", "city")

    search_fields = ("title", "description", "city")
