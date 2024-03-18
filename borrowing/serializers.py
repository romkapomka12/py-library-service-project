from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateField(format="%d-%m-%Y", default=datetime.now)
    expected_return_date = serializers.DateField(format="%d-%m-%Y")
    actual_return_date = serializers.DateField(format="%d-%m-%Y")
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        ]

    def get_is_active(self, obj):
        return obj.actual_return_date is None


class BorrowingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )

    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        book = validated_data["book"]
        book.inventory -= 1
        book.save()
        return borrowing

    def validate_expected_return_date(self, value):
        if value < datetime.now().date():
            raise ValidationError(
                detail="The expected return date cannot be in the past"
            )
        return value

    def validate_book(self, value):
        if value.inventory == 0:
            raise serializers.ValidationError(
                f"Book - {value.title} -  out of stock at this moment"
            )
        return value

    def validate_user(self, value):
        # Exclude admin users from book availability check
        if value.is_staff or value.is_superuser:
            raise serializers.ValidationError(
                "Admin users cannot borrow books. Please select a different user."
            )
        return value


class BorrowingDetailSerializer(BorrowingSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "user_email",
            "book_title",
            "is_active",
        ]

    def get_is_active(self, obj):
        return obj.actual_return_date is None


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )
        read_only_fields = ("id", "borrow_date", "expected_return_date")

    @transaction.atomic
    def validate(self, attrs):
        borrowing = self.instance
        if borrowing.actual_return_date is not None:
            raise ValidationError(detail="Borrowing has been already returned.")

        # actual_return_date = datetime.now().date()
        # expected_return_date = borrowing.expected_return_date
        # if actual_return_date > expected_return_date:
        #     overdue_period = (actual_return_date - expected_return_date).days

        return super().validate(attrs=attrs)

    def update(self, instance, validated_data):
        book = instance.book
        instance.actual_return_date = datetime.now().date()
        instance.save()
        book.inventory += 1
        book.save()
        return instance
