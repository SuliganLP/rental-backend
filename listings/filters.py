import django_filters

from .models import Listing


class ListingFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte"
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte"
    )

    min_rooms = django_filters.NumberFilter(
        field_name="rooms",
        lookup_expr="gte"
    )

    max_rooms = django_filters.NumberFilter(
        field_name="rooms",
        lookup_expr="lte"
    )

    city = django_filters.CharFilter(
        field_name="city",
        lookup_expr="icontains"
    )

    district = django_filters.CharFilter(
        field_name="district",
        lookup_expr="icontains"
    )

    class Meta:
        model = Listing
        fields = (
            "property_type",
            "city",
            "district",
            "min_price",
            "max_price",
            "min_rooms",
            "max_rooms",
        )