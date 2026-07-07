# AI_RULES.md

## Mandatory Read Order

Before changing application code, read:

1. `AGENTS.md`
2. `PROJECT_MEMORY.md`
3. `MEMORY.md`
4. `graphify-out/GRAPH_REPORT.md` for architecture or cross-module work
5. The affected source files, related migrations, and callers

Only the exact root filenames above are canonical. Files with names such as `* — копия.md` are legacy snapshots and must not replace the canonical files.

## Safe Scope

- Make minimal, targeted changes. Preserve existing architecture and working flows.
- Do not redesign the project or enable dormant features unless explicitly requested.
- Do not change unrelated files, generated files, or user edits.
- Do not add dependencies unless the user explicitly requests and approves them.
- If behavior is uncertain after inspection, write `Unknown / needs confirmation` and ask before changing it.

## Critical Business Logic

- Treat PostgreSQL as the source of truth. Inspect models, migrations, repository methods, and scheduler effects before changing persisted behavior.
- Do not change payment, subscription, access, trial, AI budget, referral, discount, or forced-channel logic without tracing the full flow.
- Payment screenshots are reviewed manually by admins. Screenshot AI analysis is advisory only and must never auto-approve a payment.
- Normal screenshot-payment activation updates user access fields and creates payment-backed AI budget records. Preserve this relationship. `/giveaccess` is an existing manual exception and must be reviewed separately.
- Subscription prices can be overridden in the database. Do not hardcode a UI-only price change.
- `COURSE_MODE_ENABLED` is intentionally `False`. Legacy HSK course code remains in the repository. Do not enable it by flipping the flag alone.
- Router order matters: admin FSM handlers and payment screenshot routing must remain ahead of the generic message handler.

## Database Rules

- Use Alembic for schema changes. Add a migration and inspect compatibility with existing Railway databases.
- Review `app/db/session.py` before schema work: startup also calls `Base.metadata.create_all()` and applies legacy bootstrap `ALTER TABLE` statements.
- Do not stamp, reset, delete, or rewrite database history without explicit approval.
- Do not delete production data or run destructive database commands without explicit approval.

## Environment And Secrets

- Never read, print, copy, commit, or document real values from `.env`.
- Never store bot tokens, API keys, admin identifiers, payment credentials, private links, passwords, or real `DATABASE_URL` values in project memory.
- Document environment variables by name and placeholder only.
- Treat non-empty example defaults as sensitive until confirmed safe for public use.

## Memory Discipline

Update `PROJECT_MEMORY.md` only when a change affects architecture, schema, access, payments, subscriptions, AI behavior, course behavior, important deployment behavior, or a durable risk.

Do not add cosmetic edits, typo fixes, minor CSS changes, temporary experiments, console cleanup, or diary-style progress notes.

## Verification

- Run syntax/import checks appropriate to the changed scope.
- For code changes, update the knowledge graph with `graphify update .` when the local graphify environment is available.
- Re-read the final diff and verify that no secret or unrelated change was included.

## Never Do

- Do not expose secrets.
- Do not silently alter payment approval or access rules.
- Do not bypass migrations with ad hoc production SQL.
- Do not revive legacy Chinese course flows as English course functionality without a product and data review.
- Do not delete, rename, or rewrite unrelated files.
