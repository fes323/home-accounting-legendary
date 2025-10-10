#!/bin/bash

# Скрипт для установки SSL сертификата Let's Encrypt
# Использование: sudo bash setup_ssl_certificate.sh

set -e

DOMAIN="wallet.my-bucket.ru"
NGINX_CONFIG="/etc/nginx/sites-available/$DOMAIN"

echo "🔧 Установка SSL сертификата Let's Encrypt для $DOMAIN"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Запустите скрипт с правами root (sudo)"
    exit 1
fi

# Обновление пакетов
echo "📦 Обновление пакетов..."
apt update

# Установка Certbot
echo "🔧 Установка Certbot..."
apt install -y certbot python3-certbot-nginx

# Остановка nginx
echo "⏹️ Остановка nginx..."
systemctl stop nginx

# Получение сертификата
echo "🔐 Получение SSL сертификата..."
certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Проверка успешного получения сертификата
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ Ошибка получения сертификата"
    exit 1
fi

# Копирование обновленной конфигурации nginx
echo "📝 Обновление конфигурации nginx..."
if [ -f "$NGINX_CONFIG" ]; then
    cp $NGINX_CONFIG ${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)
    echo "💾 Создана резервная копия: ${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Проверка конфигурации nginx
echo "🔍 Проверка конфигурации nginx..."
nginx -t

# Запуск nginx
echo "🚀 Запуск nginx..."
systemctl start nginx
systemctl enable nginx

# Настройка автоматического обновления
echo "🔄 Настройка автоматического обновления сертификата..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --reload-hook 'systemctl reload nginx'") | crontab -

# Проверка статуса сертификата
echo "✅ Проверка статуса сертификата..."
certbot certificates

echo "🎉 SSL сертификат успешно установлен!"
echo "📋 Информация о сертификате:"
echo "   - Домен: $DOMAIN"
echo "   - Сертификат: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "   - Приватный ключ: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "   - Автообновление: настроено (cron)"
echo ""
echo "🌐 Проверьте работу сайта: https://$DOMAIN"
echo "🔍 Проверить SSL можно на: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
