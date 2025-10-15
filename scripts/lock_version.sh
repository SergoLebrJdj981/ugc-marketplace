#!/bin/bash
VERSION=$1
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="notes/backups"

if [ -z "$VERSION" ]; then
    echo "❌ Укажите номер версии, например: ./scripts/lock_version.sh v1.4"
    exit 1
fi

echo "📦 Создание Context Lock $VERSION..."

mkdir -p "$BACKUP_DIR"

# создаём zip-архив со всеми md-файлами
ZIP_FILE="$BACKUP_DIR/contextlock_${VERSION}_${DATE}.zip"
if zip -r "$ZIP_FILE" notes/note/*.md > /dev/null; then
    echo "✅ Архив создан: $ZIP_FILE"
else
    echo "❌ Ошибка при создании архива."
    exit 1
fi

# удаляем старые одиночные копии (старый формат)
find "$BACKUP_DIR" -type f \( -name "*_2025-*.md" -o -name "*.md" \) -delete

# добавляем запись в changelog
echo "## [$VERSION] Context Lock — archived ($DATE)" >> notes/note/changelog.md
echo "**Описание:** Контекст проекта заархивирован в $ZIP_FILE" >> notes/note/changelog.md
echo "" >> notes/note/changelog.md

git add .
git commit -m "[version] Context Lock $VERSION — archived zip backup"
git push origin main

echo "🎯 Context Lock $VERSION успешно заархивирован и зафиксирован."
