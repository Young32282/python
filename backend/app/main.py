"""FastAPI 应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import *  # noqa: F401, F403 - 确保所有模型被加载
from app.routers import auth

# 创建表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Store API", version="1.0.0")

# CORS 配置（开发模式允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)

try:
    from app.routers import dashboard
    app.include_router(dashboard.router)
except ImportError:
    pass

try:
    from app.routers import pos
    app.include_router(pos.router)
except ImportError:
    pass

try:
    from app.routers import products
    app.include_router(products.router)
except ImportError:
    pass

try:
    from app.routers import inventory
    app.include_router(inventory.router)
except ImportError:
    pass

try:
    from app.routers import members
    app.include_router(members.router)
except ImportError:
    pass

try:
    from app.routers import ai
    app.include_router(ai.router)
except ImportError:
    pass


@app.get("/")
def root():
    return {"message": "Smart Store API is running"}
