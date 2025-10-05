import uuid

from django.db import models

from users.models.user import User


class Family(models.Model):
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="user_families")
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name="family_members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'users'
        verbose_name = 'Семья'
        verbose_name_plural = 'Семьи'

    def __str__(self):
        return f"[{self.owner.username}] {self.title}"
