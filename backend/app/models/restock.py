"""补货请求模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class RestockRequest(Base):
    __tablename__ = "restock_requests"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, nullable=False, default=1)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    current_qty = Column(Integer, nullable=False)
    request_qty = Column(Integer, nullable=False)
    ai_suggest_qty = Column(Integer, default=None)
    reason = Column(String(500), default=None)
    status = Column(String(20), default="pending")  # pending/approved/rejected/completed
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
