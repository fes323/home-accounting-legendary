#!/bin/bash

# Скрипт для настройки и запуска Django приложения и Telegram бота
# Выполните этот скрипт с правами root: sudo bash setup_services.sh

echo "Настройка сервисов для Home Accounting Legendary..."

# Создание директории для логов
sudo mkdir -p /var/log/django
sudo chown walletapp:walletapp /var/log/django

# Создание директорий для статических файлов и медиа
sudo mkdir -p /var/www/wallet.my-bucket.ru/static
sudo mkdir -p /var/www/wallet.my-bucket.ru/media
sudo chown -R walletapp:walletapp /var/www/wallet.my-bucket.ru

# Копирование service файлов в systemd
sudo cp wallet-app.service /etc/systemd/system/
sudo cp wallet-bot.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение сервисов
sudo systemctl enable wallet-app.service
sudo systemctl enable wallet-bot.service

# Создание базы данных PostgreSQL
echo "Создание базы данных..."
sudo -u postgres createdb HAL_production
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE HAL_production TO postgres;"

# Переключение на пользователя приложения для выполнения Django команд
sudo -u walletapp bash << 'EOF'
cd /var/www/wallet.my-bucket.ru/home-accounting-legendary
source /var/www/wallet.my-bucket.ru/venv/bin/activate

# Сбор статических файлов
python manage.py collectstatic --noinput --settings=core.settings.production

# Выполнение миграций
python manage.py migrate --settings=core.settings.production

# Создание суперпользователя (опционально)
echo "Создание суперпользователя..."
python manage.py createsuperuser --settings=core.settings.production
EOF

# Запуск сервисов
echo "Запуск сервисов..."
sudo systemctl start wallet-app.service
sudo systemctl start wallet-bot.service

# Проверка статуса
echo "Проверка статуса сервисов..."
sudo systemctl status wallet-app.service
sudo systemctl status wallet-bot.service

echo "Настройка завершена!"
echo "Проверьте логи командой: sudo journalctl -u wallet-app -f"
echo "Проверьте логи бота командой: sudo journalctl -u wallet-bot -f"
