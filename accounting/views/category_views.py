from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.transactionCategory import TransactionCategoryTree
from ..serializers import TransactionCategorySerializer


class TransactionCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает только категории текущего пользователя"""
        return TransactionCategoryTree.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически добавляет пользователя при создании"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Возвращает категории в виде дерева"""
        queryset = self.get_queryset()

        # Получаем только корневые категории
        root_categories = queryset.filter(parent__isnull=True)

        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def flat(self, request):
        """Возвращает плоский список всех категорий"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Удаление категории с проверкой на наличие транзакций"""
        instance = self.get_object()

        # Проверяем, есть ли транзакции в этой категории
        from ..models.transaction import Transaction
        transaction_count = Transaction.objects.filter(
            category=instance,
            user=request.user
        ).count()

        if transaction_count > 0:
            return Response(
                {'error': f'Нельзя удалить категорию с {transaction_count} транзакциями'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)
