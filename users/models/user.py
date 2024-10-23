from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)

    class Meta:
        app_label = 'users'
