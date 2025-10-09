# Решение проблемы конфликта Telegram бота

## Проблема
При запуске бота командой `python manage.py run_bot` возникает ошибка:
```
ERROR:aiogram.dispatcher:Failed to fetch updates - TelegramConflictError: 
Telegram server says - Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

## Причина
Эта ошибка возникает, когда уже запущен другой экземпляр бота с тем же токеном. Telegram API не позволяет нескольким экземплярам одного бота работать одновременно.

## Решения

### 1. Быстрое решение (рекомендуется)
Используйте скрипт `fix_bot_conflict.py`:
```bash
python fix_bot_conflict.py
```

### 2. Ручное решение

#### Шаг 1: Остановите все экземпляры бота
```bash
python manage.py stop_bot --force
```

#### Шаг 2: Запустите бота заново
```bash
python manage.py run_bot
```

### 3. Использование флагов команды run_bot

#### Автоматическая остановка существующих экземпляров:
```bash
python manage.py run_bot --kill-existing
```

#### Принудительный запуск (игнорировать конфликты):
```bash
python manage.py run_bot --force
```

## Новые команды

### `run_bot` - Запуск бота
```bash
python manage.py run_bot [опции]

Опции:
  --webhook          Запустить в режиме webhook вместо polling
  --kill-existing    Остановить все существующие экземпляры бота перед запуском
  --force           Принудительно запустить бота, игнорируя конфликты
```

### `stop_bot` - Остановка всех экземпляров бота
```bash
python manage.py stop_bot [опции]

Опции:
  --force           Принудительно завершить процессы (kill)
```

## Предотвращение проблемы

1. **Всегда корректно завершайте бота** - используйте `Ctrl+C` вместо закрытия терминала
2. **Проверяйте активные процессы** перед запуском:
   ```bash
   python manage.py stop_bot  # покажет активные процессы без остановки
   ```
3. **Используйте флаг `--kill-existing`** при разработке:
   ```bash
   python manage.py run_bot --kill-existing
   ```

## Устранение неполадок

### Если бот не останавливается
1. Найдите процесс вручную:
   ```bash
   # Windows
   tasklist | findstr python
   
   # Linux/Mac
   ps aux | grep run_bot
   ```
2. Завершите процесс принудительно:
   ```bash
   # Windows
   taskkill /PID <номер_процесса> /F
   
   # Linux/Mac
   kill -9 <номер_процесса>
   ```

### Если проблема повторяется
1. Проверьте, нет ли других скриптов, запускающих бота
2. Убедитесь, что не запущены системные сервисы бота
3. Проверьте переменные окружения и токен бота
