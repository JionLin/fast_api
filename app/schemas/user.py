from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., max_length=64, description="用户名")
    nickname: Optional[str] = Field(None, max_length=64, description="昵称")
    email: Optional[EmailStr] = Field(None, max_length=128, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, max_length=256, description="头像URL")
    remark: Optional[str] = Field(None, max_length=256, description="备注")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="明文密码")

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=64, description="昵称")
    email: Optional[EmailStr] = Field(None, max_length=128, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    avatar: Optional[str] = Field(None, max_length=256, description="头像URL")
    remark: Optional[str] = Field(None, max_length=256, description="备注")

class UserResponse(UserBase):
    id: int
    status: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    total: int
    items: List[UserResponse]
