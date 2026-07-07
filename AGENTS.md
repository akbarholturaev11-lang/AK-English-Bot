# AGENTS.md

## Owner Preferences

- Owner: Akbar.
- Answer language: Uzbek (lotin).
- Code language: English.
- Be concise, practical, and direct. Recommend the strongest path instead of listing many options.
- Preserve working behavior. Do not add unnecessary abstractions or redesign the project without an explicit request.

## Required Reading

Before editing application code:

1. Read `AGENTS.md`, `AI_RULES.md`, and `PROJECT_MEMORY.md`.
2. Read `MEMORY.md`, `TODO.md`, and `memory/YYYY-MM-DD.md` if they exist.
3. Read `graphify-out/GRAPH_REPORT.md` before architecture or codebase questions.
4. Inspect the relevant active source files. Do not treat `*.bak*`, `*.save`, `.claude/worktrees/`, or the vendored `graphify/` project as active application code.

Canonical files use these exact names:

- `AGENTS.md`
- `AI_RULES.md`
- `PROJECT_MEMORY.md`

Files with names ending in `— копия.md` are historical copies. Do not use them as the source of truth.

## Project Context

This is the `AK English Bot` / `English AI` Telegram learning bot.

- Main interface: Telegram bot built with `aiogram`.
- Runtime wrapper: FastAPI with `/health`, polling, and a background scheduler.
- Database: PostgreSQL through async SQLAlchemy and Alembic.
- Primary active learning flow: English QA, image-text explanation, and paid voice features.
- Supported UI languages: `tj`, `ru`, `uz`.
- Legacy HSK/Chinese course code and seeds remain in the repository, but `COURSE_MODE_ENABLED = False` in `app/config.py`. Do not enable or rewrite the course system casually.

## High-Risk Logic

Inspect all connected files before changing any of these areas:

- Access and limits: `app/services/access_service.py`, `app/repositories/user_repo.py`, `app/services/daily_reset_service.py`, `app/services/ai_usage_budget_service.py`
- Payments and activation: `app/bot/handlers/subscription.py`, `app/bot/handlers/payments.py`, `app/bot/handlers/admin_payments.py`, `app/services/payment_service.py`, `app/services/subscription_service.py`
- Referrals and discounts: `app/services/referral_service.py`, `app/services/discount_service.py`, `app/bot/handlers/admin_discount.py`
- AI behavior: `app/prompts/qa_system.txt`, `app/services/ai_service.py`, `app/services/qa_service.py`, `app/services/image_input_service.py`, and voice handling in `app/bot/handlers/messages.py`
- Screenshot review: `app/services/payment_screenshot_ai_service.py` is advisory only; it must not activate subscriptions
- Course and reminders: `app/config.py`, `app/bot/handlers/course.py`, `app/bot/handlers/menu.py`, `app/services/course_*`
- Database lifecycle: `alembic/versions/`, `alembic/env.py`, `app/db/models/`, `app/db/session.py`, `scripts/start.sh`

Payment screenshot AI is advisory only. Never turn it into automatic approval without an explicit product decision. Paid activation currently happens after admin approval.

## Change Rules

- Make the smallest safe change.
- Preserve the existing project style. Inspect existing code before adding a new file or abstraction.
- Keep handler ordering in `app/bot/create_bot.py`; admin FSM routers must stay before generic photo/text handlers.
- Preserve the separation between QA access, trial limits, paid AI budgets, referral bonuses, discount eligibility, and manual payment approval.
- Add an Alembic migration for schema changes. Update models and inspect `app/db/session.py` bootstrap compatibility logic. Do not rely on `create_all()` to alter existing tables.
- Inspect `scripts/start.sh` before migration work: its fallback stamping can conceal schema drift.
- Do not run database reset, delete, downgrade, stamp, or destructive scripts without explicit approval.
- Do not read, print, commit, or document secrets from `.env`.
- If env names change, update `.env.example` with empty placeholders only.

## Engineering Discipline

- For Telegram changes, inspect handler order, FSM state, callback clarity, database consistency, anti-spam behavior, admin tooling, payments, and subscriptions.
- For AI changes, inspect token cost, fallback behavior, timeout handling, logging, and abuse protection.
- When the owner says `davom et`, inspect the previous state and continue from the stopping point instead of restarting.
- If Git is used, keep commits small, preserve a working state, and use clear `feat:`, `fix:`, `refactor:`, or `docs:` messages.
- For repeated bugs, add a durable lesson under `knowledge/bugs/` if that folder exists and the note will prevent recurrence.

## Verification

Before finishing code changes:

1. Run syntax/import checks for touched Python modules.
2. Run focused tests if available. This repository currently has no application test suite, so report that limitation.
3. Review side effects across access, payment, subscription, referral, discounts, reminders, and admin handlers when relevant.
4. If application code changed, run `graphify update .` when the local graphify runtime is available.
5. Review `git diff --stat` and `git diff -- <touched files>`.

## Memory Discipline

`PROJECT_MEMORY.md` is long-term project memory, not a diary.

Update it only when a change affects architecture, schema, payment/subscription/access rules, AI prompt behavior, course logic, deployment, env variables, major bug fixes, or security-sensitive behavior.

Before adding a note, ask:

> Will this help another AI assistant understand, debug, or safely continue this project later?

Do not record cosmetic UI edits, typo fixes, emoji changes, minor CSS changes, console cleanup, temporary experiments, secrets, or a dump of Git history.

## Bug Fix Format

When reporting a bug fix, use:

- Sabab:
- Fix:
- Risk:
- Prevention:

## Security

- Never expose bot tokens, API keys, passwords, real database URLs, private links, payment credentials, webhook secrets, or private admin data.
- Keep `.env` out of Git.
- Ask for confirmation before destructive actions.
- Run syntax/import checks before deploy-related work.

## graphify

This project has a graphify knowledge graph at `graphify-out/`.

- Read `graphify-out/GRAPH_REPORT.md` for architecture questions.
- If `graphify-out/wiki/index.md` exists, navigate it before raw scanning.
- Prefer `graphify query`, `graphify path`, or `graphify explain` for cross-module questions when the local graphify runtime works.
- After application code changes, run `graphify update .` when available.
