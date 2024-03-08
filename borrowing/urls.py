from django.urls import path, include
from rest_framework import routers
from borrowing.views import BorrowingViewSet, BorrowingReturnView

router = routers.DefaultRouter()
router.register("", BorrowingViewSet)


urlpatterns = [
    path("", include(router.urls)),
    # path(
    #     "borrowings/?user_id=<int:pk>/&is_active=<bool>/",
    #     BorrowingViewSet,
    #     name="borrowings-by-user-and-active-status",
    # ),
    path(
        "borrowings/<int:pk>/return/", BorrowingReturnView.as_view(), name="return_book"
    ),
]

app_name = "borrowing"
