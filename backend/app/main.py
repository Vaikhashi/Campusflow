from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta

from app.database import Base, engine, get_db
from app.models import User, Task, Club, Event
from app.schemas import (
    UserCreate,
    UserLogin,
    TaskCreate,
    TaskUpdate,
    ClubCreate,
    EventCreate,
    EventOut,
)
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    require_role,
    get_current_user,
)
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel


Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampusFlow API")


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"user_id": db_user.id, "role": db_user.role},
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": token}


@app.post("/clubs")
def create_club(
    club: ClubCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("PRINCIPAL")),
):
    new_club = Club(name=club.name)
    db.add(new_club)
    db.commit()
    return {"message": "Club created"}


@app.post("/events")
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("CLUB_ADMIN")),
):
    new_event = Event(
        title=event.title,
        date=event.date,
        club_id=event.club_id,
    )
    db.add(new_event)
    db.commit()
    return {"message": "Event created"}


@app.get("/events", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).all()


@app.post("/tasks")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("CLUB_ADMIN")),
):
    new_task = Task(
        title=task.title,
        deadline=task.deadline,
        event_id=task.event_id,
        assigned_to=task.assigned_to,
    )
    db.add(new_task)
    db.commit()
    return {"message": "Task created"}


@app.get("/my-tasks")
def get_my_tasks(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(Task).filter(Task.assigned_to == user["user_id"]).all()


@app.put("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.assigned_to != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    task.completed = True
    db.commit()
    return {"message": "Task marked as completed"}


@app.get("/principal/clubs")
def view_all_clubs(
    db: Session = Depends(get_db),
    user=Depends(require_role("PRINCIPAL")),
):
    return db.query(Club).all()


@app.get("/principal/events")
def view_all_events(
    db: Session = Depends(get_db),
    user=Depends(require_role("PRINCIPAL")),
):
    return db.query(Event).all()


@app.put("/events/{event_id}/complete")
def complete_event(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("CLUB_ADMIN")),
):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.status = "COMPLETED"
    db.commit()
    return {"message": "Event marked as completed"}


@app.get("/notifications/my-deadlines")
def my_upcoming_deadlines(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    today = date.today()
    next_week = today + timedelta(days=7)

    return db.query(Task).filter(
        Task.assigned_to == user["user_id"],
        Task.completed == False,
        Task.deadline <= next_week,
    ).all()


@app.get("/events/{event_id}/pending-tasks")
def pending_tasks_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("CLUB_ADMIN")),
):
    return db.query(Task).filter(
        Task.event_id == event_id,
        Task.completed == False,
    ).all()


@app.get("/notifications/upcoming-meetings")
def upcoming_meetings(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(Event).filter(
        Event.status == "PLANNED"
    ).all()


class TaskDeadlineUpdate(BaseModel):
    deadline: date


@app.put("/tasks/{task_id}/deadline")
def update_task_deadline(
    task_id: int,
    data: TaskDeadlineUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("CLUB_ADMIN")),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.deadline = data.deadline
    db.commit()
    return {"message": "Deadline updated"}


@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("CLUB_ADMIN")),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.title:
        task.title = data.title
    if data.assigned_to:
        task.assigned_to = data.assigned_to

    db.commit()
    return {"message": "Task updated"}


def check_deadlines(db: Session):
    today = date.today()
    tasks = db.query(Task).filter(
        Task.deadline == today,
        Task.completed == False,
    ).all()

    for task in tasks:
        task.notify = True

    db.commit()


@app.post("/system/run-deadline-check")
def run_deadline_check(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    background_tasks.add_task(check_deadlines, db)
    return {"message": "Deadline check started"}


@app.get("/notifications")
def get_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(Task).filter(
        Task.assigned_to == user["user_id"],
        Task.notify == True,
    ).all()


@app.get("/")
def root():
    return {"message": "Welcome to CampusFlow API"}
