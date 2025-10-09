from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.user import User
from ..serializers import UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для пользователей.
    Только чтение, так как пользователи создаются через Telegram авторизацию.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только текущего пользователя"""
        return User.objects.filter(id=self.request.user.id)
