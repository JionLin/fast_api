from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func, Integer, text
from app.core.database import Base

class User(Base):
    __tablename__ = "sys_user"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    username = Column(String(64), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(128), nullable=False, comment="密码(BCrypt)")
    nickname = Column(String(64), nullable=True, comment="昵称")
    email = Column(String(128), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    avatar = Column(String(256), nullable=True, comment="头像URL")
    status = Column(Integer, nullable=False, server_default=text("1"), comment="状态 1-正常 0-禁用")
    token_version = Column(Integer, nullable=False, server_default=text("0"), comment="JWT版本，改密递增")
    remark = Column(String(256), nullable=True, comment="备注")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted = Column(Boolean, nullable=False, server_default=text("0"), comment="逻辑删除 0-否 1-是")
