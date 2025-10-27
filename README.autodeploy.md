# Автодеплой с разделением сайта и инфраструктуры

Данная инструкция описывает настройку раздельного деплоя сайта и инфраструктуры с использованием Docker, GitHub Actions и отдельных репозиториев.

## 1. Структура репозитория сайта

### Содержимое репозитория сайта (service.moscow)

Репозиторий сайта должен содержать:

```
service.moscow/
├── src/                    # Исходный код приложения
├── public/                 # Статические файлы
├── package.json           # Зависимости Node.js
├── Dockerfile             # Образ для production
├── Dockerfile.dev         # Образ для разработки
├── .dockerignore          # Исключения для Docker
├── .github/
│   └── workflows/
│       └── deploy.yml     # Автодеплой сайта
└── README.md              # Документация
```

### Пример Dockerfile для сайта

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package*.json ./
RUN npm ci --only=production

# Копируем исходный код
COPY . .

# Собираем приложение
RUN npm run build

# Открываем порт
EXPOSE 3000

# Запускаем приложение
CMD ["npm", "start"]
```

## 2. Структура репозитория VPS/инфраструктуры

### Содержимое репозитория VPS

Отдельный репозиторий для инфраструктуры должен содержать:

```
vps-infrastructure/
├── docker-compose.yml     # Основная конфигурация сервисов
├── nginx/
│   ├── nginx.conf        # Конфигурация Nginx
│   └── ssl/              # SSL сертификаты
├── postgres/
│   └── init.sql          # Инициализация БД
├── redis/
│   └── redis.conf        # Конфигурация Redis
├── .env.example          # Пример переменных окружения
├── scripts/
│   ├── deploy.sh         # Скрипт деплоя
│   └── backup.sh         # Скрипт бэкапов
└── README.md             # Документация по инфраструктуре
```

## 3. Цепочка автодеплоя

### GitHub Actions для сайта (build + push)

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy Site

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

    - name: Deploy to VPS
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USER }}
        key: ${{ secrets.VPS_SSH_KEY }}
        script: |
          cd /opt/vps-infrastructure
          git pull origin main
          ./scripts/deploy.sh ${{ steps.meta.outputs.tags }}
```

### Скрипт деплоя на VPS

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Получаем тег образа из аргумента
IMAGE_TAG=${1:-"latest"}

echo "Деплой с образом: $IMAGE_TAG"

# Обновляем переменную окружения с тегом образа
echo "APP_IMAGE_TAG=$IMAGE_TAG" > .env.deploy

# Авторизуемся в GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Останавливаем и удаляем старые контейнеры
docker-compose down

# Загружаем новый образ
docker-compose pull app

# Запускаем обновленные сервисы
docker-compose up -d

# Проверяем статус
docker-compose ps

# Очищаем старые образы
docker image prune -f

echo "Деплой завершен успешно!"
```

### Переменные окружения для VPS

```bash
# .env (создать на основе .env.example)

# GitHub Container Registry
GITHUB_USERNAME=your-github-username
GITHUB_TOKEN=your-personal-access-token

# Приложение
APP_IMAGE_TAG=latest
NODE_ENV=production
PORT=3000

# База данных
POSTGRES_DB=servicedb
POSTGRES_USER=serviceuser
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://serviceuser:your-secure-password@postgres:5432/servicedb

# Redis
REDIS_URL=redis://redis:6379

# Nginx
DOMAIN=service.moscow
SSL_EMAIL=admin@service.moscow
```

## 4. Docker Compose для VPS

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: ghcr.io/komarovai/service.moscow:${APP_IMAGE_TAG:-latest}
    container_name: service_moscow_app
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - PORT=3000
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: service_moscow_postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: service_moscow_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-}
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: service_moscow_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - certbot_data:/var/www/certbot
    depends_on:
      - app
    networks:
      - app-network

  certbot:
    image: certbot/certbot
    container_name: service_moscow_certbot
    volumes:
      - certbot_data:/var/www/certbot
      - ./nginx/ssl:/etc/letsencrypt
    command: certonly --webroot --webroot-path=/var/www/certbot --email ${SSL_EMAIL} --agree-tos --no-eff-email -d ${DOMAIN} -d www.${DOMAIN}
    profiles:
      - ssl-setup

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  certbot_data:
    driver: local

networks:
  app-network:
    driver: bridge
```

## 5. Команды для управления

### Инициальная настройка VPS

```bash
# Клонируем репозиторий инфраструктуры
git clone https://github.com/your-org/vps-infrastructure.git /opt/vps-infrastructure
cd /opt/vps-infrastructure

# Копируем и настраиваем переменные окружения
cp .env.example .env
vim .env  # Редактируем переменные

# Делаем скрипты исполняемыми
chmod +x scripts/*.sh

# Настраиваем SSL сертификаты (опционально)
docker-compose --profile ssl-setup up certbot
```

### Команды для деплоя

```bash
# Ручной деплой конкретной версии
./scripts/deploy.sh ghcr.io/komarovai/service.moscow:v1.2.3

# Деплой latest версии
./scripts/deploy.sh

# Просмотр логов
docker-compose logs -f app

# Перезапуск сервиса
docker-compose restart app

# Полная перезагрузка всех сервисов
docker-compose down && docker-compose up -d
```

### Команды для мониторинга

```bash
# Статус всех контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Проверка health check'ов
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Резервное копирование БД
./scripts/backup.sh
```

## Секреты GitHub Actions

Настройте следующие секреты в репозитории сайта:

```yaml
VPS_HOST: "your-vps-ip-or-domain"
VPS_USER: "deploy-user"
VPS_SSH_KEY: "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
```

## Дополнительные скрипты

### Скрипт резервного копирования

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/postgres_$DATE.sql

# Backup Redis
docker-compose exec -T redis redis-cli BGSAVE
docker cp service_moscow_redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

echo "Backup completed: $BACKUP_DIR"
```

---

**Примечания:**
- Замените `your-org`, `your-github-username`, и другие заглушки на реальные значения
- Убедитесь, что настроены SSH ключи и доступы к VPS
- Регулярно обновляйте и тестируйте процедуры резервного копирования
- Используйте мониторинг для отслеживания состояния сервисов
