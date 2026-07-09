# PROJECT_MEMORY.md

Last source inspection: 2026-07-09

## A. Project Identity

- **Project name:** AK English Bot / English AI
- **Project type:** Telegram-based AI English tutor with a small FastAPI runtime wrapper.
- **Main purpose:** Answer English-learning questions, explain text and images, support voice practice, and manage paid access through Telegram.
- **Target users:** Telegram users learning English with Tajik, Russian, or Uzbek interface support.
- **Current status:** The English QA path is implemented in code. Production deployment and live database state are `Unknown / needs confirmation`.
- **Important history:** The repository still contains a legacy HSK Chinese course system. It is intentionally disabled.

## B. Core Architecture

| Area | Current implementation |
| --- | --- |
| Main interface | Telegram bot using `aiogram` 3 |
| Runtime | `FastAPI` app with `/health`; bot long polling starts in lifespan |
| Backend | Async Python services, handlers, repositories, and scheduler |
| Database | PostgreSQL through SQLAlchemy async + `asyncpg`; Alembic migrations |
| FSM state | `aiogram.fsm.storage.memory.MemoryStorage` |
| AI provider | OpenAI through `AsyncOpenAI` |
| QA model | `gpt-4o-mini` |
| General/course/vision defaults | `o4-mini` |
| Voice transcription | `gpt-4o-mini-transcribe` |
| Payment system | Manual Telegram screenshot review for Visa, AliPay, and WeChat |
| Deployment files | `railway.toml`, `Procfile`, `scripts/start.sh`, `docker-compose.yml` |
| Mini App/frontend | No active Mini App or web frontend found |

External-service notes:

- Telegram is the primary user channel.
- OpenAI powers QA, image explanation, voice transcription/translation, and advisory payment screenshot analysis.
- Redis configuration exists, but active application usage was not found.
- `AirtableSyncService` exists, but active callers were not found. Treat it as legacy or unfinished until confirmed.
- Local `app.db` is a zero-byte SQLite artifact; active code targets PostgreSQL.

## C. Important Project Rules

- Make minimal safe changes and preserve existing bot behavior.
- Do not change payment, subscription, access, referral, discount, or AI budget logic without tracing the complete flow.
- PostgreSQL is the source of truth. Review models, repositories, services, migrations, and scheduler side effects together.
- Do not enable legacy course mode casually. It still contains HSK Chinese content and prompts.
- Never store secrets or real environment values in documentation.
- Update this file only for durable architecture, schema, business-logic, deployment, or risk changes.

## D. Key Files And Folders

| Path | Purpose | Be careful about |
| --- | --- | --- |
| `app/main.py` | FastAPI lifespan, bot startup, scheduler loop | Scheduler changes can alter expiry, reminders, ads, and feedback timing |
| `app/config.py` | Environment loading and feature flags | Do not expose defaults; `COURSE_MODE_ENABLED=False` is intentional |
| `app/bot/create_bot.py` | Bot creation and router registration order | Generic handlers must remain after specific FSM/payment/admin handlers |
| `app/bot/middlewares/required_channel.py` | Forced-channel subscription gate | Paid users and admins bypass; pending text can resume after verification |
| `app/bot/handlers/start.py` | Onboarding, referral start payload, returning-user reset | Returning users reset to QA mode |
| `app/bot/handlers/messages.py` | Generic text, image, and voice entry points | Shared access counters and voice-mode behavior are sensitive |
| `app/bot/handlers/payments.py` | Checkout and screenshot submission | Preserve draft/pending payment recovery behavior |
| `app/bot/handlers/admin_payments.py` | Manual admin approval/rejection | Approval activates subscription and budget records |
| `app/bot/handlers/admin.py` | Admin operations | Contains user access, pricing, channel, portfolio, and deletion operations |
| `app/services/access_service.py` | Trial, expiry, limits, and access checks | Small changes can affect all QA usage |
| `app/services/subscription_service.py` | Paid-plan activation | Keep user status, dates, discounts, and usage budget consistent |
| `app/services/ai_usage_budget_service.py` | Paid AI budget enforcement and events | Paid usage depends on these records |
| `app/services/qa_service.py` | QA prompt assembly and usage accounting | Preserve access checks, message history, referral activation, and commits |
| `app/services/image_input_service.py`, `app/services/image_qa_service.py` | Photo intake, analysis flow, and image limits | Image usage shares counters with text logic |
| `app/bot/handlers/messages.py`, `app/services/ai_service.py` | Voice-mode control, transcription, QA, and translation | Voice is paid-only and has duration limits |
| `app/services/payment_screenshot_ai_service.py` | Advisory screenshot analysis | Must not become automatic payment approval |
| `app/services/referral_service.py` | Referral attachment, activation, bonus, discount progress | Bonus and discount counters must stay idempotent |
| `app/services/discount_service.py`, `app/repositories/discount_campaign_repo.py` | Targeted discount campaigns | Quota, targeting, and time-window logic are business-critical |
| `app/services/required_channel_service.py` | Required-channel database settings | Coordinate with middleware and admin controls |
| `app/services/daily_reset_service.py`, `app/services/expiry_reminder_service.py`, `app/services/course_reminder_service.py` | Usage reset, expiry, and reminder sending | Course-off mode still reuses reminder records for QA prompts |
| `app/services/course_*_service.py` | Disabled legacy HSK course engine and tutor | Do not treat as an English course implementation |
| `app/db/models/` | SQLAlchemy schema modules | Review with Alembic and startup bootstrap logic |
| `app/db/session.py` | Engine, `create_all`, bootstrap column patches | Runtime schema patching can hide migration drift |
| `alembic/versions/` | Schema history | Add migrations for schema changes |
| `app/prompts/qa_system.txt` | English QA system prompt | Keep level adaptation, language response, and subscription routing |
| `scripts/start.sh` | Deployment startup and migration commands | Current fallback stamping can conceal schema mismatch |
| `scripts/seed_hsk*.py` | Legacy HSK seed scripts | Inactive while course mode is off |
| `graphify-out/GRAPH_REPORT.md` | Generated architecture overview | Report may be stale or include mixed corpus noise; verify against code |

