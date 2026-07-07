from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_service.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_service.update_user(db=db, db_user=db_user, user_update=user_update)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.delete_user(db=db, db_user=db_user)
    return {"detail": "User deleted"}

@router.get("/", response_model=UserListResponse)
def read_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total, items = user_service.get_user_list(db, skip=skip, limit=limit)
    return {"total": total, "items": items}
