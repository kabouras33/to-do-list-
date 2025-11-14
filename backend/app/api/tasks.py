from fastapi import APIRouter, HTTPException, Depends, status, WebSocket
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from .database import get_db
from .models import Task
from .schemas import TaskCreate, TaskUpdate, TaskResponse
from .crud import create_task, get_task, get_tasks, update_task, delete_task
from .auth import get_current_user
from .websockets import manager

router = APIRouter()

@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(task: TaskCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    try:
        new_task = create_task(db=db, task=task, user_id=current_user.id)
        await manager.broadcast({"event": "task_created", "task": new_task})
        return new_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/", response_model=List[TaskResponse])
async def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    try:
        tasks = get_tasks(db=db, user_id=current_user.id, skip=skip, limit=limit)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    task = get_task(db=db, task_id=task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_existing_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    try:
        updated_task = update_task(db=db, task_id=task_id, task=task, user_id=current_user.id)
        await manager.broadcast({"event": "task_updated", "task": updated_task})
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(task_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    try:
        delete_task(db=db, task_id=task_id, user_id=current_user.id)
        await manager.broadcast({"event": "task_deleted", "task_id": task_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket, current_user: int = Depends(get_current_user)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)