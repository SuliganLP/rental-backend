from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from .filters import ListingFilter
from .models import Listing
from .permissions import ListingPermission
from .serializers import ListingSerializer


class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = [ListingPermission]

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)

    filterset_class = ListingFilter

    search_fields = ("title", "description")

    ordering_fields = ("price", "created_at")

    ordering = ("-created_at",)

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Listing.objects.filter(Q(is_active=True) | Q(owner=user))

        return Listing.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
