from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Review
from .permissions import ReviewPermission
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("author", "listing")

    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]

    filter_backends = (DjangoFilterBackend,)

    filterset_fields = ("listing", "rating")

    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
