from django.test import TestCase

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking
from listings.models import Listing

from .models import Review


User = get_user_model()


class ReviewAPITests(APITestCase):

    def setUp(self):
        self.landlord = User.objects.create_user(
            username="landlord",
            email="landlord@example.com",
            password="StrongPassword123!",
            role=User.Role.LANDLORD,
        )

        self.tenant = User.objects.create_user(
            username="tenant",
            email="tenant@example.com",
            password="StrongPassword123!",
            role=User.Role.TENANT,
        )

        self.other_tenant = User.objects.create_user(
            username="tenant2",
            email="tenant2@example.com",
            password="StrongPassword123!",
            role=User.Role.TENANT,
        )

        self.listing = Listing.objects.create(
            owner=self.landlord,
            title="Test Apartment",
            description="Test description",
            city="Mönchengladbach",
            district="Gladbach",
            price="850.00",
            rooms=2,
            property_type=Listing.PropertyType.APARTMENT,
            is_active=True,
        )

        self.today = timezone.localdate()

    def create_completed_booking(self):
        return Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            start_date=self.today - timedelta(days=10),
            end_date=self.today - timedelta(days=5),
            status=Booking.Status.CONFIRMED,
        )

    def test_tenant_without_completed_booking_cannot_review(self):
        self.client.force_authenticate(
            user=self.tenant
        )

        data = {
            "listing": self.listing.id,
            "rating": 5,
            "comment": "Great apartment.",
        }

        response = self.client.post(
            reverse("review-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_tenant_with_completed_booking_can_review(self):
        self.create_completed_booking()

        self.client.force_authenticate(
            user=self.tenant
        )

        data = {
            "listing": self.listing.id,
            "rating": 5,
            "comment": "Great apartment.",
        }

        response = self.client.post(
            reverse("review-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        review = Review.objects.get()

        self.assertEqual(
            review.author,
            self.tenant,
        )

        self.assertEqual(
            review.rating,
            5,
        )

    def test_duplicate_review_is_rejected(self):
        self.create_completed_booking()

        Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            rating=5,
            comment="First review",
        )

        self.client.force_authenticate(
            user=self.tenant
        )

        data = {
            "listing": self.listing.id,
            "rating": 4,
            "comment": "Second review",
        }

        response = self.client.post(
            reverse("review-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_rating_above_five_is_rejected(self):
        self.create_completed_booking()

        self.client.force_authenticate(
            user=self.tenant
        )

        data = {
            "listing": self.listing.id,
            "rating": 6,
            "comment": "Invalid rating",
        }

        response = self.client.post(
            reverse("review-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_other_user_cannot_update_review(self):
        review = Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            rating=5,
            comment="Original comment",
        )

        self.client.force_authenticate(
            user=self.other_tenant
        )

        response = self.client.patch(
            reverse(
                "review-detail",
                args=[review.id],
            ),
            {
                "rating": 1,
                "comment": "Changed comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        review.refresh_from_db()

        self.assertEqual(
            review.rating,
            5,
        )

        self.assertEqual(
            review.comment,
            "Original comment",
        )

    def test_anonymous_user_can_view_reviews(self):
        Review.objects.create(
            listing=self.listing,
            author=self.tenant,
            rating=5,
            comment="Public review",
        )

        response = self.client.get(
            reverse("review-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["rating"],
            5,
        )