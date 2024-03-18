from datetime import datetime
from datetime import date
import rest_framework_simplejwt.authentication
from django.db import transaction
from django.db.models import Q


from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response


from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    @staticmethod
    def _params_to_bool(qs: str) -> bool:
        """Converts a str to bool True or False"""
        return qs.lower() == "true"

    def get_queryset(self):
        queryset = self.queryset

        """Filter by user"""
        user = self.request.query_params.get("user_id")
        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        """Filter by active loan"""
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = self._params_to_bool(is_active)
            if is_active_bool:
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.filter(actual_return_date__isnull=False)

        """If this is a request for a list or details and the user is not an administrator, filter by user """
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "borrowing_return":
            context["request"] = self.request

        return context



    @action(
        detail=True,
        methods=["post"],
        url_path="return",
        serializer_class=BorrowingReturnSerializer,
    )
    def borrowing_return(self, request, pk=None):
        """Endpoint for returning borrowing book"""
        borrowing = self.get_object()
        book = borrowing.book
        actual_return_date = datetime.now().date()

        serializer_update = BorrowingReturnSerializer(
            borrowing,
            context={"request": self.request},
            data={"actual_return_date": actual_return_date},
            partial=True,
        )
        serializer_update.is_valid(raise_exception=True)
        serializer_update.save()
        return Response({"status": "borrowing returned"})

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
