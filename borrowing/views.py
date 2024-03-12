from datetime import datetime

import rest_framework_simplejwt.authentication
from django.db import transaction

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

        """Filter by user and active loan"""
        user = self.request.query_params.get("user")
        is_active = self.request.query_params.get("is_active")

        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        if is_active:
            is_active_bool = self._params_to_bool(is_active)
            queryset = queryset.filter(is_active=is_active_bool)

        """If this is a request for a list or details and the user is not an administrator,
        filter by user """

        if self.action in ("list", "retrieve") and not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

