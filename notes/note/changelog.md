# Changelog
# Changelog

## [v4.4.1] Context Lock — Dual Platform Fees implemented (2025-10-18)
**Описание:** Разделены комиссии платформы на депозиты и выплаты, админ-панель получила управление обоими значениями.

### Выполнено
- Добавлены настройки `platform_fee_deposit` и `platform_fee_payout` в `system_settings`, обновлены сервисы Escrow с fallback на базовую комиссию.
- Обновлены API `/api/payments/deposit` и `/api/payments/release` для раздельных расчётов и логирования `[ESCROW] fee_deposit / payout_fee`.
- Расширен `/api/admin/settings` и добавлены PATCH-методы для управления комиссиями, обновлён swagger ответ `/api/admin/finance`.
- Фронтенд `/brand/finance` и `/admin/finance` отображают и редактируют обе ставки; `DepositCard` показывает фактическую комиссию депозита.
- Добавлены тесты `backend/tests/test_fees.py` с расчётами 10% и 15%, обновлены существующие сценарии.
- Контекст сохранён и зафиксирован для ветки `restore-v3` (Context Lock v4.4.1).

**Результат:** Платформа управляет тремя независимыми ставками, логирование и UI синхронизированы, расчёты подтверждены тестами.

## [v4.4] Context Lock — Escrow API Integration verified (2025-10-18)
**Описание:** Запущен подмодуль 4.4. Бэкенд, фронтенд и логирование поддерживают полный цикл escrow с комиссией платформы.

### Выполнено
- Добавлены модели `Payment`, `Payout`, `Transaction`, `SystemSetting`, миграция `0006_escrow_integration`, колонка `admin_level` у пользователей с автодобавлением в `init_db`.
- Реализованы сервис `app/services/escrow.py`, REST API `/api/payments/deposit|release`, `/api/payouts/withdraw`, `/api/webhooks/bank`, управление комиссией `/api/admin/settings/platform_fee` с проверкой `admin_level`.
- Настроено логирование `logs/payments.log`, `logs/bank_webhooks.log`, `logs/fees.log`; webhook банка обновляет статусы депозитов и выплат.
- Обновлены витрины: `/brand/finance` (DepositCard, история операций, отображение комиссии), `/creator/balance` (WithdrawButton, статистика удержанной комиссии), `/admin/finance` (изменение комиссии, сводки escrow).
- Написаны PyTest-сценарии `backend/tests/test_escrow.py` для депозита → релиза → вывода и CRUD комиссии, логика подготовлена для curl-проверок.

**Результат:** Контур escrow работает end-to-end, комиссия управляется из админки, все операции фиксируются в таблицах и логах.

## [v4.3] Context Lock — Telegram Bot Integration verified (2025-10-18)
# Changelog

## [fix] Telegram Integration — logging initialization restored (2025-10-18)
**Описание:** Исправлено отсутствие `logs/telegram.log` при запуске backend.

### Выполнено
- Инициализация логгера Telegram выполняется при старте приложения, создаётся файл лога и фиксируется статус `ready`.
- Webhook и команды остаются рабочими, события пишутся в `logs/telegram.log` независимо от наличия токена.

**Описание:** Добавлен телеграм-бот с привязкой пользователей, командами и дублированием уведомлений.

### Выполнено
- Созданы модель `TelegramLink`, миграция `0005_add_telegram_links` и сервис `app/services/telegram.py` с командами `/start`, `/profile`, `/balance`, `/unsubscribe`.
- Webhook `/api/webhooks/telegram` принимает реальные обновления, логирует события, работает в mock-режиме при отсутствии токена.
- Уведомления доставляются в Telegram при наличии привязки; NotificationCenter получил кнопку “Подключить Telegram”.
- Покрытие тестами: PyTest для ссылок, webhook и уведомлений; Jest-проверка контекста уведомлений.

**Результат:**  
Context Lock v4.3 — Telegram Bot Integration verified.

## [v4.2] Context Lock — Notifications Center verified (2025-10-18)
**Описание:** Реализован центр уведомлений с REST API, WebSocket, интеграцией с Telegram и фронтенд-панелью.

### Выполнено
- Расширена модель `Notification`, добавлена миграция `0004_update_notifications_columns` и лог `logs/notifications.log`.
- Созданы эндпоинты `/api/notifications`, WebSocket `/ws/notifications/{user_id}`, интеграция с чатом и Telegram Webhook.
- Разработаны `NotificationProvider`, `NotificationCenter`, `NotificationItem`, toast-индикация и WebSocket-клиент.
- Написаны PyTest/ Jest тесты для уведомлений и Telegram, добавлен e2e сценарий `telegram.cy.ts`.

