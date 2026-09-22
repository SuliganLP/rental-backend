from django.utils import timezone
from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    tenant = serializers.ReadOnlyField(source="tenant.email")

    class Meta:
        model = Booking
        fields = (
            "id",
            "listing",
            "tenant",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "tenant", "status", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        listing = attrs.get("listing")
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if user.role != "tenant":
            raise serializers.ValidationError("Only tenants can create bookings.")

        if not listing.is_active:
            raise serializers.ValidationError("This listing is not active.")

        if listing.owner == user:
            raise serializers.ValidationError("You cannot book your own listing.")

        if start_date < timezone.localdate():
            raise serializers.ValidationError({"start_date": "Start date cannot be in the past."})

        if end_date <= start_date:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})

        overlapping_booking = Booking.objects.filter(
            listing=listing,
            status__in=[
                Booking.Status.PENDING,
                Booking.Status.CONFIRMED,
            ],
            start_date__lt=end_date,
            end_date__gt=start_date,
        ).exists()

        if overlapping_booking:
            raise serializers.ValidationError("The listing is already booked for these dates.")

        return attrs
