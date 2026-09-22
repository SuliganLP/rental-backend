from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Listing

User = get_user_model()


class ListingAPITests(APITestCase):

    def setUp(self):
        self.landlord = User.objects.create_user(
            username="landlord",
            email="landlord@example.com",
            password="StrongPassword123!",
            role=User.Role.LANDLORD,
        )

        self.other_landlord = User.objects.create_user(
            username="otherlandlord",
            email="otherlandlord@example.com",
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
            title="Apartment in Cologne",
            description="Modern apartment near city center",
            city="Cologne",
            district="Innenstadt",
            price="900.00",
            rooms=2,
            property_type=Listing.PropertyType.APARTMENT,
            is_active=True,
        )

    def test_anonymous_user_can_view_active_listings(self):
        response = self.client.get(
            reverse("listing-list")
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
            response.data[0]["title"],
            "Apartment in Cologne",
        )

    def test_landlord_can_create_listing(self):
        self.client.force_authenticate(
            user=self.landlord
        )

        data = {
            "title": "House in Düsseldorf",
            "description": "Large family house",
            "city": "Düsseldorf",
            "district": "Bilk",
            "price": "1500.00",
            "rooms": 4,
            "property_type": Listing.PropertyType.HOUSE,
            "is_active": True,
        }

        response = self.client.post(
            reverse("listing-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        listing = Listing.objects.get(
            title="House in Düsseldorf"
        )

        self.assertEqual(
            listing.owner,
            self.landlord,
        )

    def test_tenant_cannot_create_listing(self):
        self.client.force_authenticate(
            user=self.tenant
        )

        data = {
            "title": "Tenant Apartment",
            "description": "Should not be created",
            "city": "Bonn",
            "district": "Zentrum",
            "price": "800.00",
            "rooms": 2,
            "property_type": Listing.PropertyType.APARTMENT,
            "is_active": True,
        }

        response = self.client.post(
            reverse("listing-list"),
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_other_landlord_cannot_update_listing(self):
        self.client.force_authenticate(
            user=self.other_landlord
        )

        response = self.client.patch(
            reverse(
                "listing-detail",
                args=[self.listing.id],
            ),
            {
                "price": "500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.listing.refresh_from_db()

        self.assertEqual(
            str(self.listing.price),
            "900.00",
        )

    def test_anonymous_user_does_not_see_inactive_listing(self):
        Listing.objects.create(
            owner=self.landlord,
            title="Inactive Listing",
            description="Hidden apartment",
            city="Cologne",
            district="Ehrenfeld",
            price="700.00",
            rooms=1,
            property_type=Listing.PropertyType.STUDIO,
            is_active=False,
        )

        response = self.client.get(
            reverse("listing-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            listing["title"]
            for listing in response.data
        ]

        self.assertNotIn(
            "Inactive Listing",
            titles,
        )

    def test_search_and_price_filter(self):
        Listing.objects.create(
            owner=self.landlord,
            title="Luxury House",
            description="Big house with garden",
            city="Düsseldorf",
            district="Oberkassel",
            price="2000.00",
            rooms=5,
            property_type=Listing.PropertyType.HOUSE,
            is_active=True,
        )

        search_response = self.client.get(
            reverse("listing-list"),
            {
                "search": "Luxury",
            },
        )

        self.assertEqual(
            search_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(search_response.data),
            1,
        )

        self.assertEqual(
            search_response.data[0]["title"],
            "Luxury House",
        )

        filter_response = self.client.get(
            reverse("listing-list"),
            {
                "min_price": "1500",
            },
        )

        self.assertEqual(
            filter_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(filter_response.data),
            1,
        )

        self.assertEqual(
            filter_response.data[0]["title"],
            "Luxury House",
        )
