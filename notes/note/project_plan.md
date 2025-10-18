# I. Архитектура проекта

## 1. Цель и назначение
Проект «UGC Marketplace» — платформа, объединяющая бренды и креаторов (инфлюенсеров, блогеров, UGC-создателей, амбассадоров). Цель — создать экосистему для прозрачного, безопасного и масштабируемого сотрудничества брендов и создателей контента.

### Контекстная отметка v3.9-stable (manual freeze)
29.10.2025 — проект полностью восстановлен вручную, критические сценарии backend и frontend подтверждены вручную. Автотесты не запускались из-за неполных ORM-связей. Context Lock v3.9-stable зафиксирован для перехода в модуль IV «Коммуникации и интеграции».

## 2. Пользовательские роли и уровни доступа
1. **Бренд** — размещает кампании, управляет заказами и финансами, анализирует результаты.
2. **Креатор** — принимает заказы, создает контент, получает выплаты, участвует в рейтинге.
3. **Агент** — курирует группу креаторов, формирует отчеты и взаимодействует с брендами.
4. **Команда контент-завода** — отвечает за монтаж, выкладку и отчеты по роликам.
5. **Админ (3 уровня)** — модерация, финансовое управление и полное администрирование.
6. **Гость** — доступ к публичным рейтингам и примерам кампаний.

## 3. Кабинеты и панели
### 3.1 Кабинет бренда
- Мои кампании: активные, завершенные, черновики.
- Создание кампаний: пошаговый мастер (название, цели, формат, оплата, ТЗ, бюджет).
- Мои креаторы: список исполнителей, профили, избранное.
- Аналитика и отчеты: ER, CTR, ROI, выгрузка данных.
- Финансы: баланс, история транзакций, замороженные суммы.
- Чаты и поддержка: переписка с креаторами и агентами.
- Настройки профиля.

### 3.2 Кабинет креатора
- Лента заданий и фильтры (цена, формат, бренд, условия).
- Мои задания и статусы: в работе, на утверждении, завершено.
- Доходы и баланс, вывод средств.
- Статистика и рейтинг, архив роликов.
- Обучение (для PRO и PRO+).
- Чаты и уведомления.

### 3.3 Кабинет агента
- Список закрепленных креаторов, метрики, чаты, отчеты.
- Возможность предложить креатора бренду.

### 3.4 Кабинет контент-завода
- Управление задачами по видео, календарь выкладок, отчеты.

### 3.5 Админ-панель
1 уровень — модерация контента и профилей.  
2 уровень — финансы, отчеты, транзакции.  
3 уровень — полное управление платформой.

## 4. Система статусов креаторов
- **Базовый** — стандартные заказы, ограниченный рейтинг.  
- **PRO** — платная подписка, аналитика, обучение.  
- **PRO+** — приоритетные заказы, контракты.  
- **ELITE** — блогеры с большой аудиторией, индивидуальные условия.

## 5. Финансы и права
- Все транзакции через escrow (Точка Банк).  
- Форматы прав: полное право бренда, совместное использование, контент креатора.  
- Дополнительная услуга: white-label контент (бренд выкладывает ролик у себя).

## 6. Аналитика
- ER, CTR, ROI, CPM, просмотры, доходы и расходы.
- Публичная и персональная аналитика для брендов и креаторов.

## 7. Дерево сайта
- Публичные страницы: /, /for-brands, /for-creators, /about, /faq.
- Личные кабинеты: /creator, /brand, /agent, /admin, /factory.
- Разделы: кампании, заказы, финансы, аналитика, чаты, обучение.

