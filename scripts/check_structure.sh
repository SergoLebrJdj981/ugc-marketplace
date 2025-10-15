#!/bin/bash
echo "🔍 Проверка структуры проекта UGC Marketplace..."

REQUIRED_DIRS=("frontend" "backend" "notes" "assets" "scripts")

for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "⚠️  Каталог '$dir' отсутствует — создаю..."
    mkdir -p "$dir"
  else
    echo "✅ Каталог '$dir' найден."
  fi
done

echo "📁 Проверка завершена. Все каталоги на месте."
