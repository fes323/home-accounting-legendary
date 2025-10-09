# Исправление ошибки basename в DRF Router

## Проблема
```
AssertionError: `basename` argument not specified, and could not automatically determine the name from the viewset, as it does not have a `.queryset` attribute.
```

## Причина
Django REST Framework не может автоматически определить `basename` для ViewSet, если у него нет атрибута `.queryset`.

## Решение

### 1. Добавление basename в роутер

В файле `accounting/urls.py` добавьте `basename` для каждого ViewSet:

```python
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'categories', TransactionCategoryViewSet, basename='category')
router.register(r'wallets', WalletViewSet, basename='wallet')
```

### 2. Команды для исправления на VPS

Выполните следующие команды на VPS:

```bash
# Перейдите в папку проекта
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary

# Активируйте виртуальное окружение
source ../venv/bin/activate

# Исправьте accounting/urls.py
sed -i "s/router.register(r'transactions', TransactionViewSet)/router.register(r'transactions', TransactionViewSet, basename='transaction')/" accounting/urls.py
sed -i "s/router.register(r'categories', TransactionCategoryViewSet)/router.register(r'categories', TransactionCategoryViewSet, basename='category')/" accounting/urls.py
sed -i "s/router.register(r'wallets', WalletViewSet)/router.register(r'wallets', WalletViewSet, basename='wallet')/" accounting/urls.py

# Проверьте исправление
cat accounting/urls.py
```

### 3. Альтернативное решение через редактор

Если команда `sed` не работает, отредактируйте файл вручную:

```bash
# Откройте файл в nano
nano accounting/urls.py

# Найдите строки:
# router.register(r'transactions', TransactionViewSet)
# router.register(r'categories', TransactionCategoryViewSet)
# router.register(r'wallets', WalletViewSet)

# Замените на:
# router.register(r'transactions', TransactionViewSet, basename='transaction')
# router.register(r'categories', TransactionCategoryViewSet, basename='category')
# router.register(r'wallets', WalletViewSet, basename='wallet')

# Сохраните файл (Ctrl+X, Y, Enter)
```

### 4. Проверка исправления

После исправления выполните:

```bash
# Проверьте синтаксис Python
python -m py_compile accounting/urls.py

# Если ошибок нет, выполните миграции
python manage.py makemigrations
python manage.py migrate
```

### 5. Альтернативное решение - добавление queryset

Если не хотите использовать `basename`, можно добавить атрибут `queryset` в ViewSet:

```python
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()  # Добавить эту строку
    serializer_class = TransactionSerializer
    # ... остальной код
```

Но использование `basename` предпочтительнее.

## Правила для basename

### 1. Именование
- Используйте единственное число
- Используйте строчные буквы
- Используйте подчеркивания для разделения слов

### 2. Примеры
```python
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'user-profiles', UserProfileViewSet, basename='user_profile')
router.register(r'api-keys', ApiKeyViewSet, basename='api_key')
```

### 3. Проверка URL
После добавления `basename` проверьте доступные URL:

```bash
python manage.py show_urls | grep api
```

## Дополнительные проверки

### 1. Проверка ViewSet
```bash
# Проверьте, что ViewSet правильно определены
python -c "
from accounting.views.transaction_views import TransactionViewSet
print('TransactionViewSet OK')
print('Serializer:', TransactionViewSet.serializer_class)
"
```

### 2. Проверка импортов
```bash
# Проверьте импорты в urls.py
python -c "
from accounting.urls import router
print('Router OK')
print('URLs:', [url.name for url in router.urls])
"
```

### 3. Проверка Django
```bash
python manage.py check
```

## Быстрое исправление

Если нужно быстро исправить проблему, выполните:

```bash
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary
source ../venv/bin/activate

# Исправление basename
sed -i "s/router.register(r'transactions', TransactionViewSet)/router.register(r'transactions', TransactionViewSet, basename='transaction')/" accounting/urls.py
sed -i "s/router.register(r'categories', TransactionCategoryViewSet)/router.register(r'categories', TransactionCategoryViewSet, basename='category')/" accounting/urls.py
sed -i "s/router.register(r'wallets', WalletViewSet)/router.register(r'wallets', WalletViewSet, basename='wallet')/" accounting/urls.py

# Проверка
python manage.py makemigrations
```

После этого Django должен запускаться без ошибок basename.