## Структура директорий (2025-10-16)
```
.
├── assets
├── backend
│   └── app
│       └── __pycache__
├── frontend
│   ├── node_modules
│   │   ├── @eslint
│   │   ├── @eslint-community
│   │   ├── @humanwhocodes
│   │   ├── @nodelib
│   │   ├── @ungap
│   │   ├── acorn
│   │   ├── acorn-jsx
│   │   ├── ajv
│   │   ├── ansi-regex
│   │   ├── ansi-styles
│   │   ├── argparse
│   │   ├── balanced-match
│   │   ├── brace-expansion
│   │   ├── callsites
│   │   ├── chalk
│   │   ├── color-convert
│   │   ├── color-name
│   │   ├── concat-map
│   │   ├── cross-spawn
│   │   ├── debug
│   │   ├── deep-is
│   │   ├── doctrine
│   │   ├── dotenv
│   │   ├── escape-string-regexp
│   │   ├── eslint
│   │   ├── eslint-scope
│   │   ├── eslint-visitor-keys
│   │   ├── espree
│   │   ├── esquery
│   │   ├── esrecurse
│   │   ├── estraverse
│   │   ├── esutils
│   │   ├── fast-deep-equal
│   │   ├── fast-json-stable-stringify
│   │   ├── fast-levenshtein
│   │   ├── fastq
│   │   ├── file-entry-cache
│   │   ├── find-up
│   │   ├── flat-cache
│   │   ├── flatted
│   │   ├── fs.realpath
│   │   ├── glob
│   │   ├── glob-parent
│   │   ├── globals
│   │   ├── graphemer
│   │   ├── has-flag
│   │   ├── ignore
│   │   ├── import-fresh
│   │   ├── imurmurhash
│   │   ├── inflight
│   │   ├── inherits
│   │   ├── is-extglob
│   │   ├── is-glob
│   │   ├── is-path-inside
│   │   ├── isexe
│   │   ├── js-yaml
│   │   ├── json-buffer
│   │   ├── json-schema-traverse
│   │   ├── json-stable-stringify-without-jsonify
│   │   ├── keyv
│   │   ├── levn
│   │   ├── locate-path
│   │   ├── lodash.merge
│   │   ├── minimatch
│   │   ├── ms
│   │   ├── natural-compare
│   │   ├── once
│   │   ├── optionator
│   │   ├── p-limit
│   │   ├── p-locate
│   │   ├── parent-module
│   │   ├── path-exists
│   │   ├── path-is-absolute
│   │   ├── path-key
│   │   ├── prelude-ls
│   │   ├── prettier
│   │   ├── punycode
│   │   ├── queue-microtask
│   │   ├── resolve-from
│   │   ├── reusify
│   │   ├── rimraf
│   │   ├── run-parallel
│   │   ├── shebang-command
│   │   ├── shebang-regex
│   │   ├── strip-ansi
│   │   ├── strip-json-comments
│   │   ├── supports-color
│   │   ├── text-table
│   │   ├── type-check
│   │   ├── type-fest
│   │   ├── uri-js
│   │   ├── which
│   │   ├── word-wrap
│   │   ├── wrappy
│   │   └── yocto-queue
│   └── src
├── notes
│   ├── backups
│   └── note
└── scripts

107 directories
```

## 8. Основные UX-потоки
- Регистрация и онбординг.
- Создание кампаний брендом.
- Работа креатора (отклик → выполнение → оплата).
- Модерация и финансовый цикл.
- Аналитика и обратная связь.

# II. Backend — база данных, API и логика

## 1. Архитектура данных

### 1.1 Основные сущности
- **User** — пользователи платформы (бренды, креаторы, агенты, администраторы, команда контент-завода).
- **Campaign** — кампании, размещаемые брендами.
- **Application** — отклики креаторов на кампании.
- **Order** — связь между кампанией и креатором после принятия отклика.
- **Video** — информация о контенте (ссылки на внешние облака).
- **Payment** — транзакции escrow и выплаты.
- **Message** — сообщения в чатах.
- **Notification** — уведомления.
- **Rating** — история рейтингов.
- **Report** — отчёты агентов и фабрики.

### 1.2 Взаимосвязи между таблицами
- `User 1—* Campaign (brand_id)`
- `Campaign 1—* Application`
- `Application 1—1 Order`
- `Order 1—* Video`
- `Order 1—* Payment`
- `User 1—* Rating`
- `User 1—* Report`

### 1.3 Структура БД (Context Lock v2.1)
- `users`
  - `id UUID PK`, `email UNIQUE`, `hashed_password`, `full_name`, `role user_role`, `is_active`, `created_at`, `updated_at`
  - Индексы: `ix_users_email`
- `campaigns`
  - `id UUID PK`, `brand_id FK -> users.id`, `title`, `description`, `brief`, `budget NUMERIC(12,2)`, `currency`, `status campaign_status`, `start_date`, `end_date`, `created_at`, `updated_at`
  - Индексы/ограничения: `campaign_budget_positive`, `ix_campaigns_brand_id`
