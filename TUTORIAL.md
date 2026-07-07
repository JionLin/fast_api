# 🚀 FastAPI 小白入门：逐行代码级超详细拆解

这份文档将带你深入到我们刚刚写的每一行代码中。不仅告诉你文件结构，还会详细解释**我们引入了什么框架、每一句代码是什么意思、调用的方法是干什么用的**。

---

## 1. 📦 框架与依赖库 (对应 `requirements.txt`)

在我们写代码前，先看看我们都请了哪些“外援”（第三方库）：

- **`fastapi`**: 我们的核心 Web 框架。它用来接收 HTTP 请求并返回响应。特点是速度极快，且能自动生成接口文档。
- **`uvicorn`**: 服务器。FastAPI 本身只是个代码框架，它需要运行在一个真正的 Web 服务器上，`uvicorn` 就是负责监听端口（比如 8000），把网络请求喂给 FastAPI 的。
- **`sqlalchemy`**: 数据库 ORM 工具。ORM 的意思是，不写死板的 SQL 语句（比如 `SELECT * FROM table`），而是用操作 Python 对象的方式来操作数据库。
- **`pymysql`**: 数据库驱动。SQLAlchemy 只是一个工具，它要连接 MySQL，必须通过一个“翻译官”，`pymysql` 就是让 Python 能和 MySQL 说话的翻译官。
- **`pydantic[email]`**: 数据校验专家。专门用来检查前端传来的数据格式对不对（比如字符串够不够长，邮箱格式对不对）。
- **`passlib[bcrypt]`**: 密码加密工具。绝对不能在数据库存明文密码，这个库专门用来生成和校验加密后的密码哈希值。

---

## 2. 🚰 建立数据库通道 (`app/core/database.py`)

这个文件负责和 MySQL 建立连接。

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 定义数据库地址。格式为：数据库类型+驱动://账号:密码@IP地址:端口/库名
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/demo"

# 2. create_engine: 创建一个数据库引擎。它是 SQLAlchemy 真正和数据库交流的核心。
# pool_pre_ping=True 的作用是每次连接前先 ping 一下，防止数据库断开连接导致报错。
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# 3. sessionmaker: 制造“数据库会话(Session)”的工厂。
# 每次收到一个网页请求，我们就从这里拿一个 Session 去查数据，处理完就关掉。
# autocommit=False 表示不自动提交数据，我们要手动确认无误后再 commit。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. declarative_base: 创建一个基类。我们后面定义的所有表模型，都要继承这个基类。
Base = declarative_base()

# 5. 这是一个生成器函数。它的作用是：只要有人调用它，它就给出一个数据库会话 db。
# yield db 类似于 return，但是它会在使用完后，继续执行 finally 里的 db.close()，保证连接被释放。
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 3. 🧊 数据库表模型 (`app/models/user.py`)

这个文件是告诉 SQLAlchemy，我们的 MySQL 数据库里 `sys_user` 表长什么样。

```python
from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func, Integer, text
from app.core.database import Base

# 1. 继承刚才创建的 Base 基类
class User(Base):
    # 2. __tablename__ 绑定真实的 MySQL 表名
    __tablename__ = "sys_user"

    # 3. 开始定义表的每一列 (Column)
    # primary_key=True: 说明这是主键
    # index=True: 给这个字段加索引，查询会变快
    # autoincrement=True: 自增 ID
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    
    # nullable=False: 不能为空 (NOT NULL)
    # unique=True: 这个用户名不能重复
    username = Column(String(64), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(128), nullable=False, comment="密码(BCrypt)")
    
    # DateTime 和 func.now(): func.now() 会自动调用数据库的当前时间
    # onupdate=func.now(): 只要这条数据被修改，这个字段就会自动更新为当前时间
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 逻辑删除字段。默认是 0 (没删)。
    deleted = Column(Boolean, nullable=False, server_default=text("0"), comment="逻辑删除 0-否 1-是")
```

---

## 4. 📋 数据校验模型 (`app/schemas/user.py`)

**小白注意**：为什么有了上面的 `models` 还要有这里的 `schemas`？
- `models/user.py` 是跟 **数据库** 打交道的（定义表结构）。
- `schemas/user.py` 是跟 **前端/用户** 打交道的（定义用户传来的 JSON 该长什么样，以及我们要返回给用户什么 JSON）。

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# 1. 基础模型：把增删改查都会用到的通用字段放这里
class UserBase(BaseModel):
    # Field(..., max_length=64) 中的 "..." 表示这个字段是必填的！最大长度64。
    username: str = Field(..., max_length=64, description="用户名")
    # Optional[str] 表示这个字段可填可不填 (相当于可以为 None)
    nickname: Optional[str] = Field(None, max_length=64, description="昵称")
    # EmailStr 是 pydantic 提供的，会自动帮你检查这到底是不是一个合法邮箱格式！
    email: Optional[EmailStr] = Field(None, max_length=128, description="邮箱")

# 2. 创建用户模型：前端在注册时，必须传的数据。它继承了 UserBase。
class UserCreate(UserBase):
    # 额外增加一个必填的密码，而且限制了不能少于 6 位。
    password: str = Field(..., min_length=6, max_length=128, description="明文密码")

