#!/bin/bash
# scripts/setup-filen-folders.sh
# Скрипт для создания структуры папок в Filen.io

set -e

echo "🚀 Настройка структуры папок в Filen.io для service.moscow"
echo "================================================"

# Проверяем наличие Filen CLI
if ! command -v filen &> /dev/null; then
    echo "❌ Filen CLI не установлен."
    echo "💡 Установите его: curl -fsSL https://cdn.filen.io/cli/linux_amd64.tar.gz | tar -xz && sudo mv filen /usr/local/bin/"
    exit 1
fi

# Проверяем аутентификацию
if ! filen ls / &> /dev/null; then
    echo "❌ Не авторизован в Filen."
    echo "💡 Авторизуйтесь: filen login или создайте файл .filen-cli-credentials"
    exit 1
fi

echo "✅ Filen CLI готов к работе"
echo ""

# Создаем основную структуру папок
echo "📁 Создание структуры папок..."

folders=(
    "/service-moscow"
    "/service-moscow/images"
    "/service-moscow/images/equipment"
    "/service-moscow/images/team"
    "/service-moscow/images/cases"
    "/service-moscow/images/logos"
    "/service-moscow/documents"
    "/service-moscow/documents/certificates"
    "/service-moscow/documents/licenses"
    "/service-moscow/videos"
    "/service-moscow/videos/repairs"
    "/service-moscow/videos/testimonials"
)

for folder in "${folders[@]}"; do
    if filen mkdir "$folder" 2>/dev/null; then
        echo "✅ Создана: $folder"
    else
        echo "ℹ️  Уже существует: $folder"
    fi
done

echo ""
echo "📝 Создание README файлов с инструкциями..."

# Создаем README файлы с инструкциями
cat > /tmp/equipment-readme.md << 'EOF'
# 🔧 Фото оборудования

В эту папку загружайте:
- Фото пароконвектоматов
- Фото посудомоечных машин  
- Фото холодильного оборудования
- Фото плит и грилей
- Фото водонагревателей
- Фото газовых котлов

**Рекомендации:**
- Размер: до 5 МБ на файл
- Формат: JPG, PNG
- Разрешение: 1280x960 или выше
- Имена файлов: оборудование-марка-модель.jpg

**Автоматическая обработка:**
- Изображения будут оптимизированы
- Создастся WebP версия
- Ресайз до 1280px по ширине
EOF

cat > /tmp/team-readme.md << 'EOF'
# 👥 Фото команды

В эту папку загружайте:
- Фото мастеров
- Групповые фото команды
- Фото рабочего процесса

**Рекомендации:**
- Размер: до 3 МБ на файл
- Формат: JPG, PNG
- Разрешение: 800x800 или выше (квадрат предпочтительно)
- Имена файлов: мастер-имя-фамилия.jpg

**Автоматическая обработка:**
- Ресайз до 800x800px
- Высокое качество WebP (90%)
EOF

cat > /tmp/cases-readme.md << 'EOF'
# 📋 Кейсы и примеры работ

В эту папку загружайте:
- Фото "до и после" ремонта
- Сложные случаи ремонта
- Успешные проекты

**Рекомендации:**
- Размер: до 8 МБ на файл
- Формат: JPG, PNG
- Разрешение: 1600x1200 или выше
- Имена файлов: кейс-описание-до.jpg, кейс-описание-после.jpg

**Автоматическая обработка:**
- Ресайз до 1600px по ширине
- WebP сжатие (80% качество)
EOF

# Загружаем README файлы
filen upload "/tmp/equipment-readme.md" "/service-moscow/images/equipment/README.md" 2>/dev/null || true
filen upload "/tmp/team-readme.md" "/service-moscow/images/team/README.md" 2>/dev/null || true  
filen upload "/tmp/cases-readme.md" "/service-moscow/images/cases/README.md" 2>/dev/null || true

echo "✅ README файлы созданы"
echo ""

# Показываем финальную структуру
echo "🎯 Финальная структура папок:"
echo "==============================="
filen ls -la /service-moscow/
echo ""

echo "🎉 Настройка завершена!"
echo ""
echo "📖 Следующие шаги:"
echo "1. Загрузите медиа-файлы в соответствующие папки"
echo "2. Настройте секреты GitHub: FILEN_EMAIL, FILEN_PASSWORD"
echo "3. GitHub Actions будет автоматически синхронизировать файлы каждые 30 минут"
echo ""
echo "🔗 Полезные команды:"
echo "   filen ls /service-moscow/           # Просмотр папок"
echo "   filen upload local.jpg /service-moscow/images/equipment/  # Загрузка файла"
echo "   filen download /service-moscow/images/ ./local/           # Скачивание папки"
echo ""
echo "✨ Готово к работе!"

# Cleanup
rm -f /tmp/*-readme.md