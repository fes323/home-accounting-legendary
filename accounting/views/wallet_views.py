from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models.wallet import Wallet
from ..serializers import WalletSerializer


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только кошельки текущего пользователя"""
        return Wallet.objects.filter(user=self.request.user)
