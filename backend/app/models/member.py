"""会员模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime

from app.database import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(11), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    level = Column(String(20), default="normal")  # normal/silver/gold/diamond
    total_spent = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    points = Column(Integer, default=0)
    preferences = Column(String(200), default=None)
    level_updated_at = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