- `applications`
  - `id UUID PK`, `campaign_id FK`, `creator_id FK`, `status application_status`, `pitch`, `proposed_budget`, `message`, `created_at`, `updated_at`
  - Уникальность: одно заявление на кампанию от конкретного креатора (`uq_application_campaign_creator`)
- `orders`
  - `id UUID PK`, `application_id FK`, `campaign_id FK`, `creator_id FK`, `brand_id FK`, `status order_status`, `agreed_budget`, `deliverables`, `delivery_due`, `created_at`, `updated_at`
  - Уникальность: `application_id` встречается только один раз (`uq_order_application`)
- `videos`
  - `id UUID PK`, `order_id FK`, `storage_url`, `thumbnail_url`, `status video_status`, `notes`, `submitted_at`, `approved_at`
- `payments`
  - `id UUID PK`, `order_id FK`, `payment_type`, `status payment_status`, `amount`, `currency`, `reference UNIQUE`, `processed_at`, `created_at`
- `ratings`
  - `id UUID PK`, `user_id FK`, `score NUMERIC(3,2)`, `source`, `comment`, `created_at`
  - Уникальность: один источник → одна оценка (`uq_rating_user_source`)
- `reports`
  - `id UUID PK`, `author_id FK`, `campaign_id FK`, `order_id FK`, `report_type`, `content`, `created_at`
- `messages`
  - `id UUID PK`, `chat_id UUID`, `sender_id FK -> users.id`, `receiver_id FK -> users.id`, `content TEXT`, `is_read BOOLEAN`, `created_at`
  - Индексы: `ix_messages_chat_id_created_at`

```
users (1) ──< campaigns
users (1) ──< applications
users (1) ──< orders (creator_id)
users (1) ──< orders (brand_id)
applications (1) ──1 orders
orders (1) ──< videos
orders (1) ──< payments
users (1) ──< ratings
users (1) ──< reports
campaigns (1) ──< applications ──1 orders
campaigns (1) ──< reports
```

## REST API Specification

