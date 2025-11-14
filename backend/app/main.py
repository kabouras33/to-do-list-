from fastapi import FastAPI, HTTPException, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import List
from .database import SessionLocal, engine, Base
from .models import User, Task
from .schemas import UserCreate, TaskCreate, TaskUpdate
from .crud import get_user_by_username, create_user, get_tasks, create_task, update_task, delete_task
from .auth import authenticate_user, create_access_token, get_current_user
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

Base.metadata.create_all(bind=engine)

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserCreate)
async def create_new_user(user: UserCreate, db: Session = Depends(SessionLocal)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)

@app.get("/tasks/", response_model=List[TaskCreate])
async def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    tasks = get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.post("/tasks/", response_model=TaskCreate)
async def create_new_task(task: TaskCreate, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    return create_task(db=db, task=task)

@app.put("/tasks/{task_id}", response_model=TaskUpdate)
async def update_existing_task(task_id: int, task: TaskUpdate, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    db_task = update_task(db=db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/tasks/{task_id}")
async def delete_existing_task(task_id: int, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    db_task = delete_task(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted successfully"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()