## E. Database Schema Summary

There is no separate `subscriptions` table. Subscription state is stored mainly on `users`, supported by `payments` and AI budget records.

| Table | Important fields and purpose |
| --- | --- |
| `users` | Telegram identity; `lang`, `level`, `learning_mode`, `voice_mode`; `status`, `payment_status`; question and bonus counters; referral and discount state; selected checkout plan; access dates; reminder flags |
| `messages` | User conversation history with role, content, type, Telegram message ID, and timestamp; also stores image context, onboarding challenge, and voice transcript records |
| `payments` | Telegram user, plan, method, base/final amount, currency, status, screenshot, admin comment, discount snapshot, checkout and waiting-message IDs, submitted/reviewed dates |
| `referrals` | Referrer and invited Telegram IDs, status, bonus grant marker, discount-count marker, timestamps |
| `discount_campaigns` | Active windows, multilingual copy, percent, targeting filters, optional user/method/plan restriction, quota, repeat interval, creator |
| `subscription_prices` | Database overrides by payment method and plan |
| `ai_usage_budgets` | Paid AI allowance tied to an activated plan/payment context |
| `ai_usage_events` | Per-source/model token and cost tracking |
| `course_lessons` | Legacy HSK lesson JSON content |
| `course_progress` | Legacy course state plus reminder and weekly-report fields; reminder fields are still reused |
| `course_attempts` | Legacy course answer/homework attempts |
| `course_audio` | Legacy Telegram audio file references |
| `bot_feedbacks` | Feedback prompt, completion, reply, reward, and follow-up state |
| `bot_settings` | Persistent feature settings such as forced-channel gating |
| `required_channels` | Channels users may be required to join |
| `ad_campaigns` | Scheduled admin broadcast campaigns and targeting configuration |
| `ad_deliveries` | Per-user delivery records for ad campaigns |
| `portfolio_transactions` | Subscription and manual profit/expense ledger |

Schema notes:

- Migrations exist through `alembic/versions/0039_*`.
- Startup also runs `Base.metadata.create_all()` and legacy `ALTER TABLE` bootstrap checks in `app/db/session.py`.
- Exact live Railway schema and applied migration revision are `Unknown / needs confirmation`.
- There are no separate homework or quiz-result tables; legacy course attempts and progress store that state.

## F. Current Business Logic

### User Onboarding