### Общие положения
- Базовый URL: `/api`.
- Формат данных: JSON, ключи в `snake_case`.
- Аутентификация: Bearer JWT (на этапе V2.2 используется mock-верификация).
- Коды ответов: `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `500 Internal Server Error`.
- Стандартная ошибка:
  ```json
  {
    "detail": "human readable message",
    "code": "error_identifier"
  }
  ```

### Auth
- `POST /api/auth/register`
  - Request:
    ```json
    {
      "email": "brand@example.com",
      "password": "Secret123!",
      "full_name": "Brand Manager",
      "role": "brand"
    }
    ```
  - Response `201`:
    ```json
    {
      "id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
      "email": "brand@example.com",
      "full_name": "Brand Manager",
      "role": "brand",
      "created_at": "2025-10-18T09:00:00Z"
    }
    ```
- `POST /api/auth/login`
  - Request:
    ```json
    {
      "email": "brand@example.com",
      "password": "Secret123!"
    }
    ```
  - Response `200`:
    ```json
    {
      "access_token": "mock.jwt.token",
      "token_type": "bearer",
      "user": {
        "id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
        "email": "brand@example.com",
        "role": "brand"
      }
    }
    ```

### Campaigns
- `GET /api/campaigns` — фильтры `status`, `brand_id`.
  - Response `200`:
    ```json
    {
      "items": [
        {
          "id": "f7d2ec3f-671e-43f9-bc7f-9af7b6f145a0",
          "title": "Reels Autumn Launch",
          "status": "active",
          "budget": "150000.00",
          "currency": "RUB",
          "brand_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
          "created_at": "2025-10-10T15:30:00Z"
        }
      ],
      "total": 1
    }
    ```
- `POST /api/campaigns`
  - Request:
    ```json
    {
      "title": "Winter Promo",
      "description": "UGC drive for New Year",
      "budget": "200000.00",
      "currency": "RUB"
    }
    ```
  - Response `201`:
    ```json
    {
      "id": "41a4ad8d-a0c0-4ff7-9d1d-2ae4994a6f4c",
      "title": "Winter Promo",
      "status": "draft",
      "budget": "200000.00",
      "currency": "RUB",
      "brand_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
      "created_at": "2025-10-18T10:00:00Z"
    }
    ```
  - Примечание: `brand_id` автоматически подставляется из токена бренда; администраторы могут передать его явно.

### Brands
- `POST /api/brands` — создание бренд-профиля для авторизованного бренда.
  - Request:
    ```json
    {
      "name": "Acme Corp",
      "description": "Consumer electronics"
    }
    ```
  - Response `201`:
    ```json
    {
      "id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
      "name": "Acme Corp",
      "description": "Consumer electronics",
      "created_at": "2025-10-18T10:02:00Z"
    }
    ```

### Applications
- `POST /api/applications`
  - Request:
    ```json
    {
      "campaign_id": "f7d2ec3f-671e-43f9-bc7f-9af7b6f145a0",
      "creator_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
      "pitch": "I can deliver 3 UGC videos in 7 days",
      "proposed_budget": "45000.00"
    }
    ```
  - Response `201`:
    ```json
    {
      "id": "a37f227a-e463-4964-9c88-97f33042b6c4",
      "status": "pending",
      "campaign_id": "f7d2ec3f-671e-43f9-bc7f-9af7b6f145a0",
      "creator_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
      "created_at": "2025-10-18T10:05:00Z"
    }
    ```

### Orders
- `GET /api/orders`
  - Response `200`:
    ```json
    {
      "items": [
        {
          "id": "19bc1f23-08c8-4a26-b7a9-9f52ef9d8a12",
          "status": "in_progress",
          "campaign_id": "f7d2ec3f-671e-43f9-bc7f-9af7b6f145a0",
          "creator_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
          "brand_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
          "agreed_budget": "45000.00"
        }
      ],
      "total": 1
    }
    ```
- `PATCH /api/orders/{order_id}`
  - Request:
    ```json
    {
      "status": "approved"
    }
    ```
  - Response `200`:
    ```json
    {
      "id": "19bc1f23-08c8-4a26-b7a9-9f52ef9d8a12",
      "status": "approved",
      "updated_at": "2025-10-18T11:00:00Z"
    }
    ```

### Payments
- `POST /api/payments` — создание операции hold.
  - Request:
    ```json
    {
      "order_id": "19bc1f23-08c8-4a26-b7a9-9f52ef9d8a12",
      "payment_type": "hold",
      "amount": "45000.00",
      "currency": "RUB"
    }
    ```
  - Response `201`:
    ```json
    {
      "id": "4f8dcb60-9fbb-4e54-9a2f-fd6f8a376281",
      "order_id": "19bc1f23-08c8-4a26-b7a9-9f52ef9d8a12",
      "payment_type": "hold",
      "status": "pending",
      "amount": "45000.00",
      "currency": "RUB",
      "created_at": "2025-10-18T11:05:00Z"
    }
    ```

### Notifications
- `GET /api/notifications` — поддерживает фильтры `user_id`, `is_read`.
  - Response `200`:
    ```json
    {
      "items": [
        {
          "id": "c82b2bfa-6da2-4df2-8311-2c24fe6125b1",
          "user_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
          "type": "campaign_update",
          "title": "Новая кампания",
          "content": "Your application was approved",
          "related_id": "camp-42",
          "is_read": false,
          "created_at": "2025-10-18T11:10:00Z"
        }
      ],
      "total": 1
    }
    ```
- `PATCH /api/notifications/{id}/read` — помечает уведомление как прочитанное.
- `POST /api/notifications/send` — системное уведомление (доступно администраторам).

Типы уведомлений:
- `chat_message`
- `new_campaign`
- `payment_success`
- `admin_notice`

Структура `notifications`:
`id | user_id | type | title | content | is_read | created_at | related_id`

### Telegram Webhook
- `POST /api/webhooks/telegram` — принимает обновления от Telegram, поддерживаются команды `/start`, `/profile`, `/balance`, `/unsubscribe`.
- Ссылки вида `https://t.me/<bot>?start=<user_id>` формируют привязку пользователя к Telegram.
- Логирование всех событий ведётся в `logs/telegram.log`; при отсутствии `TELEGRAM_BOT_TOKEN` используется mock-режим.
- Структура `telegram_links`: `id | user_id | telegram_id | username | first_name | last_name | is_active | created_at | updated_at`.
- При наличии токена уведомления доставляются в Telegram через Bot API, иначе фиксируются как `bot_disabled`.


