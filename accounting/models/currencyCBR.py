from django.db import models
import uuid
from django.utils import timezone


class CurrencyCBR(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    num_code = models.SmallIntegerField(unique=True)
    char_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=255)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_default_currency(cls):
        currencyCBR, created = cls.objects.get_or_create(num_code=643, char_code='RUB', name='Российский рубль')
        return currencyCBR.pk

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'
