from django.contrib.auth import authenticate
from rest_framework import serializers

from .models.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'username', 'first_name',
                  'last_name', 'telegram_id', 'total_balance']
        read_only_fields = ['uuid', 'total_balance']


class TelegramAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    auth_date = serializers.IntegerField()
    hash = serializers.CharField()

    def validate(self, attrs):
        # Проверяем обязательные поля
        if not attrs.get('id'):
            raise serializers.ValidationError("Telegram ID is required")

        if not attrs.get('first_name'):
            raise serializers.ValidationError("First name is required")

        # Проверяем дату авторизации (не старше 24 часов)
        import time
        current_time = int(time.time())
        auth_date = attrs.get('auth_date', 0)
        if current_time - auth_date > 86400:  # 24 часа
            raise serializers.ValidationError("Authorization data is too old")

        # TODO: Добавить проверку подписи Telegram для безопасности
        # Для этого нужно использовать TELEGRAM_BOT_TOKEN и проверить hash
        return attrs

    def create(self, validated_data):
        telegram_id = validated_data['id']

        # Ищем существующего пользователя
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            # Создаем нового пользователя
            username = validated_data.get('username') or f"user_{telegram_id}"
            user = User.objects.create(
                telegram_id=telegram_id,
                username=username,
                first_name=validated_data['first_name'],
                last_name=validated_data.get('last_name', ''),
            )

        return user
