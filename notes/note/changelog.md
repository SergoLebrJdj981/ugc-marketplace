# Changelog

## [v2.1] Database & ORM (2025-10-17)
**Описание:** Реализована архитектура базы данных и ORM-моделей.

### Выполнено
- Созданы модели: User, Campaign, Application, Order, Video, Payment, Rating, Report.
- Настроены миграции и проверено создание таблиц (Alembic + PostgreSQL).
- Добавлен дамп схемы в `backend/app/schema_dump.sql`.
- Обновлены project_plan.md, changelog и tasks.

**Результат:**  
Context Lock v2.1 — база данных успешно создана и готова к интеграции с API.

## [v1.7] Context Lock — System Documentation and Revisions (2025-10-17)
**Описание:** Настроена система автоматической ревизии notes, создан шаблон протокола и скрипты проверки целостности.

### Выполнено
- Добавлены скрипты `revision_check.sh` и `sync_notes.py`.
- Создан шаблон `revision_protocol.md`.
- Настроена автоматическая сверка consistency файлов notes.
- Обновлены changelog и tasks.

**Результат:**  
Context Lock v1.7 установлен. Система ревизий готова к работе.

## [v1.6] Git Workflow and Dev Environment setup (2025-10-17)
**Описание:** Настроена система ветвления и commit-конвенций, интегрирована среда Git с VS Code и Codex.
- Добавлены ветки main / dev / feature.
- Настроены husky и lint-staged.
- Обновлён readme.md с разделом Git Workflow.
- Обновлены changelog и tasks.

**Результат:**  
Context Lock v1.6 установлен. Система Git полностью интегрирована и стандартизирована.

## [v1.5] Project Structure Control implemented (2025-10-16)
**Описание:** Настроен скрипт проверки и восстановления структуры директорий.
- Добавлен скрипт check_structure.sh.
- Интегрирован с pre-commit hook.
- Сгенерировано дерево каталогов.
- Обновлён project_plan.md.

**Результат:**  
Структура проекта зафиксирована и контролируется автоматически.

## [v1.4] Context Lock — Zip archive optimization (2025-10-16)
**Описание:** Механизм Context Lock оптимизирован. Теперь каждая версия хранится в одном архиве (.zip).

### Выполнено
- Обновлён скрипт lock_version.sh.
- Удалён механизм множественного копирования файлов.
- Создание zip-архива для каждой версии.
- Changelog автоматически фиксирует заархивированные версии.

**Результат:**  
Context Lock стал компактнее и безопаснее. Архивы версий хранятся в /notes/backups/.

## [v1.4-testzip] Context Lock — archived (2025-10-16)
**Описание:** Контекст проекта заархивирован в notes/backups/contextlock_v1.4-testzip_2025-10-16.zip.

## [v1.3] Context Lock — Core system implemented (2025-10-16)
**Описание:** Внедрён механизм фиксации и проверки контекста проекта.
- Добавлен шаблон commit-сообщений.
- Настроен pre-commit hook для валидации notes.
- Реализован скрипт lock_version.sh для создания версий Context Lock.
- Проверена работоспособность freeze/unfreeze.

## [v1.3-test2] Context Lock — 2025-10-16
**Описание:** Автоматическая фиксация состояния проекта.

## 2025-10-16
### [update] Notes System setup complete
- Настроена система документации проекта.
- Проверены файлы: project_plan.md, tasks.md, changelog.md, readme.md.
- Добавлены автосохранение и резервное копирование.
- Notes готовы к ревизии GPT.

## 2025-10-15
### [init] Project structure created
- initialized frontend and backend environments
- created .env.example, .gitignore, LICENSE
- verified directory structure
