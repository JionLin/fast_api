<!-- WORKSPACE_META_CARD_START -->
> 📌 **项目速览卡片**  
> - **业务领域**：学习沙箱 · Python Web  
> - **核心定位**：FastAPI 分层 CRUD 教学工程。  
> - **启动**：`uvicorn main:app --reload --port 8000` → `/docs`  
> - **状态**：📦 Sandbox，非生产  
> 
> ---
<!-- WORKSPACE_META_CARD_END -->

# FastAPI 用户增删改查实战与学习工程 (fast_api)

> 基于 FastAPI、SQLAlchemy 与 Pydantic 的标准轻量级 Web 服务工程。

---

## 1. 项目定位与简介
本项目是一套用于快速上手与掌握现代 Python 异步 Web 开发的标准 CRUD 示例工程。工程遵循工业级的分层架构设计（路由层、服务层、数据模型层、数据模式校验层及核心配置层），演示了用户注册、查询、密码加密哈希与 MySQL/SQLite 数据库联动。

## 2. 核心功能特性
- **经典分层架构**：清晰划分 API Router、Service、Model、Schema 与 Core 模块。
- **参数校验与序列化**：深度使用 Pydantic 实现强类型请求参数解析与安全响应校验。
- **ORM 数据库交互**：采用 SQLAlchemy ORM 进行数据库建模与会话生命周期管理。
- **安全密码加密**：集成 Passlib 与 Bcrypt 算法，保障用户凭证安全存储。
- **交互式文档自动生成**：原生支持 Swagger UI 与 Redoc 交互式接口文档。
- **详尽配套教程**：工程内附有逐行拆解的技术教学指南 (`TUTORIAL.md`)。

## 3. 技术栈与核心依赖
- **开发语言**：Python 3.10+
- **Web 框架**：FastAPI
- **ASGI 服务器**：Uvicorn
- **ORM 与驱动**：SQLAlchemy, PyMySQL
- **数据校验**：Pydantic (带邮箱格式校验支持)
- **安全加密**：Passlib[bcrypt]

## 4. 快速启动与调试方式

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
# 启动热重载开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 访问接口文档
- 欢迎首页：http://127.0.0.1:8000/
- 交互式 Swagger 文档：http://127.0.0.1:8000/docs
- Redoc 备用文档：http://127.0.0.1:8000/redoc

## 5. 工程目录速览
```text
fast_api/
├── main.py               # 应用入口文件，注册路由与全局配置
├── requirements.txt      # 核心依赖清单
├── TUTORIAL.md           # 逐行代码级超详细教学拆解指南
└── app/
    ├── api/              # 路由控制层 (用户 CRUD 路由定义)
    ├── core/             # 核心配置与数据库连接通道 (database.py)
    ├── models/           # 数据库 ORM 实体模型 (user.py)
    ├── schemas/          # Pydantic 请求与响应校验模式 (user.py)
    └── services/         # 业务逻辑处理服务层 (user.py)
```