### Chat
- `POST /api/chat/send` — отправка сообщения в указанный чат.
  - Request `201`:
    ```json
    {
      "chat_id": "41a4ad8d-a0c0-4ff7-9d1d-2ae4994a6f4c",
      "receiver_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
      "content": "Привет! Готов обсудить детали кампании."
    }
    ```
  - Response `201`:
    ```json
    {
      "id": "dd2f9cf1-72be-4f5f-849d-6eb97f9d9101",
      "chat_id": "41a4ad8d-a0c0-4ff7-9d1d-2ae4994a6f4c",
      "sender_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
      "receiver_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
      "content": "Привет! Готов обсудить детали кампании.",
      "is_read": false,
      "timestamp": "2025-10-18T10:42:00Z"
    }
    ```
- `GET /api/chat/{chat_id}` — история сообщений, параллельно помечает входящие как прочитанные.
  - Response `200`:
    ```json
    {
      "total": 2,
      "items": [
        {
          "id": "dd2f9cf1-72be-4f5f-849d-6eb97f9d9101",
          "chat_id": "41a4ad8d-a0c0-4ff7-9d1d-2ae4994a6f4c",
          "sender_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
          "receiver_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
          "content": "Привет! Готов обсудить детали кампании.",
          "is_read": true,
          "timestamp": "2025-10-18T10:42:00Z"
        },
        {
          "id": "b13c947b-ff27-4d46-9fd0-66ce763637f6",
          "chat_id": "41a4ad8d-a0c0-4ff7-9d1d-2ae4994a6f4c",
          "sender_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
          "receiver_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
          "content": "Отлично, я на связи!",
          "is_read": false,
          "timestamp": "2025-10-18T10:44:12Z"
        }
      ]
    }
    ```
- WebSocket `GET /ws/chat/{chat_id}` — двустороннее соединение, обязательный query `token`.
  - Payload уведомления:
    ```json
    {
      "event": "message",
      "data": {
        "id": "dd2f9cf1-72be-4f5f-849d-6eb97f9d9101",
        "chat_id": "41a4ad8d-a0c0-4ff7-9d1d-2ae4994a6f4c",
        "sender_id": "8d1f38ec-4ff3-4e0c-82ac-1c2acfb4d5b9",
        "receiver_id": "c34d1de2-9b19-4aa5-82fd-a1a0f5ebd2b7",
        "content": "Привет!",
        "timestamp": "2025-10-18T10:42:00Z",
        "is_read": false
      }
    }
    ```

### Ошибки
- `400 Bad Request` — ошибки валидации/бизнес-правил:
  ```json
  {
    "detail": "budget must be positive",
    "code": "validation_error"
  }
  ```
- `401 Unauthorized` — ошибки авторизации.
- `404 Not Found` — ресурс не найден.
- `500 Internal Server Error` — необработанные исключения, логируются middleware.

## Notifications & Webhooks System

### 1. Таблицы
- **Notification**
  - Поля: `id UUID PK`, `user_id FK -> users.id`, `type VARCHAR(64)`, `message TEXT`, `is_read BOOLEAN DEFAULT false`, `created_at TIMESTAMP`.
  - Индексы: `ix_notifications_user_id`, использование каскадного удаления к пользователю.
- **WebhookEvent**
  - Поля: `id UUID PK`, `event_type VARCHAR(80)`, `payload JSONB`, `signature VARCHAR(255)`, `created_at TIMESTAMP`.
  - Назначение: аудит входящих webhook'ов и диагностика интеграций.

### 2. Потоки уведомлений
- Создание кампании — уведомляет бренд (`campaign.created`).
- Заморозка и подтверждение платежа — уведомляют бренд и креатора (`payment.hold`, `payment.completed`).
- Обновление статуса заказа — уведомляет обе стороны (`order.status`).
- Отправка выполняется через `BackgroundTasks`, чтобы не блокировать HTTP-ответ.

### 3. Webhook payloads
- `POST /api/webhooks/payment`
  ```json
  {
    "payment_id": "4f8dcb60-9fbb-4e54-9a2f-fd6f8a376281",
    "status": "completed",
    "signature": "hmac-sha256",
    "metadata": {
      "provider": "bank-mock",
      "reference": "TX-20251018-001"
    }
  }
  ```
  - Логика: обновить `payments.status`, зафиксировать событие в `webhook_events`, разослать уведомления.
