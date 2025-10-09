import uuid

from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class TransactionCategoryTree(MPTTModel):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="user_transaction_categories")
    title = models.CharField(max_length=255)
    svg_file = models.FileField(
        upload_to='upload/TransactionCategoryTree/svgs/', blank=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = 'Категория транзакции'
        verbose_name_plural = 'Категории транзакции'
        unique_together = [['user', 'title', 'parent']]

    def __str__(self):
        return self.title
