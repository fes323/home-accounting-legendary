#!/bin/bash

# Скрипт для настройки VPS Ubuntu для Home Accounting Legendary

echo "🚀 Настройка VPS для Home Accounting Legendary..."

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка Python 3.11 и pip
echo "🐍 Установка Python 3.11..."
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Node.js больше не нужен для Django Mini App
echo "📱 Node.js больше не требуется для Django Mini App..."

# Установка PostgreSQL
echo "🐘 Установка PostgreSQL..."
apt install -y postgresql postgresql-contrib

# Установка nginx
echo "🌐 Установка nginx..."
apt install -y nginx

# Установка дополнительных пакетов
echo "🔧 Установка дополнительных пакетов..."
apt install -y git curl wget build-essential libpq-dev

# Создание пользователя для приложения
echo "👤 Создание пользователя для приложения..."
useradd -m -s /bin/bash wallet
usermod -aG sudo wallet

# Создание директорий
echo "📁 Создание директорий..."
mkdir -p /var/www/wallet.my-bucket.ru
chown -R wallet:wallet /var/www/wallet.my-bucket.ru

# Настройка PostgreSQL
echo "🗄️ Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE wallet_db;"
sudo -u postgres psql -c "CREATE USER wallet_user WITH PASSWORD 'wallet_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE wallet_db TO wallet_user;"
sudo -u postgres psql -c "ALTER USER wallet_user CREATEDB;"

# Настройка nginx
echo "🌐 Настройка nginx..."
cp /var/www/wallet.my-bucket.ru/home-accounting-legendary/server/nginx_wallet_config.conf /etc/nginx/sites-available/wallet.my-bucket.ru
ln -sf /etc/nginx/sites-available/wallet.my-bucket.ru /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Создание SSL сертификатов (самоподписанные для тестирования)
echo "🔒 Создание SSL сертификатов..."
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/wallet.my-bucket.ru.key \
    -out /etc/nginx/ssl/wallet.my-bucket.ru.crt \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Wallet/OU=IT/CN=wallet.my-bucket.ru"

# Настройка systemd сервисов
echo "⚙️ Настройка systemd сервисов..."

# Django сервис
cat > /etc/systemd/system/wallet-app.service << EOF
[Unit]
Description=Wallet Django App
After=network.target

[Service]
Type=exec
User=wallet
Group=wallet
WorkingDirectory=/var/www/wallet.my-bucket.ru/home-accounting-legendary
Environment=DJANGO_SETTINGS_MODULE=core.settings.production
ExecStart=/var/www/wallet.my-bucket.ru/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Telegram Bot сервис
cat > /etc/systemd/system/wallet-bot.service << EOF
[Unit]
Description=Wallet Telegram Bot
After=network.target

[Service]
Type=exec
User=wallet
Group=wallet
WorkingDirectory=/var/www/wallet.my-bucket.ru/home-accounting-legendary
Environment=DJANGO_SETTINGS_MODULE=core.settings.production
ExecStart=/var/www/wallet.my-bucket.ru/venv/bin/python manage.py run_bot --webhook
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd
systemctl daemon-reload

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chown -R wallet:wallet /var/www/wallet.my-bucket.ru
chmod -R 755 /var/www/wallet.my-bucket.ru

# Создание .env файла
echo "📝 Создание .env файла..."
cat > /var/www/wallet.my-bucket.ru/home-accounting-legendary/.env << EOF
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://wallet_user:wallet_password@localhost:5432/wallet_db
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
ALLOWED_HOSTS=wallet.my-bucket.ru,localhost,127.0.0.1
WEBHOOK_URL=https://wallet.my-bucket.ru/telegram/
WEBHOOK_SECRET=your-webhook-secret
EOF

chown wallet:wallet /var/www/wallet.my-bucket.ru/home-accounting-legendary/.env
chmod 600 /var/www/wallet.my-bucket.ru/home-accounting-legendary/.env

echo "✅ Настройка VPS завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Перейдите в папку проекта: cd /var/www/wallet.my-bucket.ru/home-accounting-legendary"
echo "2. Активируйте виртуальное окружение: source ../venv/bin/activate"
echo "3. Установите зависимости: pip install -r requirements.txt"
echo "4. Выполните миграции: python manage.py migrate"
echo "5. Создайте суперпользователя: python manage.py createsuperuser"
echo "6. Соберите статические файлы: python manage.py collectstatic"
echo "7. Настройте React приложение: cd frontend && npm install && npm run build"
echo "8. Запустите сервисы: systemctl start wallet-app wallet-bot nginx"
echo "9. Включите автозапуск: systemctl enable wallet-app wallet-bot nginx"
echo ""
echo "🔧 Не забудьте отредактировать .env файл с вашими настройками!"
