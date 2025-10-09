# Исправление ошибки относительного импорта

## Проблема
```
ImportError: attempted relative import beyond top-level package
```

## Причина
Неправильный относительный импорт в файле `users/views/auth_views.py`:
```python
from ...users.serializers import TelegramAuthSerializer, UserSerializer
```

## Решение

### 1. Исправление импорта в auth_views.py

Замените строку:
```python
from ...users.serializers import TelegramAuthSerializer, UserSerializer
```

На:
```python
from users.serializers import TelegramAuthSerializer, UserSerializer
```

### 2. Команды для исправления на VPS

Выполните следующие команды на VPS:

```bash
# Перейдите в папку проекта
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary

# Активируйте виртуальное окружение
source ../venv/bin/activate

# Исправьте импорт в auth_views.py
sed -i 's/from ...users.serializers import/from users.serializers import/' users/views/auth_views.py

# Проверьте исправление
cat users/views/auth_views.py | grep "from users.serializers import"
```

### 3. Альтернативное решение через редактор

Если у вас есть доступ к редактору на VPS:

```bash
# Откройте файл в nano
nano users/views/auth_views.py

# Найдите строку:
# from ...users.serializers import TelegramAuthSerializer, UserSerializer

# Замените на:
# from users.serializers import TelegramAuthSerializer, UserSerializer

# Сохраните файл (Ctrl+X, Y, Enter)
```

### 4. Проверка исправления

После исправления выполните:

```bash
# Проверьте синтаксис Python
python -m py_compile users/views/auth_views.py

# Если ошибок нет, выполните миграции
python manage.py makemigrations
python manage.py migrate
```

### 5. Если ошибки продолжаются

Проверьте другие файлы на наличие неправильных относительных импортов:

```bash
# Поиск всех относительных импортов
grep -r "from \.\.\." . --include="*.py"

# Поиск импортов users
grep -r "from.*users\." . --include="*.py"
```

## Правильные импорты для Django

### Внутри приложения (users/)
```python
# Правильно
from users.serializers import UserSerializer
from users.models import User

# Неправильно
from ...users.serializers import UserSerializer
from ..serializers import UserSerializer
```

### Между приложениями
```python
# Правильно
from accounting.models import Transaction
from users.models import User

# Неправильно
from ..accounting.models import Transaction
```

## Дополнительные проверки

### 1. Проверка структуры проекта
```bash
find . -name "*.py" -path "*/users/*" | head -10
```

### 2. Проверка __init__.py файлов
```bash
find . -name "__init__.py" | grep users
```

### 3. Проверка импортов Django
```bash
python manage.py check
```

## Быстрое исправление

Если нужно быстро исправить проблему, выполните:

```bash
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary
source ../venv/bin/activate

# Исправление импорта
sed -i 's/from ...users.serializers import/from users.serializers import/' users/views/auth_views.py

# Проверка
python manage.py makemigrations
```

После этого Django должен запускаться без ошибок импорта.