- `POST /api/webhooks/order`
  ```json
  {
    "order_id": "19bc1f23-08c8-4a26-b7a9-9f52ef9d8a12",
    "status": "delivered",
    "message": "Factory marked as delivered",
    "signature": "hmac-sha256"
  }
  ```
  - Логика: обновить `orders.status`, сохранить событие, уведомить бренд и креатора.

### 4. Обработка уведомлений
1. REST-эндпоинт инициирует событие (создание кампании, изменение статуса).
2. Через `schedule_batch_notifications` формируется очередь фоновых задач.
3. Фоновая задача открывает транзакцию, записывает `Notification`.
4. Клиент получает уведомления через `GET /api/notifications` и может отметить их прочитанными `POST /api/notifications/mark-read`.

## Архитектура безопасности API
- JWT-аутентификация: access-токен (15 мин) + refresh-токен (7 дней) с алгоритмом HS256. Refresh ротуируется при обновлении и попадает в blacklist после `/api/auth/logout`.
- Валидация токенов: `verify_token` проверяет подпись, тип и срок действия; `get_current_user` строится на access-токене.
- Middleware:
  - CORS пропускает только origin'ы из `ALLOWED_ORIGINS`.
  - Rate limiter ограничивает до 60 запросов/минуту на IP, возвращая 429 и заголовок `Retry-After`.
  - Request logger (Loguru) пишет логи в `logs/app.log` в формате `[YYYY-MM-DD HH:mm:ss] LEVEL — сообщение`.
- Централизованные обработчики ошибок — унифицированные ответы `{"status":"error","code":...}` для `HTTPException`, `ValidationError`, `TokenError`, `IntegrityError` и неожиданных ошибок.
- Обновление токенов: `/api/auth/refresh` выдает новую пару access/refresh с немедленной ревокацией старого refresh.

## Admin API Layer
- Уровни доступа:
  - `admin_level_1` (Moderator) — просмотр пользователей, кампаний, заморозка статусов, работа с жалобами.
  - `admin_level_2` (Finance) — доступ к статистике и финансовым отчётам, выгрузка CSV.
  - `admin_level_3` (Superuser) — полный доступ, изменение ролей, удаление пользователей и кампаний.
- Dependencies: `require_admin(level)` проверяет `user.admin_level` через JWT.
- Маршруты:
  - `/api/admin/users` — список, изменение роли, удаление.
  - `/api/admin/campaigns` — обзор, изменение статуса, удаление.
  - `/api/admin/statistics` + `/export` — агрегированные метрики и отчёты.
- Отчётность: сервис `reports` рассчитывает роли, топ-бренды/креаторов, суммы платежей, экспорт в CSV.
- Логи: действия записываются в таблицу `admin_logs` и файл `logs/admin_actions.log` через middleware.

## 3. ORM-модели (Prisma-style)

### 3.1 Пример модели User
```prisma
model User {
  id                String   @id @default(uuid())
  role              Role
  name              String
  email             String   @unique
  telegram          String?
  rating            Float    @default(0)
  balance           Decimal  @default(0)
  subscription_tier SubscriptionTier @default(FREE)
  created_at        DateTime @default(now())
}
```

### 3.2 Пример модели Campaign
```prisma
model Campaign {
  id          String   @id @default(uuid())
  brand_id    String
  title       String
  description String
  budget      Decimal
  status      CampaignStatus @default(DRAFT)
  created_at  DateTime @default(now())
}
```

## 4. Система Escrow
- Все платежи проходят через API Точка Банк.
- Средства блокируются при создании кампании (`type=hold`).
- Разблокировка (`release`) происходит после утверждения видео.
- Все операции логируются и сохраняются в таблице `payments`.

## 5. Безопасность и валидация
- Авторизация через JWT (access + refresh tokens).
- Валидация запросов на уровне middleware.
- Rate limiting для защиты от спама.
- Webhooks: `/api/webhooks/bank` — уведомления от банка.

## 6. Триггеры и события
- После `video.status = approved` → `release escrow`.
- После `order.status = completed` → обновление рейтинга.
- После `payment.error` → уведомление администратору.

## 7. Преимущества архитектуры
- Лёгкая масштабируемость.
- Минимальные затраты при MVP.
- Гибкая ORM-модель для любых технологий.
- Возможность интеграции с CDN и внешними API в будущем.

