# PROJECT_MEMORY.md

## 1. Project Identity

Project name: Unknown / needs inspection  
Project type: Telegram Bot / Mini App / Website / Backend / Other  
Main purpose: Unknown / needs inspection  
Target users: Unknown / needs inspection  
Current status: Unknown / needs inspection  

Short description:
- This project is built to: Unknown / needs inspection
- Main user problem: Unknown / needs inspection
- Main business goal: Unknown / needs inspection

---

## 2. Core Architecture

Frontend:
- Unknown / needs inspection

Backend:
- Unknown / needs inspection

Database:
- Unknown / needs inspection

Hosting:
- Unknown / needs inspection

Bot framework:
- Unknown / needs inspection

AI provider/model:
- Unknown / needs inspection

Payment system:
- Unknown / needs inspection

External services:
- Unknown / needs inspection

---

## 3. Important Project Rules

- Do not redesign the whole architecture without explicit request.
- Do not remove working logic unless there is a clear reason.
- Make minimal safe changes.
- Keep user/payment/subscription logic stable.
- If database schema changes, document the migration.
- If environment variables change, update `.env.example`.
- Never write secrets, API keys, tokens, passwords, or private URLs in this file.
- Before changing payment, subscription, or access logic, check the current flow first.
- If something is unclear, inspect the code first instead of guessing.

---

## 4. Memory Update Policy

This file is NOT a daily diary and must NOT become a dump of every small change.

Only update this file when the change is important for future AI assistants to understand, debug, or safely continue the project.

Update this file only for:
- Architecture changes
- Database schema changes
- Payment logic changes
- Subscription logic changes
- User access logic changes
- Important user flow changes
- Deployment or environment changes
- AI prompt behavior changes
- Course or lesson logic changes
- Important business logic decisions
- Major bug fixes
- Security-sensitive changes

Do NOT update this file for:
- Small text edits
- Emoji changes
- Typo fixes
- Minor UI/CSS changes
- Console log cleanup
- Small refactoring with no logic change
- Temporary experiments
- Changes already obvious from the code

Before updating memory, ask internally:

> Will this help another AI assistant understand, debug, or safely continue this project later?

If the answer is no, do not update this file.

When updating memory, keep it short and useful:
- What changed
- Why it changed
- Files touched
- Risk / follow-up if needed

Never turn this file into a long changelog.

---

## 5. Key Files and Folders

Main files:
- `main.py` — Unknown / needs inspection
- `bot.py` — Unknown / needs inspection
- `database.py` — Unknown / needs inspection
- `config.py` — Unknown / needs inspection
- `handlers/` — Unknown / needs inspection
- `keyboards/` — Unknown / needs inspection
- `services/` — Unknown / needs inspection
- `miniapp/` — Unknown / needs inspection
- `.env.example` — Unknown / needs inspection

Important note:
- Do not rename or delete important files unless necessary.

---

## 6. Database Schema Summary

### users
Purpose: stores Telegram users and access status.

Important fields:
- `telegram_id`
- `language`
- `status`
- `payment_status`
- `subscription_until`
- `question_limit`
- `questions_used`

### payments
Purpose: stores payment requests and confirmations.

Important fields:
- `payment_id`
- `telegram_id`
- `amount`
- `payment_code`
- `status`
- `created_at`
- `confirmed_at`

### logs / history
Purpose: stores important user actions or AI interactions.

Important fields:
- Unknown / needs inspection

---

## 7. Current Business Logic

### User onboarding
Current flow:
1. Unknown / needs inspection

### Subscription logic
Current logic:
- Free trial: Unknown / needs inspection
- Paid plans: Unknown / needs inspection
- Question limits: Unknown / needs inspection
- Expiration logic: Unknown / needs inspection
- Access blocked when: Unknown / needs inspection

### Payment logic
Current logic:
- Payment method: Unknown / needs inspection
- Manual approval: Unknown / needs inspection
- Auto approval: Unknown / needs inspection
- Admin notification: Unknown / needs inspection

### AI logic
Current logic:
- Unknown / needs inspection

---

## 8. Current Features

Working:
- Unknown / needs inspection

Partially working:
- Unknown / needs inspection

Not built yet:
- Unknown / needs inspection

---

## 9. Important Decisions

### Decision 1
Date: Unknown  
Decision: Unknown / needs inspection  
Reason: Unknown / needs inspection  
Risk: Unknown / needs inspection  

---

## 10. Recent Important Changes

### YYYY-MM-DD — Change title

Changed:
- 

Why:
- 

Files touched:
- 

Risk:
- 

Follow-up:
- 

---

## 11. Known Problems

### Problem 1
Problem:
- Unknown / needs inspection

Suspected cause:
- Unknown / needs inspection

Status:
- Open / Fixed / Needs testing

---

## 12. Next Planned Work

Priority 1:
- Unknown / needs inspection

Priority 2:
- Unknown / needs inspection

Priority 3:
- Unknown / needs inspection

---

## 13. Required Environment Variables

Do not write real values here.

Required:
- `BOT_TOKEN`
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `ADMIN_IDS`

Optional:
- Unknown / needs inspection

---

## 14. AI Assistant Instructions

Any AI coding assistant working on this project must:

1. Read this file before changing code.
2. Understand the current architecture before editing.
3. Make minimal changes.
4. Preserve working flows.
5. Never store secrets in this file.
6. Update this file only after important changes.
7. Do not write small cosmetic changes here.
8. If changing database/payment/subscription logic, explain the risk.
9. If unsure, inspect the code before guessing.
10. Do not rewrite this file completely unless explicitly requested.
