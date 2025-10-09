import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from accounting.models.transactionCategory import TransactionCategoryTree
from accounting.models.wallet import Wallet


class Transaction(models.Model):

    CHOICES = (
        ("IN", "INCOME"),
        ("EX", "EXPENSE"),
    )

    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    t_type = models.CharField(choices=CHOICES, max_length=2)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="wallet_transactions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_transactions")
    category = models.ForeignKey(TransactionCategoryTree, on_delete=models.CASCADE,
                                 related_name="category_transactions", blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, blank=True)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Тарнзакция'
        verbose_name_plural = 'Тарнзакции'

    def __str__(self):
        return f'[{self.user.username}] ' + str(self.t_type) + ': ' + str(self.amount)
