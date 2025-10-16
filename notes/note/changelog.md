# Changelog

## [v2.4] Context Lock — Security & Middleware implemented (2025-10-18)
**Описание:** Добавлены JWT-аутентификация, CORS, rate limiter, валидация данных и централизованное логирование.

### Выполнено
- Реализованы access/refresh токены, refresh-ротация, logout с blacklist.
- Подключены middleware: CORS, rate limiter (60 req/min), request logger Loguru.
- Настроена унифицированная обработка ошибок и обновлены схемы аутентификации.
- Протестированы сценарии login/refresh/logout, rate limit и CORS.
- Обновлены project_plan.md, readme.md, changelog и tasks.

**Результат:**
Context Lock v2.4 — Security & Middleware активированы.

## [fix] Database connection verified (2025-10-18)
**Описание:** Исправлено подключение SQLite, добавлено авто-создание базы при отсутствии.

**Результат:**
Context Lock v2.4 database connection verified.

## [v2.5] Context Lock — Admin API Layer implemented (2025-10-19)
**Описание:** Реализован административный уровень API с ролевой системой и отчётами.

### Выполнено
- Добавлены маршруты `/api/admin/users`, `/api/admin/campaigns`, `/api/admin/statistics` и экспорт CSV.
- Внедрена система ролей `admin_level_1–3`, middleware логирования и таблица `admin_logs`.
- Настроены отчёты и сервис `reports` для метрик.
- Написаны тесты доступа, отчётов и ограничений.

**Результат:**
Context Lock v2.5 — Admin API готов к интеграции с фронтендом.

## [v2.3] Notifications & Webhooks implemented (2025-10-18)
**Описание:** Реализована система уведомлений и webhook-интеграций.

### Выполнено
- Добавлены модели Notification и WebhookEvent.
- Настроены маршруты `/api/notifications`, `/api/notifications/mark-read`, `/api/webhooks/payment`, `/api/webhooks/order`.
- События обрабатываются через фоновые задачи (BackgroundTasks), ведётся аудит webhook-запросов.
- Обновлены project_plan.md, readme.md, changelog и tasks.

**Результат:**  
Context Lock v2.3 — Notifications & Webhooks функционируют корректно.

## [fix] Database migration reset (2025-10-18)
**Описание:** Alembic полностью пересоздан, база данных восстановлена.

### Выполнено
- Удалены устаревшие миграции, сгенерирована новая ревизия `reset database`.
- Созданы таблицы: users, campaigns, applications, orders, payments, notifications, webhook_events, reports, ratings, videos.
- Миграции применены к SQLite (`backend/app.db`), структура проверена через SQLAlchemy inspector.
- API протестирован: получение уведомлений на пустой базе, создание кампании, автоматическое уведомление бренда.

**Результат:**  
Context Lock v2.3 database reset successful.

## [v2.2] REST API implemented (2025-10-18)
**Описание:** Реализованы маршруты Auth, Campaigns, Applications, Orders, Payments, Notifications.

### Выполнено
- Добавлен REST API на FastAPI с централизованным error handler и Swagger (/docs).
- Реализованы маршруты: регистрация/логин, управление кампаниями, отклики, заказы, платежи, уведомления.
- Написаны unit-тесты для Auth, Campaigns и Payments.
- Обновлены project_plan.md (REST API Specification), readme.md (API Usage Guide), changelog и tasks.

**Результат:**  
Context Lock v2.2 — REST API готов к интеграции с frontend.

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
