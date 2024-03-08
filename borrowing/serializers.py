from datetime import datetime
from rest_framework import serializers
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateTimeField(format="%d-%m-%Y", default=datetime.now)
    expected_return_date = serializers.DateTimeField(format="%d-%m-%Y")
    actual_return_date = serializers.DateTimeField(format="%d-%m-%Y")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        ]


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "user", "book", "borrow_date", "expected_return_date", "actual_return_date")

class BorrowingDetailSerializer(BorrowingSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "user_email",
            "book_title",
            "is_active",
        ]

    def get_is_active(self, obj):
        return obj.actual_return_date is None
