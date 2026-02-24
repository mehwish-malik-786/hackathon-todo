---
id: 007
title: Add Constitution Principles
stage: constitution
date: 2026-02-24
surface: agent
model: qwen-code
feature: constitution
branch: master
user: mehwish
command: Add principles to constitution: Clean Architecture, Spec-Driven Development, No manual DB queries, Tests required, Env secrets hidden
labels: ["constitution", "principles", "governance"]
links:
  spec: specs/constitution.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

Add principles:
- Clean Architecture
- Spec-Driven Development
- No manual DB queries
- Tests required
- Env secrets hidden

## Response snapshot

Updated specs/constitution.md with 2 new principles:

**Principle 9: No Manual Database Queries**
- All DB access through repository layer
- Use ORM (SQLModel/SQLAlchemy) for queries
- No raw SQL in application code
- Database migrations version-controlled

**Principle 10: Environment Secrets Hidden**
- Secrets stored in .env files only
- Never commit .env to version control
- Use environment variables in code
- .env files listed in .gitignore

Existing principles already covered:
- Clean Architecture (Principle 4)
- Spec-Driven Development (Principle 1)
- Tests for Every Feature (Principle 6)

## Outcome

- ✅ Impact: Constitution now has 10 core principles covering architecture, security, and development practices
- 🧪 Tests: N/A (constitution document)
- 📁 Files: specs/constitution.md (updated)
- 🔁 Next prompts: Continue with Phase-II backend implementation
- 🧠 Reflection: Principles align with project goals and industry best practices

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase-II backend spec
