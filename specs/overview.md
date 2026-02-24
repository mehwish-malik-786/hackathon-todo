# Hackathon Todo - Project Overview

## Project Vision

**Project Name**: Hackathon Todo  
**Theme**: Evolution of a Todo Application  
**Journey**: CLI → Full-Stack → AI Chatbot → Kubernetes → Cloud

---

## Executive Summary

Build a production-ready todo application that evolves through five phases, demonstrating modern software engineering practices with Python 3.13, Next.js, FastAPI, and cloud-native technologies.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.13, FastAPI |
| **Frontend** | Next.js (React) |
| **Database** | Neon PostgreSQL (serverless) |
| **ORM** | SQLModel |
| **AI/Chatbot** | OpenAI Agents SDK |
| **AI Integration** | MCP (Model Context Protocol) Tools |
| **Containerization** | Docker |
| **Orchestration** | Kubernetes |
| **Cloud Provider** | DigitalOcean |
| **Authentication** | JWT-based auth |

---

## Phase Evolution

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: Console Todo App                                      │
│  └─ Python CLI, JSON storage, CRUD operations                   │
│           ↓                                                     │
│  Phase 2: Full-Stack Web Todo                                   │
│  └─ FastAPI + Next.js, Neon PostgreSQL, JWT Auth                │
│           ↓                                                     │
│  Phase 3: AI Chatbot Todo                                       │
│  └─ OpenAI Agents SDK, MCP Tools, natural language interface    │
│           ↓                                                     │
│  Phase 4: Local Kubernetes Deployment                           │
│  └─ Docker containers, K8s manifests, local cluster             │
│           ↓                                                     │
│  Phase 5: Cloud Deployment                                      │
│  └─ DigitalOcean Kubernetes, CI/CD, production-ready            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Details

### Phase 1: Console Todo App
**Goal**: Core domain logic with CLI interface

| Aspect | Details |
|--------|---------|
| Language | Python 3.13 |
| Interface | Command-line (argparse/typer) |
| Storage | JSON file |
| Features | Create, Read, Update, Delete, List, Filter |

**Success Criteria**:
- [ ] All CRUD operations via CLI
- [ ] Data persists across sessions
- [ ] Unit tests passing (80%+ coverage)
- [ ] Clean architecture with repository pattern

---

### Phase 2: Full-Stack Web Todo
**Goal**: Web application with authentication

| Aspect | Details |
|--------|---------|
| Backend | FastAPI (Python 3.13) |
| Frontend | Next.js (React) |
| Database | Neon PostgreSQL |
| ORM | SQLModel |
| Auth | JWT tokens, password hashing |

**Features**:
- User registration and login
- Task CRUD via REST API
- Responsive web UI
- Protected routes

**Success Criteria**:
- [ ] Full CRUD via web UI
- [ ] Authentication working
- [ ] Database migrations functional
- [ ] API documented (OpenAPI)

---

### Phase 3: AI Chatbot Todo
**Goal**: Natural language todo management

| Aspect | Details |
|--------|---------|
| AI Framework | OpenAI Agents SDK |
| Integration | MCP (Model Context Protocol) Tools |
| Interface | Chat UI (web + CLI) |
| Features | NLP parsing, smart suggestions |

**Features**:
- Natural language task creation
- AI-powered task parsing
- Conversational interface
- Smart reminders and suggestions

**Success Criteria**:
- [ ] Natural language commands understood
- [ ] MCP tools integrated
- [ ] Chat interface functional
- [ ] AI suggestions accurate

---

### Phase 4: Local Kubernetes Deployment
**Goal**: Containerized deployment on local K8s

| Aspect | Details |
|--------|---------|
| Containers | Docker (multi-stage builds) |
| Orchestration | Kubernetes |
| Local Cluster | minikube / kind |
| Config | ConfigMaps, Secrets |

**Deliverables**:
- Dockerfiles for all services
- Kubernetes manifests (deployments, services, ingress)
- Health checks and probes
- Local deployment documentation

**Success Criteria**:
- [ ] All services containerized
- [ ] K8s manifests deploy successfully
- [ ] Health checks passing
- [ ] Services communicate correctly

---

### Phase 5: Cloud Deployment
**Goal**: Production deployment to DigitalOcean

| Aspect | Details |
|--------|---------|
| Cloud | DigitalOcean |
| K8s | DigitalOcean Kubernetes (DOKS) |
| Database | Neon PostgreSQL (cloud) |
| CI/CD | GitHub Actions |
| IaC | Terraform (optional) |

**Deliverables**:
- DigitalOcean Kubernetes cluster
- Container registry setup
- CI/CD pipeline
- Monitoring and logging
- Production URL live

**Success Criteria**:
- [ ] Automated deployment pipeline
- [ ] Production environment live
- [ ] Monitoring configured
- [ ] Auto-scaling enabled

---

## Core Features

### Task Management
- Create tasks with title, description, priority, due date
- Update task status (pending, in-progress, completed)
- Delete tasks
- Filter by status, priority, date
- Search tasks

