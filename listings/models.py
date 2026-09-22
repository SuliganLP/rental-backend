from django.db import models
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator


class Listing(models.Model):
    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartment"
        HOUSE = "house", "House"
        STUDIO = "studio", "Studio"
        ROOM = "room", "Room"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    city = models.CharField(max_length=100)

    district = models.CharField(max_length=100, blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    rooms = models.PositiveSmallIntegerField()

    property_type = models.CharField(max_length=20, choices=PropertyType.choices)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
