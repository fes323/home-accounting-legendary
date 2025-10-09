# Исправление ошибки импорта UserViewSet

## Проблема
```
ImportError: cannot import name 'UserViewSet' from 'users.views'
```

## Решение

### 1. Создание UserViewSet

Создайте файл `users/views/user_views.py`:

```python
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
```

### 2. Обновление __init__.py

Обновите `users/views/__init__.py`:

```python
# Views для users app
from .user_views import UserViewSet

__all__ = ['UserViewSet']
```

### 3. Установка зависимостей

Установите недостающие пакеты:

```bash
pip install djangorestframework-simplejwt==5.3.0
pip install django-cors-headers==4.3.1
```

### 4. Выполнение миграций

После исправления ошибок выполните:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Дополнительные исправления

### Исправление полей в сериализаторах

В `accounting/serializers.py` исправьте поля:

```python
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['uuid', 'title', 'balance', 'currency', 'is_family_access']  # title вместо name

class TransactionSerializer(serializers.ModelSerializer):
    wallet_name = serializers.CharField(source='wallet.title', read_only=True)  # title вместо name
```

### Проверка моделей

Убедитесь, что все модели правильно импортированы в `accounting/models/__init__.py`:

```python
from accounting.models.currencyCBR import CurrencyCBR
from accounting.models.product import Product
from accounting.models.transaction import Transaction
from accounting.models.transactionCategory import TransactionCategoryTree
from accounting.models.transactionRow import TransactionRow
from accounting.models.wallet import Wallet
```

## Быстрое исправление на VPS

Выполните следующие команды на VPS:

```bash
# Перейдите в папку проекта
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary

# Активируйте виртуальное окружение
source ../venv/bin/activate

# Установите недостающие зависимости
pip install djangorestframework-simplejwt==5.3.0 django-cors-headers==4.3.1

# Выполните миграции
python manage.py makemigrations
python manage.py migrate

# Создайте суперпользователя (если нужно)
python manage.py createsuperuser

# Соберите статические файлы
python manage.py collectstatic
```

## Проверка работы

После исправления проверьте:

1. **Django сервер**:
   ```bash
   python manage.py runserver
   ```

2. **API endpoints**:
   - `http://localhost:8000/api/transactions/`
   - `http://localhost:8000/api/categories/`
   - `http://localhost:8000/api/wallets/`

3. **Telegram Bot**:
   ```bash
   python manage.py run_bot
   ```

## Если ошибки продолжаются

1. Проверьте логи Django
2. Убедитесь, что все файлы загружены на VPS
3. Проверьте права доступа к файлам
4. Убедитесь, что виртуальное окружение активировано