- `/start` creates a new user with `status=trial`, `payment_status=none`, QA mode, Tajik default language, beginner level, five-question base limit, and no initial active subscription window.
- New users select interface language: Tajik, Russian, or Uzbek.
- Users select English level using Beginner, A1, A2, B1, and B2 labels, then choose a trial course lesson. Internally, the imported course scaffold still maps these levels to legacy `hsk1`-`hsk4` lesson levels until English course material is finalized.
- Level selection keeps unpaid users in `trial`, clears active dates, and routes them to trial lesson selection.
- Returning unpaid trial users without a selected trial lesson are sent back to trial lesson selection; returning course users get course access checked before the menu is shown.

### Access, Trial, And Limits

- Blocked users are denied access.
- Active users with an unexpired period can use text AI. If an AI budget exists, paid-budget enforcement also applies.
- Initial onboarding is a `trial` flow, not a temporary `active` free period. Trial users are routed toward one selected course lesson and normal daily trial limits still apply.
- Expired active users are downgraded to `trial`; the scheduler also performs this downgrade.
- Trial users receive daily text-question resets. The base question limit defaults to five for newly created users.
- Bonus questions can extend trial usage.
- Image use for unpaid/trial users is limited per UTC day. Paid approved users use AI budget checks instead.
- Voice mode requires `status=active` and `payment_status=approved`; voice messages are capped at 60 seconds.

### Referral And Bonus Logic

- A `/start=<referral_code>` payload can attach a referrer once. Self-referral is rejected.
- A referral activates after the invited user has used at least two questions.
- Activation grants the referrer five bonus questions once.
- During an eligible referral-discount window, qualifying referral activations increment discount progress. Three qualifying activations make the referrer discount-eligible.
- The referral discount is consumed after a successful subscription activation.

### Payment And Subscription Flow

- Supported methods are Visa, AliPay, and WeChat.
- Supported plans are 10 days and 1 month.
- Prices may come from database overrides in `subscription_prices`; code defaults are fallback values.
- Checkout creates or reuses a draft payment and stores the selected plan on the user.
- The user uploads a payment screenshot in Telegram. The payment becomes pending and admins receive a review notification.
- Screenshot AI analysis is advisory only: it can mark a screenshot trusted, suspicious, or rejected for admin context, but it does not approve access.
- Admin approval marks the payment approved, activates the selected plan, sets paid access dates, consumes applicable discount state, creates AI budget records, records subscription portfolio profit, and notifies the user.
- Admin rejection marks the payment rejected and restores the selected plan so the user can retry.
- Expired paid users are downgraded to trial. A reminder is sent about one day before paid expiry.
- Payment-backed AI allowance is split into two plan segments. Usage events are costed by source/model, and overuse can trigger a six-hour cooldown.
- `/giveaccess TELEGRAM_ID PLAN` grants active approved access without a payment-backed budget. `AccessService` permits AI when no active budget exists, so this manual path effectively bypasses normal paid-budget throttling. Confirm that this complimentary behavior is intentional before changing it.

### Discounts And Campaigns

- Normal checkout applies referral discount logic.
- Admin-created targeted campaigns can restrict user, audience status, language, level, payment method, plan, active window, quota, and repeat interval.
- Admin campaign discounts are applied through the campaign notification/callback path rather than ordinary checkout.
- Feedback can schedule a separate 20% price-offer path after a negative response.

### Feedback

- Users become eligible for a feedback prompt after approximately one day. Completed feedback is not requested again for approximately 30 days; unfinished feedback can be retried after approximately 24 hours.
- Completing feedback grants one extra active day, resets question usage, and clears pending checkout state.
- A price-related negative response schedules a 20% offer after approximately five minutes.
- Admins can reply to completed feedback from the bot.

### Required Channel Gate

- Admins bypass forced-channel checks.
- Paid approved active users bypass forced-channel checks.
- `/start` and onboarding states are allowed through the middleware.
- Other users must join configured active channels when the database setting `force_channel_subscription_enabled` is enabled.
- A blocked text request can be stored and resumed after the user presses the membership-check callback.

### AI And Prompt Behavior

- Text QA uses `app/prompts/qa_system.txt`, the user language and level, up to five recent messages, latest image context, and latest onboarding challenge when available.
- The QA prompt positions the bot as an English tutor, avoids unsolicited extras, routes subscription questions to `/subscription`, and hides provider details.
- QA usage records the user message, assistant response, AI usage source, question consumption, and referral activation attempt.
- Photo analysis uses vision plus an explanation pass and stores reusable image context.
- Voice first asks the user to choose QA practice or translator mode, then persists that mode until text input exits it.

### Course Mode

