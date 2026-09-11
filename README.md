# HIQ Application Assistant

Track job applications and generate a tailored resume bullets / cover letter draft from a master profile and a job description.

**FastAPI · Postgres · OpenAI**

(UI scaffold only for now; API is usable via `/docs`.)

---

## What you can do

- Register / login
- CRUD applications (company, role, status, notes, dates)
- Statuses: wishlist → applied → interview → offer → rejected
- Store a master resume / profile text
- `POST /ai/tailor-resume` and `POST /ai/cover-letter` using that profile + a JD

---

## Run

```bash
git clone https://github.com/Invenitur42/HIQ_Aplication_assistant.git
cd HIQ_Aplication_assistant
docker compose up -d

cd backend
cp .env.example .env   # OPENAI_API_KEY, SECRET_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

## Layout

Tracker logic is normal CRUD. AI calls sit in a separate service so prompts stay in one place. You save the profile once and reuse it across applications.

Later: full UI, interview question helpers, and basic rate limits on OpenAI routes.
