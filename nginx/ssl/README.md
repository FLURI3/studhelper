# SSL сертификаты для Nginx
# Разместите здесь ваши SSL сертификаты

# Файлы:
# - fullchain.pem (публичный сертификат + промежуточные сертификаты)
# - privkey.pem (приватный ключ)

# Для Let's Encrypt:
# Скопируйте из /etc/letsencrypt/live/your-domain.com/

# Для самоподписанного сертификата (только для тестов):
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
#   -keyout privkey.pem -out fullchain.pem \
#   -subj "/CN=your-domain.com"