### Authentication
- User registration with email/password
- Login with JWT tokens
- Password hashing (bcrypt)
- Protected API routes
- Session management

### AI Chatbot (via MCP Tools)
- Natural language task creation: "Remind me to call John tomorrow at 3pm"
- Task queries: "Show me my urgent tasks"
- Smart suggestions based on patterns
- Conversation history

---

## Architecture Overview

### Clean Architecture Layers

```
┌─────────────────────────────────────────────┐
│           Infrastructure Layer              │
│   (FastAPI, Next.js, PostgreSQL, Docker)    │
├─────────────────────────────────────────────┤
│           Application Layer                 │
│   (Use Cases, Services, DTOs, MCP Tools)    │
├─────────────────────────────────────────────┤
│             Domain Layer                    │
│   (Entities, Value Objects, Repositories)   │
└─────────────────────────────────────────────┘
```

### System Architecture (Phase 2+)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI   │────▶│   Neon      │
│   Frontend  │     │    Backend  │     │  PostgreSQL │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  OpenAI     │
                    │ Agents SDK  │
                    │  + MCP      │
                    └─────────────┘
```

---

## Quality Standards

### Testing Strategy

| Test Type | Coverage | Tools |
|-----------|----------|-------|
| Unit | Domain logic | pytest |
| Integration | API, DB | pytest + httpx |
| E2E | User workflows | Playwright |
| Contract | MCP tools | Custom |

### Code Quality
- **Linting**: ruff (Python), ESLint (TypeScript)
- **Formatting**: black (Python), Prettier (TypeScript)
- **Type Safety**: mypy (Python), TypeScript
- **Coverage**: Minimum 80%

### Documentation
- README for each phase
- API documentation (FastAPI auto-generated OpenAPI)
- Architecture Decision Records (ADRs)
- Inline code comments for complex logic

---

## Development Workflow

### Spec-Driven Development Process

1. **Spec Creation** → Define requirements, interfaces, acceptance criteria
2. **Spec Review** → Validate completeness and testability
3. **Plan/Architecture** → Design solution, create ADRs
4. **Tasks** → Break down into testable tasks
5. **Implementation** → AI-generated code (Qwen Code / Claude Code)
6. **Testing** → All tests must pass
7. **Documentation** → Update docs and PHR

### Git Strategy

```
main ────────────────────────────────────────────►
       \         \         \         \
    feature/  feature/  feature/  feature/
     phase1    phase2    phase3    phase4-5
```

### Branch Naming Convention
- `feature/phase-<n>-<description>`
- `fix/<issue-description>`
- `docs/<documentation-update>`
- `chore/<maintenance-task>`

---

## Project Structure

```
hackathon-todo/
├── specs/                    # Specifications
│   ├── constitution.md       # Project constitution
│   ├── overview.md           # This file
│   ├── phase-1-cli/          # Phase 1 specs
│   ├── phase-2-web/          # Phase 2 specs
│   ├── phase-3-ai/           # Phase 3 specs
│   ├── phase-4-k8s/          # Phase 4 specs
│   └── phase-5-cloud/        # Phase 5 specs
├── src/                      # Source code (per phase)
├── tests/                    # Tests (per phase)
├── history/                  # Project history
│   ├── prompts/              # Prompt History Records (PHRs)
│   └── adr/                  # Architecture Decision Records
├── infra/                    # Infrastructure code
│   ├── docker/               # Dockerfiles
│   ├── k8s/                  # Kubernetes manifests
│   └── terraform/            # Terraform configs
└── docs/                     # Documentation
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test Coverage | ≥80% |
| API Response Time (p95) | <200ms |
| Build Time | <5 minutes |
| Deployment Time | <10 minutes |
| Uptime (Phase 5) | 99.9% |

---

## Risk Management

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Strict phase boundaries, MVP focus |
| AI code quality | Medium | Human review, comprehensive tests |
| Cloud costs | Low | Use free tiers, set budgets |
| Time constraints | High | Prioritize core features |
| API rate limits | Medium | Caching, request batching |

---

## Deliverables Summary

| Phase | Deliverables |
|-------|-------------|
| **Phase 1** | CLI app, JSON storage, unit tests |
| **Phase 2** | FastAPI backend, Next.js frontend, Neon DB, auth, E2E tests |
| **Phase 3** | OpenAI Agents SDK, MCP tools, chat interface |
| **Phase 4** | Docker containers, K8s manifests, local deployment |
| **Phase 5** | DigitalOcean deployment, CI/CD, monitoring |

---

## References

| Document | Path |
|----------|------|
| Constitution | `specs/constitution.md` |
| Phase Specs | `specs/phase-*/spec.md` |
| Architecture Plans | `specs/phase-*/plan.md` |
| Task Lists | `specs/phase-*/tasks.md` |
| ADRs | `history/adr/` |
| PHRs | `history/prompts/` |

---

**Version**: 1.0.0  
**Created**: 2026-02-24  
**Status**: Active  
**Next Review**: After Phase 1 completion
