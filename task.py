from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User, Task
from app.scahmes import CreateUser, UpdateUser, UpdateTask, CreateTask
from sqlalchemy import insert, select, update, delete
import slugify

router = APIRouter(prefix="/task", tags=["task"])

@router.get("/all_users")
async def all_tasks(db: Annotated[Session, Depends(get_db())]):
    tasks_query = db.scalars(select(Task))
    return [task for task in tasks_query.all]


@router.get("/user_id/{user_id}")
async def task_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    task_query = db.execute(select(Task).where(Task.id == user_id)).scalar_one_or_none()
    if task_query is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    return task_query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_task(create_task: CreateTask, user_id: int, db: Annotated[Session, Depends(get_db)]):
    # Ищем пользователя по user_id
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # Если пользователь не найден, выбрасываем исключение
        raise HTTPException(status_code=404, detail="User was not found")

    new_task = Task(
        taskname=create_task.taskname,
        firstname=create_task.firstname,
        lastname=create_task.lastname,
        age=create_task.age,
        title=create_task.title,
        description=create_task.description,
        user_id=user_id, # Связываем рагудую задачу с пользователем
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    except Exception as e:
        # Обработка возможных исключений, например, уникальности поля taskname
        print(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {e}")



@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
async def update_task(task_id: int, update_task: UpdateTask, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.query(Task).filter(Task.id == task_id).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    existing_user.username = update_task.username
    existing_user.firstname = update_task.firstname
    existing_user.lastname = update_task.lastname
    existing_user.age = update_task.age

    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "Task update is successful!"}


@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_task = db.query(Task).filter(Task.id == task_id).first()

    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task was not found")

    db.delete(existing_task)
    db.commit()

    return {"status_code": status.HTTP_204_NO_CONTENT, "transaction": "Task deleted successfully!"}