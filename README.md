**FastAPI Practice Plan: From Basics to Advanced (4-Week Progressive Roadmap)**

This is a **daily, hands-on practice plan** designed to take you from zero to advanced FastAPI skills. It assumes you already know basic Python. Plan for **1–2 hours per day** (30–45 min learning + 45–75 min coding). Consistency beats intensity — code **every single day**.

You’ll build **one main project** across all weeks (a full-featured **Task Management API** with users, tasks, teams, file uploads, and real-time notifications) while doing small daily exercises. Track everything in a GitHub repo (commit daily!).

### Prerequisites (Do this on Day 0 – 30 minutes)
- Python 3.11+
- Install: `pip install fastapi uvicorn pydantic[email] python-multipart`
- Editor: VS Code + Python extension + Black + Ruff
- Testing tool: HTTPie (`pip install httpie`) or Postman/Insomnia
- Run server: `uvicorn main:app --reload`

---

### **Week 1: FastAPI Fundamentals (Basics)**
**Goal**: Build a working API with routes, parameters, and responses.

| Day | What to Practice | Daily Task (Code This) |
|-----|------------------|------------------------|
| 1   | Setup & First Endpoint | Create `main.py` with `/` and `/health` GET endpoints. Return JSON + status codes. |
| 2   | Path & Query Parameters | `/tasks/{task_id}` (path) and `/tasks/?status=pending&limit=10` (query). Add validation (`gt`, `le`). |
| 3   | Request Body + Pydantic Models | POST `/tasks/` with `TaskCreate` model. Use `response_model`. |
| 4   | Response Models & Status Codes | Separate `TaskRead` model. Use `status.HTTP_201_CREATED`. |
| 5   | Error Handling | Custom `HTTPException` + global exception handler for `RequestValidationError`. |
| 6   | Mini Project Day | Build a full CRUD for Tasks **without database** (store in a Python list/dict). |
| 7   | Review & Deploy Locally | Add OpenAPI docs customisation (`title`, `version`, `docs_url`). Test everything with HTTPie. Push to GitHub. |

**Resources**: Official Tutorial (first 5 sections) → https://fastapi.tiangolo.com/tutorial/

---

### **Week 2: Data Validation, Dependencies & Middleware (Intermediate)**
**Goal**: Clean, reusable, production-ready code.

| Day | What to Practice | Daily Task |
|-----|------------------|----------|
| 8   | Advanced Pydantic (v2) | Field constraints, `model_validator`, `computed_field`, ConfigDict. |
| 9   | Dependencies (simple) | Create `get_current_user` dependency (fake user for now). |
| 10  | Dependency Injection + Security | Use `Depends()` on multiple routes. Add `Header()` and `Cookie()`. |
| 11  | Middleware | Add CORS, GZip, and a custom logging middleware. |
| 12  | Background Tasks & File Uploads | POST `/tasks/{id}/upload` with `UploadFile` + background task to "process" file. |
| 13  | WebSockets (Intro) | `/ws/tasks` endpoint that broadcasts new tasks. |
| 14  | Mini Project Day | Refactor Week 1 CRUD to use dependencies + file upload for task attachments. |

**Pro Tip**: Use `Annotated` everywhere (FastAPI v0.100+ style).

---

### **Week 3: Databases & ORM (Core Backend Skills)**
**Goal**: Persistent data with best practices.

| Day | What to Practice | Daily Task |
|-----|------------------|----------|
| 15  | SQLModel (recommended) or SQLAlchemy 2.0 | Set up SQLModel + SQLite. Create `Task` and `User` models. |
| 16  | CRUD with Database | Full async CRUD using `SessionDep` dependency. |
| 17  | Relationships & Migrations | One-to-many (User ↔ Tasks) + Alembic migrations. |
| 18  | PostgreSQL + Docker | Switch to PostgreSQL in Docker Compose. |
| 19  | Advanced Queries | Filtering, pagination, search with SQLModel. |
| 20  | Async Database (full async) | Use `async` routes + `asyncpg`/`async_session`. |
| 21  | Mini Project Day | Add Users + Tasks relationship to your main project. |

**Alternative**: If you prefer Tortoise-ORM or Prisma, swap SQLModel — but SQLModel is fastest to learn.

---

### **Week 4: Authentication, Testing & Production (Advanced)**
**Goal**: Secure, testable, deployable API.

| Day | What to Practice | Daily Task |
|-----|------------------|----------|
| 22  | JWT Authentication | OAuth2PasswordBearer + JWT (PyJWT or python-jose). |
| 23  | Password Hashing + User Registration | Use `passlib` + `bcrypt`. Protected routes. |
| 24  | Role-based Access | Dependency that checks admin/user roles. |
| 25  | Testing (pytest + TestClient) | Write 15+ tests: CRUD, auth, errors, file upload. |
| 26  | Advanced Testing | Mock database + factory-boy or pytest-factoryboy. |
| 27  | Deployment Prep | Dockerize the app + Docker Compose (app + postgres + redis). |
| 28  | Production Features | Rate limiting (slowapi), logging (structlog), environment variables (pydantic-settings). |
| 29–30 | Full Project Polish + Deployment | Add background tasks, WebSocket notifications, email (optional). Deploy free on **Railway**, **Render**, or **Fly.io**. |

**Bonus Advanced Topics** (Continue after Week 4 – 1 topic per day):
- Celery + Redis for heavy background jobs
- GraphQL with Strawberry + FastAPI
- Server-Sent Events (SSE)
- OpenAPI custom security schemes + automatic docs
- Performance: Uvicorn workers, Gunicorn, or Hypercorn
- Monitoring: Prometheus + Grafana
- CI/CD: GitHub Actions

---

### Daily Routine (Copy-Paste This)
1. **10 min** – Review yesterday’s code.
2. **30–40 min** – Read the exact section in official docs + watch 1 short video if needed.
3. **45–60 min** – Code the daily task **from scratch** (no copy-paste).
4. **10 min** – Test with HTTPie/Postman + commit to GitHub with good message.
5. **Weekend** – Refactor or add one extra feature to the main project.

