from django.db import models
from accounting.models.transaction import Transaction
import uuid


class TransactionRow(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="transaction_rows")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Строка тарнзакции'
        verbose_name_plural = 'Строки тарнзакции'