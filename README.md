# AI Job Assistant

Full-stack **job application tracker** with AI-powered resume tailoring and cover letter generation.

Built for mid-level full-stack interviews. Combines classic CRUD product features with practical LLM integration.

---

## Features

- [x] User authentication (JWT)
- [x] Job applications tracker (company, role, status, notes, dates)
- [x] Status pipeline: wishlist → applied → interview → offer → rejected
- [x] Master resume / profile text storage
- [x] AI-generated tailored resume bullet points for a job description
- [x] AI-generated cover letter draft
- [x] Docker Compose + Postgres
- [x] FastAPI backend with clean service layer
- [ ] Next.js frontend UI (scaffold ready)
- [ ] Interview question prep generation (easy extension)

---

## Tech Stack

| Layer    | Technology                         |
|----------|------------------------------------|
| Backend  | FastAPI + Python 3.11+             |
| AI       | OpenAI API (chat models)           |
| Database | PostgreSQL + SQLAlchemy            |
| Auth     | JWT                                |
| Frontend | Next.js 15 + TypeScript (scaffold) |
| Infra    | Docker Compose                     |

---

## Architecture

```
User → Next.js Frontend
         ↓
      FastAPI Backend
         ├── Auth
         ├── Applications (CRUD + status)
         ├── Profile / master resume
         └── AI service (tailor resume, cover letter)
         ↓
      PostgreSQL + OpenAI
```

---

## API Overview

| Method | Endpoint                              | Description                    |
|--------|---------------------------------------|--------------------------------|
| POST   | `/api/v1/auth/register`               | Register                       |
| POST   | `/api/v1/auth/login`                  | Login                          |
| GET    | `/api/v1/auth/me`                     | Current user                   |
| GET    | `/api/v1/applications/`               | List applications              |
| POST   | `/api/v1/applications/`               | Create application             |
| PATCH  | `/api/v1/applications/{id}`           | Update application             |
| DELETE | `/api/v1/applications/{id}`           | Delete application             |
| GET    | `/api/v1/profile/`                    | Get master resume/profile      |
| PUT    | `/api/v1/profile/`                    | Upsert master resume           |
| POST   | `/api/v1/ai/tailor-resume`            | AI-tailored bullets for a JD   |
| POST   | `/api/v1/ai/cover-letter`             | AI cover letter draft          |

---

## Getting Started

```bash
git clone https://github.com/Invenitur42/ai-job-assistant.git
cd ai-job-assistant
docker-compose up -d

cd backend
cp .env.example .env   # set OPENAI_API_KEY + SECRET_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

---

## Interview Talking Points

- Separating deterministic product logic (tracker) from probabilistic AI features
- Prompt design for grounded, useful resume/cover letter output
- Storing a master profile once and reusing it across many applications
- Status workflow modeling for job pipelines
- How you would add rate limiting and cost controls for OpenAI calls

---

Part of the [AI Tools Portfolio](https://github.com/Invenitur42/ai-tools-portfolio).