# 3. 响应给前端的模型：我们查完数据库，要扔给前端的数据。
class UserResponse(UserBase):
    id: int
    status: int
    create_time: datetime
    update_time: datetime

    # 这个 Config 是灵魂！它允许 Pydantic 直接把 SQLAlchemy 的数据库对象(models)，
    # 自动转换成这个字典格式，不需要我们手动一个一个字段去赋值。
    class Config:
        from_attributes = True
```
*看！在 `UserResponse` 里面，我们没有写 `password`。这就保证了密码绝对不会返回给前端！*

---

## 5. 👨‍🍳 核心业务逻辑 (`app/services/user.py`)

这里是专门负责去数据库里做增删改查动作的“工人”。

```python
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# 1. 初始化密码加密工具，指定使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # 调用 pwd_context.hash()，把明文密码变成哈希乱码
    return pwd_context.hash(password)

# --- 查询单个用户 ---
def get_user(db: Session, user_id: int):
    # db.query(User): 相当于 SELECT * FROM sys_user
    # .filter(...): 相当于 WHERE id = user_id AND deleted = 0
    # .first(): 相当于 LIMIT 1，只拿第一条数据，查不到就返回 None
    return db.query(User).filter(User.id == user_id, User.deleted == 0).first()

# --- 分页查询用户列表 ---
def get_user_list(db: Session, skip: int = 0, limit: int = 10):
    query = db.query(User).filter(User.deleted == 0)
    # query.count(): 查一共有多少条数据 (用于前端分页显示总数)
    total = query.count()
    # .offset(skip).limit(limit): 跳过 skip 条，拿 limit 条。相当于 LIMIT skip, limit
    # .all(): 把所有数据拿出来放到一个列表里
    items = query.offset(skip).limit(limit).all()
    return total, items

# --- 创建用户 ---
def create_user(db: Session, user: UserCreate):
    # 1. 拿到明文密码，进行加密
    hashed_password = get_password_hash(user.password)
    # 2. 实例化一个数据库模型 User (准备往里面塞数据)
    db_user = User(
        username=user.username,
        password=hashed_password,
        nickname=user.nickname,
        # ...省略其他字段
    )
    # 3. db.add() 告诉数据库我要新增这个对象 (但此时还没真正执行 SQL)
    db.add(db_user)
    # 4. db.commit() 真正向数据库提交事务 (INSERT 执行)
    db.commit()
    # 5. db.refresh() 提交后，数据库会生成一个自增的 ID，这行代码把新生成的 ID 刷新回 db_user 对象里
    db.refresh(db_user)
    return db_user

# --- 软删除用户 ---
def delete_user(db: Session, db_user: User):
    # 并没有调用 db.delete()！只是把 deleted 字段变成了 1。
    db_user.deleted = 1
    # 提交修改
    db.commit()
    return True
```

---

## 6. 💁 暴露 API 接口 (`app/api/user.py`)

这里是程序暴露给外网的大门，前端就是向这里发请求的。

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services import user as user_service

# 1. APIRouter: 路由组。prefix="/users" 意味着下面所有的接口前面都会自动拼上 /users
router = APIRouter(prefix="/users", tags=["Users"])

# 2. @router.post("/"): 定义一个 POST 接口 (对应增)
# response_model=UserResponse: 告诉 FastAPI，把返回的数据自动按照 UserResponse 的格式过滤一下
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Depends(get_db): 依赖注入。FastAPI 收到请求时，会自动去调用 database.py 里的 get_db() 给我们一个会话
    
    # 检查用户名是否已经被注册了
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        # 如果注册过，抛出一个 HTTPException，前端会收到 400 报错和 detail 里的文字
        raise HTTPException(status_code=400, detail="Username already registered")
        
    # 如果没注册过，叫厨师 (user_service) 去干活
    return user_service.create_user(db=db, user=user)

# 3. @router.get("/{user_id}"): 路径参数。大括号里的 user_id 会被 FastAPI 自动抓取并传给下面的函数
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 4. @router.get("/"): 获取列表，Query() 是查询参数 (问号后面的内容 ?skip=0&limit=10)
# ge=0 表示 >= 0, le=100 表示 <= 100。FastAPI 会自动帮你校验这些规则！
def read_users(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    total, items = user_service.get_user_list(db, skip=skip, limit=limit)
    return {"total": total, "items": items}
```

---

## 7. 🚪 程序的起点 (`main.py`)

最后，我们看看这个极简的启动入口：

```python
from fastapi import FastAPI
from app.api import user

# 1. 实例化 FastAPI 核心对象，这就好比你建了一台服务器。
# title 会展示在自动生成的文档页面上。
app = FastAPI(title="FastAPI CRUD Learning API")

# 2. 挂载路由！把我们在 app/api/user.py 里写的那个收银台(router) 搬到大厅里来。
# 这样服务器就知道要去哪里处理 /users 的请求了。
app.include_router(user.router)

# 3. 这是一个最简单的根目录接口 (测试服务死活用的)
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI CRUD Learning API"}
```

