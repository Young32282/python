"""认证相关 Schema"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    role: str
    store_id: int
    real_name: str


class LoginResponse(BaseModel):
    access_token: str
    user: UserInfo
