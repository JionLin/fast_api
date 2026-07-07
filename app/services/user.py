from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id, User.deleted == 0).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username, User.deleted == 0).first()

def get_user_list(db: Session, skip: int = 0, limit: int = 10):
    query = db.query(User).filter(User.deleted == 0)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return total, items

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        remark=user.remark
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user_update: UserUpdate):
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User):
    db_user.deleted = 1
    db.commit()
    return True
