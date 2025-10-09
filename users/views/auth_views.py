from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.serializers import TelegramAuthSerializer, UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth(request):
    """
    Авторизация через Telegram WebApp
    """
    serializer = TelegramAuthSerializer(data=request.data)

    if serializer.is_valid():
        try:
            user = serializer.save()

            # Создаем или получаем токен
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    """
    Получение профиля текущего пользователя
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
