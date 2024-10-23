from django.db import models
from django.conf import settings
import uuid


class Wallet(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_wallets")
    title = models.CharField(max_length=255)
    svg_file = models.FileField(upload_to='upload/Wallet/svgs/', blank=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return f'[{self.user.username}] {self.title}'