- `COURSE_MODE_ENABLED=False`.
- The course router is not registered, course seeding is skipped, promotional course entry is gated off, and course-mode users are reset to QA when they send messages.
- Legacy HSK lessons, seed scripts, progress, attempts, audio references, Chinese tutor prompts, and engine services remain in the repository.
- English-facing onboarding/course lesson lists filter out legacy lessons containing CJK/Chinese characters so old HSK material is not shown as English course content.
- Static `app/static/course_v3_data` lesson maps, lesson JSON files, exam JSON files, ads copy, and `hsk-data.js` are English-facing as of 2026-07-09, while legacy internal identifiers such as `hsk1`-`hsk4`, `zh`, `pinyin`, and `build_chinese_sentence` remain intentionally unchanged.
- Reminder records in `course_progress` are still reused for QA reminders even while course mode is disabled.
- Enabling course mode requires product, content, prompt, and migration review. Flipping the flag alone is unsafe.

### Admin Tools

- Admin tools include statistics, user search, access grants, user deletion, payment review, dynamic prices, required channels, broadcast, scheduled ads, targeted discounts, portfolio records, feedback replies, and legacy audio operations.
- Scheduled ad campaigns support targeting and delivery throttling: the creation flow enforces at least a 10-minute interval and no more than 24 sends per campaign.
- A code path that sets or clears `users.status=blocked` was not found: `Unknown / needs confirmation`.

### Notifications And Scheduler

- The scheduler runs approximately once per minute.
- It handles expired-user downgrade, daily trial reset notifications, paid-expiry reminders, QA reminders backed by progress records, conditional weekly course reports, feedback offer timing, due ads, and periodic feedback prompt checks.
- Weekly course progress sending is skipped while course mode is off.

## G. Current Features

### Working In Code

- Telegram onboarding and multilingual interface selection
- English text QA with level-aware prompts and message context
- Image explanation with follow-up context
- Paid voice QA/translator modes
- Trial access, question limits, daily reset, and bonus questions
- Referral rewards and referral-discount progress
- Manual screenshot-based payments and admin review
- Database-backed subscription price overrides
- Required-channel gating
- Admin feedback, pricing, ads, discounts, portfolio, and user tools
- Reminder and expiry scheduler

### Partially Working Or Inactive

- Legacy HSK course mode is preserved but intentionally disabled.
- Airtable sync service exists without confirmed active callers.
- Redis configuration exists without confirmed active use.
- `app/admin_api/__init__.py` exists, but no admin web API implementation was found.

### Not Built Yet / Planned

- No reliable product roadmap or root `TODO.md` was found.
- No active Mini App implementation was found.

### Unknown / Needs Testing

- Live Railway migration state and production environment configuration
- End-to-end payment screenshot and admin callback behavior in production
- Required-channel checks against real Telegram channel permissions
- Scheduled jobs with live database records
- Whether Redis or Airtable should remain supported

## H. Important Decisions

- Telegram is the main user interface.
- PostgreSQL is the intended source of truth.
- English QA is the active learning experience.
- Legacy Chinese HSK course code remains stored but disabled.
- Payment approval is manual; AI screenshot analysis assists admins only.
- Access control, discounts, referrals, and AI budgets are database-backed and must remain consistent.
- Subscription state is stored on users plus payment and budget records; there is no separate subscription table.
- Dynamic subscription prices are stored in the database with code fallbacks.

## I. Recent Important Changes

Recent Git history shows these durable changes:

- 2026-06-13: HSK AI bot mini app, HSK-style onboarding/course-trial structure, and related backend infrastructure were imported as the base for future English course mode. This added static Mini App pages (`hsk1.html`-`hsk4.html`, `study.html`, `stroke-order.html`, `subscription.html`), FastAPI Mini App endpoints, Telegram WebApp auth, Subscription Mini App checkout APIs, QR-specific payment support, partner program modules, onboarding tip events, and Alembic migrations `0028` through `0039`. `COURSE_MODE_ENABLED` remains `False`, course seeding stays skipped while disabled, new users start as `trial` with no temporary active subscription window, and `MINI_APP_BASE_URL` is now the deployment URL placeholder for Mini App WebApp links.
- 2026-06-13: English-facing texts for the imported onboarding/course scaffold were adjusted from HSK/Chinese to English learning copy. User-visible levels now show Beginner/A1/A2/B1/B2 while the internal scaffold can still map to legacy course levels; legacy CJK lesson material is filtered from English-facing lesson lists.
- English bot QA behavior replaced the former active course-first behavior.
- Course mode was disabled while preserving legacy files.
- Required-channel gating gained database management and pending-text resume.
- Admin ads, targeting, pricing controls, referral-discount progress, and feedback reply tooling were expanded.
- QA reminder menu behavior was restored after the English-bot transition.

