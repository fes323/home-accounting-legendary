from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        app_label = 'users'