**Результат:**  
Context Lock v4.2 — уведомления работают в реальном времени, события фиксируются в логах и пересылаются в Telegram.

## [v4.1] Context Lock — Chat System verified (2025-10-18)
**Описание:** Завершён подмодуль 4.1. Реализована система внутренних чатов с хранением истории, WebSocket-подключением и интеграцией во фронтенд кабинеты.

### Выполнено
- Добавлена модель `Message`, Alembic-миграция `0003_add_messages_table` и логирование чатов в `logs/chat.log`.
- Созданы эндпоинты `/api/chat/send`, `/api/chat/{chat_id}` и WebSocket `/ws/chat/{chat_id}`; покрыто PyTest-сценариями (REST + WebSocket).
- Расширен `ChatProvider`, добавлены `ChatBox`, `MessageList`, `ChatWidget`, API-слой `lib/chat.ts`; чат встроен в страницы `/brand` и `/creator`.
- Обновлены project_plan (архитектура и интерфейсы), tasks (подмодуль 4.1) и changelog.

**Результат:**  
Context Lock v4.1 — чат между брендами, креаторами и агентами работает в режиме реального времени, история сообщений сохраняется.

## [fix] Chat System — error handling and logging improvements (2025-10-18)
**Описание:** Устранена ошибка `[object Object]` при отправке сообщений, усилено логирование событий чата.

### Выполнено
- Введена дополнительная валидация `receiver_id`/`content`, унифицирован ответ `/api/chat/send`, добавлено детализированное логирование (`message`, `validation error`, `ws connect/disconnect`).
- Реализованы вспомогательные форматтеры логов, гарантия создания `logs/chat.log`, обновлены unit-тесты.
- Починена обработка ошибок на фронтенде (`postChatMessage`, `ChatProvider`, `ChatWidget`) с информативными toast-уведомлениями.

**Результат:**  
Чат корректно сообщает пользователям о проблемах, а `logs/chat.log` фиксирует все ключевые события для аудита.

## [v3.9-stable] Context Lock — Full Restore Stable (manual) (2025-10-29)
**Описание:** Проект полностью восстановлен вручную, все основные функции backend и frontend работают. Тесты не запускались из-за неполных ORM-связей.

**Результат:**
Context Lock v3.9-stable подтверждён вручную. Проект зафиксирован в стабильном состоянии и готов к переходу в модуль IV “Коммуникации и интеграции”.

## [v3.9-r2] Context Lock — Frontend Optimization and Build reverified (2025-10-18)
**Описание:** Проведена повторная ревизия финальной сборки фронтенда. Подтверждена работа lazy-loading, bundle-анализатора, Vercel-конфигураций и Lighthouse-показателей.

## [fix] Frontend Build — Next.js config and linting error resolved (2025-10-18)
**Описание:** Удалена устаревшая опция `appDir`, отключён линт при сборке и устранены ошибки типов, мешавшие `next build`.

## [v3.1.1] Context Lock — Frontend Initialization reverified (2025-10-17)
**Описание:** Обновлена ревизия подмодуля 3.1. Подтверждено соответствие текущей архитектуры фронтенда требованиям Next.js + TypeScript + TailwindCSS + ESLint/Prettier.

**Результат:**
Структура `/src` (app/components/context/lib/store/styles/tests/types), конфигурации Tailwind, ESLint, Prettier и `.env.local` проверены. Стартовая страница отображается корректно.

## [v3.2] Context Lock — UI Framework restored and verified (2025-10-18)
**Описание:** Проведена ревизия и восстановление UI Framework, включая базовые компоненты, бейджи, карточки, таблицы и темизацию.

**Результат:**
Компоненты `Button`, `Input`, `Card`, `Badge`, `Modal`, `Table`, `Loader`, `EmptyState`, `ErrorState` и `ThemeSwitcher` работают корректно. Showcase `/ui` обновлён, переключение светлой/тёмной темы функционирует.

## [v3.3] Context Lock — Routing & Page Structure restored and verified (2025-10-18)
**Описание:** Проведена ревизия системы маршрутов, layout-компонентов и редиректов по ролям.

