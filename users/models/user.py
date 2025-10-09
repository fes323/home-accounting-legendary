import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Case, DecimalField, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce


class User(AbstractUser):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    telegram_id = models.IntegerField(unique=True, null=True, blank=True)
    total_balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=0.00)

    class Meta:
        app_label = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
