from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from listings.models import Listing

from .models import Booking


User = get_user_model()


class BookingAPITests(APITestCase):

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

    def test_tenant_can_create_booking(self):
        self.client.force_authenticate(
            user=self.tenant
        )

        data = {
            "listing": self.listing.id,
            "start_date": self.today + timedelta(days=10),
            "end_date": self.today + timedelta(days=15),
        }

        response = self.client.post(
            reverse("booking-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        booking = Booking.objects.get()

        self.assertEqual(
            booking.tenant,
            self.tenant,
        )

        self.assertEqual(
            booking.status,
            Booking.Status.PENDING,
        )

    def test_landlord_cannot_create_booking(self):
        self.client.force_authenticate(
            user=self.landlord
        )

        data = {
            "listing": self.listing.id,
            "start_date": self.today + timedelta(days=10),
            "end_date": self.today + timedelta(days=15),
        }

        response = self.client.post(
            reverse("booking-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_overlapping_booking_is_rejected(self):
        Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=15),
            status=Booking.Status.PENDING,
        )

        second_tenant = User.objects.create_user(
            username="tenant2",
            email="tenant2@example.com",
            password="StrongPassword123!",
            role=User.Role.TENANT,
        )

        self.client.force_authenticate(
            user=second_tenant
        )

        data = {
            "listing": self.listing.id,
            "start_date": self.today + timedelta(days=12),
            "end_date": self.today + timedelta(days=18),
        }

        response = self.client.post(
            reverse("booking-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_landlord_can_confirm_booking(self):
        booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=15),
        )

        self.client.force_authenticate(
            user=self.landlord
        )

        response = self.client.post(
            reverse(
                "booking-confirm",
                args=[booking.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        booking.refresh_from_db()

        self.assertEqual(
            booking.status,
            Booking.Status.CONFIRMED,
        )

    def test_tenant_cannot_confirm_booking(self):
        booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=15),
        )

        self.client.force_authenticate(
            user=self.tenant
        )

        response = self.client.post(
            reverse(
                "booking-confirm",
                args=[booking.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_can_cancel_booking(self):
        booking = Booking.objects.create(
            listing=self.listing,
            tenant=self.tenant,
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=15),
            status=Booking.Status.CONFIRMED,
        )

        self.client.force_authenticate(
            user=self.tenant
        )

        response = self.client.post(
            reverse(
                "booking-cancel",
                args=[booking.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        booking.refresh_from_db()

        self.assertEqual(
            booking.status,
            Booking.Status.CANCELLED,
        )