# III. Frontend — структура, UI и маршрутизация

## 1. Структура проекта (Next.js + TypeScript)
```
/ugc-marketplace-frontend
├── /public
├── /src
│   ├── /app
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── /auth (login, register, forgot)
│   │   ├── /creator (feed, orders, balance, rating, learning)
│   │   ├── /brand (campaigns, create, analytics, finance)
│   │   ├── /agent (creators, reports)
│   │   ├── /admin (campaigns, users, finance, analytics)
│   │   ├── /factory (tasks, calendar)
│   │   └── /public (top-creators, cases, faq, about)
│   ├── /components
│   │   ├── /ui (Button, Input, Modal, Card, Badge)
│   │   ├── /layout (Header, Sidebar, Footer)
│   │   ├── /forms (CampaignForm, VideoForm)
│   │   ├── /tables (OrdersTable, CampaignTable)
│   │   └── /charts (AnalyticsChart)
│   ├── /hooks (useAuth, useFetch, useNotifications, useChat)
│   ├── /lib (api.ts, constants.ts, utils.ts, storage.ts, roles.ts)
│   ├── /context (AuthContext, NotificationContext, ChatContext)
│   ├── /store (userStore, campaignStore, orderStore, uiStore)
│   ├── /types (user.ts, campaign.ts, video.ts, order.ts)
│   ├── /styles (globals.css, theme.css)
│   └── /tests (auth.test.ts, api.test.ts, ui.test.ts)
└── package.json
```

## 2. Основные маршруты
| Роль | Путь | Разделы |
|------|------|----------|
| Гость | `/` | `/faq`, `/cases`, `/top-creators` |
| Креатор | `/creator` | `/feed`, `/orders`, `/balance`, `/rating`, `/learning` |
| Бренд | `/brand` | `/campaigns`, `/create`, `/analytics`, `/finance` |
| Агент | `/agent` | `/creators`, `/reports` |
| Админ | `/admin` | `/campaigns`, `/users`, `/finance`, `/analytics` |
| Контент-завод | `/factory` | `/tasks`, `/calendar` |

## 3. Компоненты интерфейса
- **UI-компоненты:** кнопки, поля, модальные окна, карточки, статусы.
- **Средние компоненты:** карточки кампаний, таблицы заказов.
- **Высокие компоненты:** мастера кампаний, статус-бары, формы ссылок на видео.

## 4. Контексты
- **AuthContext** — авторизация, роль, токен.
- **NotificationContext** — уведомления.
- **ChatContext** — активный чат.
- **ThemeContext** — тема интерфейса.

## 5. Состояния и сторы
| Store | Данные | Триггеры |
|--------|---------|----------|
| userStore | токен, роль | login/logout |
| campaignStore | кампании | loadCampaigns |
| orderStore | заказы | updateOrderStatus |
| notificationStore | уведомления | pushNotification |

## 6. Логика работы с API
- Все запросы выполняются через `lib/api.ts` (fetch или SWR).
- Авторизация: `Authorization: Bearer <token>`.
- Ошибки отображаются через toast-уведомления.
- Данные обновляются polling’ом (или WebSocket’ом).

## 7. Стек технологий
| Компонент | Технология |
|------------|-------------|
| Framework | Next.js 15 |
| Language | TypeScript |
| CSS | TailwindCSS + shadcn/ui |
| Forms | React Hook Form |
| State | Zustand или Redux Toolkit |
| API | Fetch / SWR |
| Deployment | Vercel / Netlify |

## 8. Логика данных
| Действие | API | UI |
|-----------|-----|----|
| Вход | `/api/auth/login` | сохранение токена, редирект |
| Отклик креатора | `/api/applications` | уведомление “Отклик отправлен” |
| Прикрепление видео | `/api/videos` | обновление статуса |
| Утверждение видео | `/api/videos/:id` | обновление аналитики |
| Выплата | `/api/payouts` | уведомление о выплате |

## 9. Тестирование
- **Unit-тесты:** компоненты UI, API-запросы.
- **Integration-тесты:** регистрация, авторизация, кампании.
- **End-to-End:** Cypress, сценарии для креатора и бренда.

## 10. Итог

# IV. Roadmap и управление задачами (M0–M10 + Context Lock)

