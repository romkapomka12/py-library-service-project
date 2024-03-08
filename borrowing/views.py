from datetime import date

from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from book.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_superuser:
    #         return Borrowing.objects.all()
    #     else:
    #         return Borrowing.objects.filter(user=user)

    # def get_queryset(self):
    #     return self.queryset.filter(user=self.user.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        elif self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def _params_to_bool(qs: str) -> bool:
        """Converts a str to bool True or False"""
        return qs.lower() == "true"

    @api_view(["GET"])
    def get_borrowings_by_user_id(request):
        user_id = request.query_params.get("user_id")
        is_active_param = request.query_params.get("is_active")

        if is_active_param is not None:
            is_active = True if is_active_param.lower() == "true" else False
            borrowings = Borrowing.objects.filter(user_id=user_id, is_active=is_active)
        else:
            borrowings = Borrowing.objects.filter(user_id=user_id)

        serializer = BorrowingDetailSerializer(borrowings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BorrowingReturnView(APIView):
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def post(self, request, borrowing_id):
        borrowing = Borrowing.objects.get(id=borrowing_id)

        if borrowing.actual_return_date:
            return Response(
                {"error": "Book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = date.today()
        borrowing.save()

        # Increment the inventory count of the returned book
        returned_book = borrowing.book
        returned_book.inventory_count += 1
        returned_book.save()

        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
