from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking
from .permissions import BookingPermission
from .serializers import BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [BookingPermission]

    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Booking.objects.none()

        return Booking.objects.filter(
            Q(tenant=user)
            | Q(listing__owner=user)
        ).select_related(
            "tenant",
            "listing",
            "listing__owner",
        )

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        booking = self.get_object()

        if booking.status != Booking.Status.PENDING:
            return Response({"detail": "Only pending bookings can be confirmed."},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response({"detail": "Only pending bookings can be rejected."},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.Status.REJECTED
        booking.save(update_fields=["status", "updated_at"])

        return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()

        allowed_statuses = (
            Booking.Status.PENDING,
            Booking.Status.CONFIRMED,
        )

        if booking.status not in allowed_statuses:
            return Response({"detail": "This booking cannot be cancelled."},
                            status=status.HTTP_400_BAD_REQUEST
                            )

        if booking.start_date <= timezone.localdate():
            return Response(
                {
                    "detail": (
                        "Booking cannot be cancelled "
                        "after it has started."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

        return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def active(self, request):
        today = timezone.localdate()

        bookings = self.get_queryset().filter(
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED], end_date__gte=today)

        serializer = self.get_serializer(bookings, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def completed(self, request):
        today = timezone.localdate()

        bookings = self.get_queryset().filter(
            status=Booking.Status.CONFIRMED,
            end_date__lt=today,
        )

        serializer = self.get_serializer(
            bookings,
            many=True,
        )

        return Response(serializer.data)
