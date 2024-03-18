from django.shortcuts import render
from rest_framework import mixins, viewsets

from book.permissions import IsAdminOrIfAuthenticatedReadOnly
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Payment.objects.all().select_related("borrowing__user")
    serializer_class = PaymentSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