## 1. Общие принципы
Разработка проекта делится на десять основных этапов (M0–M10). Каждый этап соответствует отдельному коммиту в GitHub и отражает ключевую точку прогресса. Все задачи выполняются Codex с фиксацией изменений в `tasks.md` и `changelog.md`.

## 2. Этапы разработки

### M0 — Инициализация проекта
**Цель:** создать структуру и базовую конфигурацию проекта.
- Инициализация фронтенда и бэкенда.
- Настройка TypeScript, ESLint, Prettier.
- Создание файлов: `/notes/project_plan.md`, `/notes/tasks.md`, `/notes/changelog.md`.
- Настройка `.env` и переменных окружения.
- Commit: `init: project structure`.

### M1 — Архитектура и авторизация
**Цель:** базовая авторизация и маршрутизация.
- Реализация `/api/auth/register`, `/login`, `/users/me`.
- JWT-аутентификация и refresh-токены.
- Настройка AuthContext и страниц login/register.
- Commit: `feat: auth + routing`.

### M2 — Структура кабинетов
**Цель:** навигация по ролям и layout-интерфейс.
- Реализация редиректа по ролям.
- Создание layout-файлов для `/creator`, `/brand`, `/admin`.
- Добавление Sidebar и Header.
- Commit: `feat: dashboards skeleton`.

### M3 — Модуль CREATOR
**Цель:** лента заданий, отклики, прикрепление видео.
- GET `/api/campaigns` — список заданий.
- POST `/api/applications` — отклик на кампанию.
- GET `/api/orders` — список заказов.
- POST `/api/videos` — прикрепление ссылок.
- Commit: `feat: creator module v1`.

### M4 — Модуль BRAND
**Цель:** управление кампаниями и утверждение видео.
- POST `/api/campaigns` — создание кампании.
- GET `/api/applications?campaign_id=`.
- PATCH `/api/applications/:id` — принятие креаторов.
- PATCH `/api/videos/:id` — утверждение контента.
- Commit: `feat: brand module v1`.

### M5 — Модули AGENT и FACTORY
**Цель:** управление креаторами и контентом.
- GET `/api/users?role=creator&agent_id=`.
- POST `/api/reports` — отчёты агента.
- GET `/api/factory/tasks` — задачи контент-завода.
- Commit: `feat: agent+factory`.

### M6 — Модуль ADMIN
**Цель:** модерация и аналитика платформы.
- GET `/api/campaigns?status=pending`.
- PATCH `/api/campaigns/:id` — одобрение кампаний.
- GET `/api/payments`, `/api/users` — отчёты.
- Commit: `feat: admin panel v1`.

### M7 — Коммуникации (чаты и уведомления)
**Цель:** коммуникации между ролями.
- POST `/api/chat/send`, GET `/api/chat/:id`.
- GET `/api/notifications`.
- Подключение Telegram Webhook.
- Commit: `feat: chats+notifications`.

### M8 — Финансы и Escrow
**Цель:** реализация платёжных процессов.
- POST `/api/payments` — заморозка бюджета.
- POST `/api/payouts` — выплаты.
- GET `/api/payments?user_id=` — история транзакций.
- Commit: `feat: payments module`.

### M9 — Геймификация и рейтинги
**Цель:** мотивация креаторов и система статусов.
- Таблица `Rating` и API `/api/rating`.
- Страница `/creator/rating`.
- Система рангов (PRO, PRO+, ELITE).
- Commit: `feat: gamification`.

### M10 — Финализация и Context Lock
**Цель:** зафиксировать систему и документацию.
- Обновить `/notes/project_plan.md`, `/notes/tasks.md`, `/notes/changelog.md`.
- Commit: `Context Lock v1.0 — Architecture Frozen`.

## 3. Контроль прогресса
- Каждая задача фиксируется в `tasks.md` с меткой статуса.
- Изменения фиксируются Codex в `changelog.md`.
- После каждого milestone выполняется push в GitHub.

## 4. Протокол фиксации
```
git add .
git commit -m "Context Lock v1.0 — Architecture Frozen"
git push origin main
```

## 5. Результат
После выполнения M10 платформа достигает стабильного MVP-состояния. Все архитектурные решения, версии и данные зафиксированы в репозитории и могут быть восстановлены из точки Context Lock.
