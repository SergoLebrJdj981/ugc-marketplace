#!/bin/bash
VERSION=$1
DATE=$(date +%Y-%m-%d)
BACKUP_DIR="notes/backups"

if [ -z "$VERSION" ]; then
    echo "❌ Укажите номер версии, например: ./scripts/lock_version.sh v1.3"
    exit 1
fi

echo "📦 Создание Context Lock $VERSION..."

mkdir -p "$BACKUP_DIR"
cp notes/note/*.md "$BACKUP_DIR"/
echo "✅ Резервные копии notes созданы."

echo "## [$VERSION] Context Lock — $(date +%Y-%m-%d)" >> notes/note/changelog.md
echo "**Описание:** Автоматическая фиксация состояния проекта." >> notes/note/changelog.md
echo "" >> notes/note/changelog.md

git add .
git commit -m "[version] Context Lock $VERSION — Auto backup and verification"
git push origin main

echo "🎯 Context Lock $VERSION успешно создан и зафиксирован."
