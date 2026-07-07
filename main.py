from fastapi import FastAPI
from app.api import user
from app.core.database import engine, Base

# In a real app you might use Alembic, but for learning we can just create tables here if they don't exist
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI CRUD Learning API")

app.include_router(user.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI CRUD Learning API"}
