from datetime import datetime, timedelta

from django.db import models
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models.transaction import Transaction
from ..serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['t_type', 'category', 'wallet', 'date']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Возвращает только транзакции текущего пользователя"""
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически добавляет пользователя при создании"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Статистика по транзакциям"""
        queryset = self.get_queryset()

        # Фильтры по дате
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Подсчет статистики
        total_income = queryset.filter(t_type='IN').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        total_expense = queryset.filter(t_type='EX').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

        balance = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'transaction_count': queryset.count()
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Последние транзакции"""
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
