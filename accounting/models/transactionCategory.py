from django.db import models
from django.conf import settings


class TransactionCategory(models.Model):
    uuid = models.UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_transaction_categories")
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
