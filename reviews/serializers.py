from django.utils import timezone
from rest_framework import serializers

from bookings.models import Booking

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.email")

    class Meta:
        model = Review
        fields = (
            "id",
            "listing",
            "author",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        )

        read_only_fields = ("id", "author", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        listing = attrs.get("listing", getattr(self.instance, "listing", None))

        if self.instance is not None:
            new_listing = attrs.get("listing")

            if new_listing is not None and new_listing != self.instance.listing:
                raise serializers.ValidationError({"listing": "Listing cannot be changed after review creation."})

        if listing.owner == user:
            raise serializers.ValidationError("You cannot review your own listing")

        completed_booking_exists = (
            Booking.objects.filter(
                listing=listing,
                tenant=user,
                status=Booking.Status.CONFIRMED,
                end_date__lt=timezone.localdate(),
            ).exists()
        )

        if not completed_booking_exists:
            raise serializers.ValidationError(
                "You can review only a listing "
                "that you have already rented."
            )

        if self.instance is None:
            review_exists = Review.objects.filter(
                listing=listing,
                author=user,
            ).exists()

            if review_exists:
                raise serializers.ValidationError("You have already reviewed this listing.")

        return attrs
