from django.db import models
from accounting.models import Transaction


class TransactionRow(models.Model):
    uuid = models.UUIDField(primary_key=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="transaction_rows")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)