from django.db import models
from django.conf import settings


class Wallet(models.Model):
    uuid = models.UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_wallets")
    title = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'