## J. Known Problems / Risks

- `scripts/start.sh` can stamp Alembic head when revision detection or upgrade fails. This may hide schema drift.
- Runtime `create_all()` and bootstrap `ALTER TABLE` logic coexist with Alembic. Schema changes require review of both paths.
- `.env.example` and config defaults contain a non-empty admin identifier. Do not copy it into docs; confirm whether the example should be sanitized.
- `.env.example` omits `PAYMENT_DETAILS`, although Visa checkout reads it. Confirm deployment configuration before editing payment UI.
- FSM uses in-memory storage, so onboarding and admin interaction state can be lost on restart.
- Referral records are activated with status `active`, while an admin statistics query checks `activated`. Referral statistics may be inaccurate.
- Daily reset clears `bonus_questions_used`; accumulated bonus may become reusable each day. Confirm product intent before changing it.
- Unpaid image-limit handling shares and can reset question counters used by text access. Inspect carefully before modifying limits.
- Manual `/giveaccess` creates approved active access without the normal payment-backed AI budget path. Confirm intended complimentary behavior.
- User deletion should be reviewed before changes because some payment/referral history is keyed by Telegram ID rather than user foreign key.
- Legacy HSK code and English QA code coexist. Broad refactors can accidentally revive obsolete behavior.
- No automated test suite was found. Source syntax parsing passed during the 2026-06-02 inspection, but end-to-end behavior still needs manual verification.
- The generated graph report may be stale or include unrelated corpus entries. Verify important claims against source.

## K. Next Planned Work

- No authoritative `TODO.md` or code-backed roadmap was found.
- Confirm live migration state before the next schema change.
- Confirm intended semantics for bonus-question reset, unpaid image counters, and complimentary `/giveaccess`.
- Confirm whether inactive Airtable and Redis configuration should remain.

## L. Required Environment Variables

Document names only. Never write real values into memory files.

### Core Runtime

- `BOT_TOKEN=<telegram-bot-token>`
- `OPENAI_API_KEY=<openai-api-key>`
- `DATABASE_URL=<postgresql-asyncpg-url>`
- `ADMIN_IDS=<comma-separated-telegram-admin-ids>`
- `BOT_USERNAME=<telegram-bot-username>`
- `PAYMENT_DETAILS=<manual-payment-instructions>`
- `PORT=<runtime-port>`

### Configured Optional Or Defaulted

- `REDIS_URL=<redis-url>`
- `DEFAULT_LANGUAGE=<language-code>`
- `LOG_LEVEL=<log-level>`

### Legacy Airtable Service

- `AIRTABLE_API_KEY=<airtable-api-key>`
- `AIRTABLE_BASE_ID=<airtable-base-id>`
- `AIRTABLE_USERS_TABLE=<table-name>`
- `AIRTABLE_PAYMENTS_TABLE=<table-name>`
- `AIRTABLE_REFERRALS_TABLE=<table-name>`
- `AIRTABLE_CHAT_SUMMARY_TABLE=<table-name>`
- `AIRTABLE_CHAT_ARCHIVE_TABLE=<table-name>`

## M. AI Assistant Instructions

1. Read `AGENTS.md`, `AI_RULES.md`, this file, `MEMORY.md`, and affected source files before editing.
2. For architecture work, read `graphify-out/GRAPH_REPORT.md`, then verify important paths against source.
3. Preserve router order, scheduler behavior, database-backed access rules, and manual admin payment approval.
4. Before payment, subscription, access, referral, discount, or AI budget changes, trace handlers, services, models, migrations, and scheduled effects together.
5. Before AI prompt changes, inspect QA, image, voice, and legacy course behavior separately.
6. Keep course mode disabled unless the user explicitly requests a reviewed reactivation project.
7. Use Alembic for schema changes and inspect startup bootstrap compatibility.
8. Keep secrets out of output and memory. Use placeholders only.
9. Update this file only for durable changes that help a future assistant avoid breaking the system.
10. When evidence is missing, write `Unknown / needs confirmation` instead of guessing.
