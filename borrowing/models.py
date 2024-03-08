from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateTimeField()
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings")

    def __str__(self) -> str:
        borrow_date = self.borrow_date.strftime("%d-%m-%Y")
        return f"{self.user} - {self.book} - {borrow_date}"

    def save(self, *args, **kwargs):
        if self.book.inventory == 0:
            raise ValidationError('This book is not available for borrowing.')
        super(Borrowing, self).save(*args, **kwargs)


@receiver(pre_save, sender=Borrowing)
def reduce_inventory_on_borrow(instance, **kwargs):
    if not instance.pk:  # New instance is being created
        book = instance.book
        book.inventory -= 1
        book.save()

