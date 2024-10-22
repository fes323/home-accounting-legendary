from django.db import models
from django.conf import settings
from accounting.models import TransactionCategory
from accounting.models import Wallet


class Transaction(models.Model):

    CHOICES = (
        ("IN", "INCOME"),
        ("EX", "EXPENSE"),
    )

    uuid = models.UUIDField(primary_key=True)
    t_type = models.CharField(choices=CHOICES, max_length=2)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="wallet_transactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_transactions")
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, related_name="category_transactions", blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Тарнзакция'
        verbose_name_plural = 'Тарнзакции'

    def __str__(self):
        return f'[{self.user.username}] ' + str(self.t_type) + ': ' + str(self.amount)