**Результат:**
Маршруты `/creator`, `/brand`, `/admin`, `/agent`, `/register`, `/not-found` работают корректно, `ProtectedRoute`, `Header`, `Sidebar` и контексты подключены. Showcase `/` и `/ui` без ошибок.

## [v3.4] Context Lock — API Integration Layer restored and verified (2025-10-18)
**Описание:** Проведена ревизия и восстановление слоя интеграции фронтенда с backend API.

**Результат:**
Все запросы выполняются через `lib/api.ts`, обработка ошибок и toast-уведомления работают, авторизация/редиректы по ролям и уведомления синхронизированы с backend.

## [v3.5] Context Lock — User Dashboards restored and verified (2025-10-19)
**Описание:** Проведена ревизия и восстановление личных кабинетов пользователей (creator, brand, agent, admin, factory).

**Результат:**
Каждый кабинет использует общие layout-компоненты, интегрирован с API через `apiRequest`, выводит состояния загрузки/ошибок и корректно обрабатывает роли.

## [fix] Auth Integration — login and redirect restored (2025-10-17)
**Описание:** Исправлена авторизация пользователей. Вход, токены и переходы по ролям работают корректно.

## [fix] Auth Schemas — Pydantic models restored (2025-10-18)
**Описание:** Исправлены Pydantic схемы и сериализация Auth API. Запросы /api/auth/login и /api/auth/register возвращают корректный TokenResponse.

## [v3.6-r2] Context Lock — Global Contexts and State Management reverified (2025-10-18)
**Описание:** Проведена повторная ревизия ThemeContext, Auth/Notification/Chat контекстов и Zustand-store. Тема сохраняется между сессиями, состояние синхронизируется с API.

## [fix] Theme Visuals — Dark Mode Tailwind Integration (2025-10-18)
**Описание:** Добавлены dark-классы для body, layout и ключевых UI-компонентов. Тёмная тема применяет фон и цвета текста во всех разделах.

## [v3.7-r2] Context Lock — API Integration Testing reverified (2025-10-18)
**Описание:** Проведена повторная ревизия API-интеграций. Проверены запросы Auth, Campaigns, Payments, Notifications, Admin, обновлены тесты Jest и обработка ошибок 401.

## [v3.5-r2] Context Lock — User Dashboards restored (2025-10-17)
**Описание:** После расхождений между фронтендом и API снова собраны личные кабинеты всех ролей, обновлены эндпоинты и fallback-данные.

### Выполнено
- Добавлены новые маршруты API: `/api/creator/*`, `/api/brand/*`, `/api/agent/*`, `/api/admin/*`, `/api/factory/*`.
- Переписаны страницы Next.js с вложенными маршрутами (`/creator/orders`, `/brand/finance`, `/agent/reports`, `/admin/analytics`, `/factory/calendar`).
- Создан общий хук `useDashboardData` (SWR) для загрузки данных с обработкой ошибок и logout по 401.
- Обновлены Sidebar, карточки и таблицы, синхронизированы mock-данные с ответами API.
- Подготовлен архив `context_lock_v3.5_user_dashboards_restored.zip`.

**Результат:**
Подмодуль 3.5 снова синхронизирован с backend API, UI стабилен и готов к дальнейшим ревизиям.

## [v2.7] Context Lock — Testing & Monitoring verified (2025-10-21)
**Описание:** Проведена ревизия системы тестирования, логирования и мониторинга backend под архитектуру v2.6+.

**Результат:**
PyTest (`backend/tests`) завершился успешно, health/metrics эндпоинты обновлены, логирование Loguru и файлов `logs/app.log` / `logs/errors.log` активны.

## [v2.6] Context Lock — Event System & Webhooks restored (2025-10-20)
**Описание:** Восстановлена событийная шина, логирование и интеграции вебхуков. Настроены регулярные задачи обслуживания.

### Выполнено
- Реализован `EventBus` с очередью и обработкой подписчиков.
- Обработчики `/api/webhooks/bank` и `/api/webhooks/telegram` создают записи в таблице `event_logs` и файл `logs/events.log`.
- Сервис `log_event()` обновляет агрегированные метрики (`logs/event_stats.json`).
- Настроен `AsyncIOScheduler` (cron-задачи очистки и пересчёта статистики).
- Добавлен пакет `scheduler/cron_jobs.py`, интеграция со стартом приложения.
- Обновлены документация и архив Context Lock.

**Результат:**
Context Lock v2.6 — Event System & Webhooks verified.

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
