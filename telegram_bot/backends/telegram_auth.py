"""
Кастомный backend аутентификации для Telegram WebApp
"""
import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

from ..telegram_auth import get_telegram_user_from_webapp

logger = logging.getLogger(__name__)


class TelegramWebAppAuthBackend(BaseBackend):
    """
    Backend аутентификации для Telegram WebApp

    Использует данные Telegram WebApp для аутентификации пользователей
    и сохраняет их в сессии Django для последующих запросов.
    """

    def authenticate(self, request, telegram_data=None, **kwargs):
        """
        Аутентификация пользователя через Telegram WebApp данные

        Args:
            request: HTTP запрос
            telegram_data: Данные от Telegram WebApp
            **kwargs: Дополнительные параметры

        Returns:
            User объект или None
        """
        if not telegram_data:
            return None

        try:
            # Парсим и проверяем данные Telegram WebApp
            user_data = get_telegram_user_from_webapp(
                telegram_data,
                verify_signature=True
            )

            if not user_data:
                logger.warning("Failed to parse Telegram WebApp data")
                return None

            telegram_id = user_data.get('id')
            if not telegram_id:
                logger.warning("No telegram_id in user data")
                return None

            # Ищем или создаем пользователя
            user = self._get_or_create_user(user_data)

            if user:
                # Сохраняем данные аутентификации в сессии
                self._store_auth_data_in_session(request, user_data)
                logger.info(
                    f"User authenticated: {user.username} (telegram_id: {telegram_id})")

            return user

        except Exception as e:
            logger.error(f"Error in Telegram WebApp authentication: {e}")
            return None

    def get_user(self, user_id):
        """
        Получение пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            User объект или None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _get_or_create_user(self, user_data: dict) -> Optional[User]:
        """
        Получение или создание пользователя на основе данных Telegram

        Args:
            user_data: Данные пользователя от Telegram

        Returns:
            User объект или None
        """
        telegram_id = user_data.get('id')
        username = user_data.get('username') or f"tg_{telegram_id}"

        # Ищем существующего пользователя
        user = User.objects.filter(telegram_id=telegram_id).first()

        if not user:
            # Создаем нового пользователя
            user = User.objects.create(
                telegram_id=telegram_id,
                username=username,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
            )
            logger.info(
                f"Created new user: {user.username} (telegram_id: {telegram_id})")
        else:
            # Обновляем данные существующего пользователя
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
            logger.info(
                f"Updated existing user: {user.username} (telegram_id: {telegram_id})")

        return user

    def _store_auth_data_in_session(self, request, user_data: dict):
        """
        Сохранение данных аутентификации в сессии

        Args:
            request: HTTP запрос
            user_data: Данные пользователя от Telegram
        """
        if not request.session:
            return

        # Сохраняем только необходимые данные
        auth_data = {
            'telegram_id': user_data.get('id'),
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'auth_method': 'telegram_webapp',
            'authenticated_at': user_data.get('auth_date'),
        }

        request.session['telegram_auth'] = auth_data
        request.session['telegram_authenticated'] = True

        # Устанавливаем время жизни сессии
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        logger.debug(
            f"Stored auth data in session for user: {user_data.get('id')}")


class TelegramWebAppSessionBackend(BaseBackend):
    """
    Backend для аутентификации через сессию

    Используется для последующих запросов после первоначальной аутентификации
    через Telegram WebApp
    """

    def authenticate(self, request, **kwargs):
        """
        Аутентификация через сессию

        Args:
            request: HTTP запрос
            **kwargs: Дополнительные параметры

        Returns:
            User объект или None
        """
        if not request.session:
            return None

        # Проверяем флаг аутентификации в сессии
        if not request.session.get('telegram_authenticated', False):
            return None

        auth_data = request.session.get('telegram_auth')
        if not auth_data:
            return None

        telegram_id = auth_data.get('telegram_id')
        if not telegram_id:
            return None

        try:
            # Получаем пользователя по telegram_id
            user = User.objects.filter(telegram_id=telegram_id).first()

            if user:
                logger.debug(
                    f"User authenticated via session: {user.username}")
                return user
            else:
                # Пользователь не найден, очищаем сессию
                self._clear_auth_session(request)
                logger.warning(
                    f"User not found for telegram_id: {telegram_id}")

        except Exception as e:
            logger.error(f"Error in session authentication: {e}")
            self._clear_auth_session(request)

        return None

    def get_user(self, user_id):
        """
        Получение пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            User объект или None
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _clear_auth_session(self, request):
        """
        Очистка данных аутентификации из сессии

        Args:
            request: HTTP запрос
        """
        if request.session:
            request.session.pop('telegram_auth', None)
            request.session.pop('telegram_authenticated', None)
            logger.debug("Cleared auth data from session")
