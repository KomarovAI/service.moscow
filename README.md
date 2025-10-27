# 🚀 Автодеплой сайта artur789298.work.gd

Два Python-скрипта для полного развертывания и обновления вашего сайта на VPS с автоматическим SSL.

## 📋 Что включено

### 🛠️ deploy.py - Полное развертывание
- Автоустановка Docker и Docker Compose
- Настройка файервола (UFW)
- Клонирование репозитория сайта
- Создание оптимизированной конфигурации Nginx
- Автоматическое получение SSL сертификатов Let's Encrypt
- Настройка автообновления сертификатов
- Полная проверка работоспособности

### 🔄 update.py - Быстрое обновление
- Резервное копирование текущей версии
- Обновление исходного кода из Git
- Пересборка только измененных контейнеров
- Проверка работоспособности после обновления
- Очистка старых Docker образов

## 🚀 Быстрый старт

### 1. Первоначальное развертывание

```bash
# Скачиваем скрипт развертывания
wget https://raw.githubusercontent.com/KomarovAI/service.moscow/main/deploy.py

# Запускаем полное развертывание (требует sudo)
sudo python3 deploy.py
```

### 2. Обновление контента

```bash
# Стандартное обновление
sudo python3 /opt/service-moscow/update.py

# Быстрое обновление без проверок
sudo python3 /opt/service-moscow/update.py --quick

# Обновление с показом логов
sudo python3 /opt/service-moscow/update.py --show-logs
```

## 📁 Структура после установки

```
/opt/service-moscow/
├── deploy.py              # Скрипт первоначальной установки
├── update.py              # Скрипт обновления
├── docker-compose.yml     # Конфигурация контейнеров
├── Dockerfile            # Образ сайта
├── nginx/
│   └── conf.d/
│       └── site.conf     # Конфигурация виртуального хоста
├── scripts/
│   └── renew-cert.sh     # Автообновление SSL
├── backups/              # Резервные копии (создаются при обновлениях)
├── letsencrypt/          # SSL сертификаты Let's Encrypt
├── logs/                 # Логи Nginx
└── src/                  # Исходники сайта
```

## ⚙️ Параметры запуска

### deploy.py параметры:
```bash
--skip-ssl          # Пропустить настройку SSL (только HTTP)
--skip-firewall     # Не настраивать файервол
```

### update.py параметры:
```bash
--no-backup         # Не создавать резервную копию
--no-cleanup        # Не удалять старые Docker образы
--show-logs         # Показать логи после обновления
--quick             # Быстрое обновление без лишних проверок
```

## 🔧 Управление сайтом

```bash
# Статус всех сервисов
cd /opt/service-moscow && docker compose ps

# Просмотр логов
cd /opt/service-moscow && docker compose logs -f

# Перезапуск конкретного сервиса
cd /opt/service-moscow && docker compose restart nginx

# Полный перезапуск
cd /opt/service-moscow && docker compose down && docker compose up -d

# Проверка SSL сертификата
echo | openssl s_client -connect artur789298.work.gd:443 -servername artur789298.work.gd 2>/dev/null | openssl x509 -noout -dates
```

## 🛡️ Безопасность и производительность

### Что настраивается автоматически:
- ✅ Файервол UFW (только 22, 80, 443 порты)
- ✅ SSL/TLS сертификаты Let's Encrypt с автообновлением
- ✅ HTTP → HTTPS редиректы
- ✅ Security headers (HSTS, XSS Protection, Content-Type)
- ✅ Gzip сжатие для статических файлов
- ✅ Кэширование статики на 1 год
- ✅ HTTP/2 поддержка

### Оптимизация производительности:
- ✅ Nginx Alpine (легкий образ)
- ✅ Gzip сжатие всех текстовых файлов
- ✅ Кэш браузера для статических файлов
- ✅ Минимальное потребление памяти
- ✅ Автоочистка старых Docker образов

## 🆘 Устранение проблем

### Проблемы с SSL:
```bash
# Проверить статус сертификата
docker run --rm -v /opt/service-moscow/letsencrypt:/etc/letsencrypt certbot/certbot certificates

# Принудительно обновить сертификат
/opt/service-moscow/scripts/renew-cert.sh

# Проверить конфигурацию Nginx
cd /opt/service-moscow && docker exec service-moscow-nginx nginx -t
```

### Проблемы с доступностью:
```bash
# Проверить DNS
dig artur789298.work.gd

# Проверить статус контейнеров
cd /opt/service-moscow && docker compose ps

# Проверить логи Nginx
cd /opt/service-moscow && docker compose logs nginx
```

## 📊 Мониторинг

Встроенные health-check'и проверяют:
- Доступность веб-контейнера каждые 30 секунд
- Автоматический перезапуск при сбое
- Логирование всех запросов и ошибок

## 🎯 Результат

После запуска `deploy.py` ваш сайт будет:
- 🌐 Доступен по адресу: https://artur789298.work.gd
- 🔒 Защищен SSL сертификатом с автообновлением
- ⚡ Оптимизирован для максимальной скорости загрузки
- 🛡️ Защищен файерволом и security headers
- 🔄 Готов к быстрым обновлениям через `update.py`

## 💻 Техническое описание сайта

### Особенности
- **100% статический** - HTML, CSS, JavaScript без зависимостей
- **Docker-контейнеризация** - легкое развертывание на любом сервере
- **Nginx Alpine** - оптимизированная конфигурация для максимальной скорости

### Производительность
- **Core Web Vitals оптимизация** - LCP < 1с, INP < 50мс, CLS = 0
- **Gzip сжатие** - уменьшение размера на 70-80%
- **Кэширование статики** - браузерное кэширование на 1 год
- **Critical CSS** - инлайн критические стили

### SEO-оптимизация
- **Семантическая HTML5-разметка** - полная семантика
- **Schema.org JSON-LD** - структурированные данные для LocalBusiness
- **Open Graph и Twitter Cards** - оптимизация для соцсетей
- **Оптимизированные meta-теги** - титлы, описания, ключевые слова

### Адаптивность
- **Mobile-First дизайн** - приоритет мобильным устройствам
- **Responsive Grid** - CSS Grid и Flexbox
- **Оптимизация touch-взаимодействия** - 44px минимум для кнопок

## 📧 Контакты

- **Автор:** KomarovAI
- **Email:** artur.komarovv@gmail.com
- **GitHub:** https://github.com/KomarovAI/service.moscow
- **Сайт:** https://artur789298.work.gd

---
**ВСЁ ЗЕБА! 🚀** Сайт готов к продуктивной эксплуатации.