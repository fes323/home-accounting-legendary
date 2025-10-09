from rest_framework import serializers

from .models.transaction import Transaction
from .models.transactionCategory import TransactionCategoryTree
from .models.wallet import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['uuid', 'name', 'balance', 'currency', 'is_family_access']


class TransactionCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = TransactionCategoryTree
        fields = ['uuid', 'title', 'description',
                  'parent', 'children', 'created_at']

    def get_children(self, obj):
        children = obj.get_children()
        return TransactionCategorySerializer(children, many=True).data


class TransactionSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(
        source='category.title', read_only=True)
    wallet_name = serializers.CharField(source='wallet.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'uuid', 't_type', 'amount', 'tax', 'description', 'date',
            'created_at', 'updated_at', 'category', 'category_title',
            'wallet', 'wallet_name'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Добавляем пользователя из контекста
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Убеждаемся, что пользователь не может изменить транзакцию другого пользователя
        if instance.user != self.context['request'].user:
            raise serializers.ValidationError(
                "Недостаточно прав для изменения этой транзакции")
        return super().update(instance, validated_data)