现在，你应该对这里的每一行代码到底是干什么用的都了如指掌了吧！

---

## 8. 💡 进阶解惑：FastAPI 是如何区分入参的？

很多从其他语言（比如 Java 里的 `@PathVariable`, `@RequestParam`, `@RequestBody`）刚转到 FastAPI 的新手，最容易对**入参是怎么传递的**感到困惑。

FastAPI 的设计哲学是**“魔法般的类型提示”**。它完全靠你**写的类型（Type Hints）和路径规则**来自动判断数据是从哪里来的。

记住以下 **3 条黄金法则**：

### 法则 1：如何识别 Path Variable (路径参数)？
**规则：只要参数名字出现在了路由的 `{}` 里，它就是路径参数。**

```python
@router.get("/{user_id}") # 👈 路由里声明了 {user_id}
def read_user(user_id: int): # 👈 函数的参数名刚好也叫 user_id
    pass
```
*   **解释**：FastAPI 一看路由里有 `{user_id}`，函数的参数也叫 `user_id`，它立马懂了：你要从 URL 路径里抠出这个数字（比如 `/users/123` 中的 `123`）。

### 法则 2：如何识别 Request Body (请求体)？
**规则：只要参数的类型是一个 Pydantic 的 `BaseModel`，它就是请求体。**

```python
# UserCreate 是继承自 BaseModel 的类
@router.post("/") 
def create_user(user: UserCreate): # 👈 参数类型是 UserCreate
    pass
```
*   **解释**：当 FastAPI 看到参数 `user` 的类型是 `UserCreate`（复杂数据模型）时，它知道这种复杂数据不能放在 URL 里，于是它会**自动去读取 HTTP 请求的 Body (JSON 格式)**。

### 法则 3：如何识别 Query Parameter (查询参数 / Param)？
**规则：如果参数既不在 `{}` 里，又不是 `BaseModel`（也就是普通的 `int`、`str` 等基本类型），那它就是查询参数。**

```python
@router.get("/")
def read_users(skip: int = 0, limit: int = 10): 
    pass
```
*   **解释**：路由是 `/`（没有 `{}`）。参数 `skip` 和 `limit` 只是普通的 `int` 类型。FastAPI 会自动把它们当成跟在问号后面的查询参数（例如 `/users/?skip=0&limit=10`）。

### 终极混合大测试
如果你的接口长这样，你能分清它们分别是从哪里来的吗？

```python
@router.put("/users/{user_id}")
def update_something(
    user_id: int,           # 👈 1. 路由里有，这是 Path Variable
    q: str,                 # 👈 2. 普通类型，不在路由里，这是 Query Parameter
    user_data: UserUpdate   # 👈 3. BaseModel 类型，这是 Request Body
):
    pass
```
所以，一个形如 `PUT /users/1?q=search` 并且带有 JSON Body 的请求，FastAPI 能够完美且自动地把这三种数据分别塞给这三个参数，**你一行解析代码都不需要写！**

如果在启动或者测试时遇到不明白的地方，随时问我！

---

## 9. 💡 进阶解惑：为什么每个文件夹下都有一个 `__init__.py`，可以删掉吗？

这是一个非常典型的 Python 语言特性的问题！

在我们的项目里，你会发现 `app/`、`api/`、`core/` 等每一个文件夹下面都有一个空文件叫 `__init__.py`。

### 结论先行
**在 Python 3.3 及以上的版本中，你可以删掉它们，程序照样能跑。但是，作为工业级项目，强烈建议保留它们！**

### 为什么要有这个文件？

在 Python 的世界里：
1. **带有 `__init__.py` 的文件夹**，被称为 **Package（包）**。
2. **没有 `__init__.py` 的文件夹**，仅仅就是一个**普通的系统目录**。

当你写出这样的代码时：
```python
from app.api import user
```
Python 的底层逻辑是：
* “哦！你要导入 `app`？让我看看 `app` 文件夹里有没有 `__init__.py`。”
* 如果有，Python 就会把它当作一个正规的包，然后顺着找里面的 `api` 包，再找里面的 `user.py` 模块。

### 既然 Python 3.3 之后能删，为什么还要保留？

从 Python 3.3 开始，引入了“隐式命名空间包 (Implicit Namespace Packages)”的概念。意思是就算没有 `__init__.py`，Python 也能勉强把它当成包来导入。但我们**依然坚持在每个文件夹下放一个空的 `__init__.py`**，原因有三：

1. **兼容性与稳健性**：很多第三方的代码检查工具（比如 `mypy` 用于类型检查，`flake8` 用于代码规范检查）以及测试框架（比如 `pytest`）非常死板，如果不加 `__init__.py`，它们可能会找不到你的代码，导致诡异的报错。
2. **你可以用它来“对外暴露”接口**：`__init__.py` 不一定非得是空的。比如在 `app/models/__init__.py` 里，你可以写 `from .user import User`。这样其他地方导入时，只需要写 `from app.models import User`，而不需要写很长的 `from app.models.user import User`。
3. **行业规范**：这就像是给其他程序员的一个“视觉信号”，告诉大家：“嘿！这是一个 Python 代码包，不是放图片或者文档的杂物堆！”
