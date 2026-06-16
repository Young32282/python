"""FastAPI 应用入口"""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine, Base
from app.models import *  # noqa: F401, F403 - 确保所有模型被加载
from app.routers import auth

# 创建表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Store API", version="1.0.0")

# 前端静态文件目录（相对于 backend 目录）
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

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


# 托管前端静态文件
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """前端 SPA 路由：所有非 API 路径返回 index.html"""
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "Smart Store API is running"}
