"""认证路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.services.auth_service import verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    token = create_token(user)
    return LoginResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            role=user.role,
            store_id=user.store_id,
            real_name=user.real_name,
        ),
    )


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        store_id=current_user.store_id,
        real_name=current_user.real_name,
    )
