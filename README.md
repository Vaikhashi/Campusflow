# CampusFlow

A small app for running college clubs. Club admins create events and hand out tasks, members see what's due, and the principal can see every club and event in one place.

Backend is FastAPI with SQLAlchemy. Frontend is React (Vite).

## What it does

- Sign up and log in with a JWT. Every request carries a role: `CLUB_ADMIN`, `MEMBER` or `PRINCIPAL`.
- Club admins create events, assign tasks with deadlines, and mark events as completed.
- Members see their tasks, tick them off, and get a list of deadlines due in the next 7 days.
- The principal gets read-only views of all clubs and events.
- `POST /system/run-deadline-check` flags tasks due today as a background task.

## Main endpoints

| Method | Path | Who |
| --- | --- | --- |
| POST | `/register`, `/login` | anyone |
| POST | `/events`, `/tasks` | club admin |
| PUT | `/events/{id}/complete` | club admin |
| GET | `/my-tasks`, `/notifications/my-deadlines` | logged in |
| PUT | `/tasks/{id}/complete` | the member it's assigned to |
| GET | `/principal/clubs`, `/principal/events` | principal |

## Running it

Backend:

```bash
cd backend
pip install fastapi uvicorn sqlalchemy python-dotenv passlib[bcrypt] python-jose
# .env needs DATABASE_URL and SECRET_KEY, e.g.
# DATABASE_URL=sqlite:///./campusflow.db
uvicorn app.main:app --reload
```

Frontend (expects the API on `http://127.0.0.1:8000`):

```bash
npm install
npm run dev
```

## Still to do

- The React side only has the login page and an events dashboard so far.
- Add a `requirements.txt` and tests.
