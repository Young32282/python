"""用户模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # cashier/manager/regional
    store_id = Column(Integer, default=1)
    real_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
