# 📁 Filen.io Интеграция для service.moscow

Автоматическая синхронизация медиа-файлов из Filen.io в GitHub репозиторий.

## 🎯 Основные возможности

- ✅ **Автосинхронизация** каждые 30 минут
- ✅ **Оптимизация изображений** (WebP, ресайз)
- ✅ **Ручной запуск** через GitHub Actions
- ✅ **Уведомления** в Telegram (опционально)
- ✅ **Манифест файлов** для сайта

## 🚀 Быстрая настройка

### 1. Настройка Filen аккаунта

1. **Регистрация**: [filen.io](https://filen.io) → используй реферальную ссылку для 20GB
2. **Подтверждение email**: получи +10GB бонус
3. **Опционально**: промокоды для дополнительного места

### 2. Настройка GitHub Secrets

Перейди: **Repository** → **Settings** → **Secrets and variables** → **Actions**

Добавь секреты:

| Название | Описание | Обязательно |
|----------|-------------|----------|
| `FILEN_EMAIL` | Твой email в Filen.io | ✅ |
| `FILEN_PASSWORD` | Пароль от Filen.io | ✅ |
| `FILEN_2FA_CODE` | Код 2FA (если включен) | ❌ |
| `TG_BOT_TOKEN` | Telegram бот для уведомлений | ❌ |
| `TG_CHAT_ID` | Telegram chat ID | ❌ |

### 3. Создание структуры папок в Filen

Используй готовый скрипт:

```bash
# Установи Filen CLI
curl -fsSL https://cdn.filen.io/cli/linux_amd64.tar.gz | tar -xz
sudo mv filen /usr/local/bin/

# Авторизация
filen login

# Создание структуры
bash scripts/setup-filen-folders.sh
```

Или создай папки вручную через веб-интерфейс:

```
/service-moscow/
├── images/
│   ├── equipment/     # Фото оборудования
│   ├── team/          # Фото команды
│   ├── cases/         # Кейсы до/после
│   └── logos/         # Логотипы и иконки
├── documents/         # Документы
└── videos/            # Видео
```

## 📝 Использование

### Автоматическая синхронизация

- **По расписанию**: каждые 30 минут (00:00, 00:30, 01:00...)
- **При push** в репозиторий (опционально)
- **Webhook** с Filen (будущая функция)

### Ручной запуск

1. Перейди: **Actions** → **📁 Filen Media Sync**
2. Нажми: **Run workflow**
3. Выбери ветку: `main`
4. Нажми: **Run workflow**

### Загрузка файлов

**Через веб-интерфейс Filen:**
1. Открой: [app.filen.io](https://app.filen.io)
2. Перейди в нужную папку
3. Перетащи файлы или нажми "Загрузить"

**Через Filen CLI:**
```bash
# Один файл
filen upload photo.jpg /service-moscow/images/equipment/

# Целая папка
filen upload ./local-photos/ /service-moscow/images/equipment/ --recursive
```

## 🔧 Оптимизация изображений

Изображения автоматически оптимизируются:

| Категория | Макс. размер | WebP качество | Назначение |
|-----------|-------------|--------------|------------|
| Equipment | 1280px | 85% | Каталог оборудования |
| Team | 800px | 90% | Фото сотрудников |
| Cases | 1600px | 80% | Портфолио работ |
| Logos | 512px | 95% | Логотипы и иконки |

## 📄 Файлы в репозитории

После синхронизации файлы появляются в:

```
src/assets/
├── img/
│   ├── equipment/          # Из /service-moscow/images/equipment
│   ├── team/               # Из /service-moscow/images/team
│   ├── cases/              # Из /service-moscow/images/cases
│   └── logos/              # Из /service-moscow/images/logos
├── docs/                   # Из /service-moscow/documents
├── videos/                 # Из /service-moscow/videos
├── thumbs/                 # Миниатюры (будущая функция)
└── media-manifest.json    # Манифест файлов
```

### Манифест файлов

`src/assets/media-manifest.json` содержит:
```json
{
  "generated_at": "2025-10-29T12:35:00Z",
  "sync_source": "filen",
  "folders": {
    "equipment": ["parokonvektomat-rational.jpg", "parokonvektomat-rational.webp"],
    "team": ["master-ivan-petrov.jpg", "master-ivan-petrov.webp"],
    "cases": ["restoran-abc-do.jpg", "restoran-abc-posle.jpg"],
    "logos": ["logo-service-moscow.png", "logo-service-moscow.webp"]
  }
}
```

## 📊 Мониторинг

### GitHub Actions

Просмотр логов:
1. **Actions** → **📁 Filen Media Sync**
2. Кликни по последнему запуску
3. Открой **sync-media** job

### Telegram уведомления

Если настроены `TG_BOT_TOKEN` и `TG_CHAT_ID`:
- ✅ Успешная синхронизация
- ❌ Ошибки синхронизации

## 🔍 Устранение неполадок

### Ошибки авторизации

```
❌ Login failed: Invalid credentials
```

Проверь:
- `FILEN_EMAIL` - правильность email
- `FILEN_PASSWORD` - правильность пароля
- `FILEN_2FA_CODE` - актуальность 2FA кода

### Папки не найдены

```
⚠️ Equipment folder not found
```

Создай папки в Filen:
```bash
filen mkdir /service-moscow/images/equipment
# или через веб-интерфейс
```

### Проблемы с оптимизацией

```
❌ Failed to convert to WebP
```

Обычно решается повторным запуском.

## 🔗 Полезные ссылки

- [Filen.io официальный сайт](https://filen.io)
- [Filen CLI документация](https://docs.filen.io/docs/cli/)
- [GitHub Actions документация](https://docs.github.com/en/actions)
- [WebP оптимизация](https://developers.google.com/speed/webp)

---

## 🎆 Готово!

Теперь твой сайт service.moscow имеет:
- ✅ Автоматическую синхронизацию медиа-файлов
- ✅ Оптимизацию изображений для быстрой загрузки
- ✅ Полную связку с системой деплоя

**Загружай файлы в Filen → они автоматически появятся на сайте!** 🚀
