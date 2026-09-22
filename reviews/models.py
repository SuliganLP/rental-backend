from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    listing = models.ForeignKey("listings.Listing", on_delete=models.CASCADE, related_name="reviews")

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "author"],
                name="unique_review_per_listing_author",
            )
        ]

    def __str__(self):
        return (
            f"{self.author.email} - "
            f"{self.listing.title}: "
            f"{self.rating}/5"
        )
