#!/bin/bash
set -e

echo "🔍 Проверка целостности notes..."

REQUIRED_FILES=("project_plan.md" "tasks.md" "changelog.md" "readme.md")
NOTES_DIR="notes/note"

for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -s "$NOTES_DIR/$file" ]; then
    echo "❌ Ошибка: отсутствует или пустой файл $file"
    exit 1
  else
    echo "✅ $file — проверен и доступен"
  fi
done

echo ""
echo "📅 Проверка синхронизации дат..."
ls -lt "$NOTES_DIR"/*.md | head -n 5

echo ""
echo "✅ Проверка notes завершена успешно!"
