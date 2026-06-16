"""库存模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, nullable=False, default=1)
    quantity = Column(Integer, nullable=False, default=0)
    safety_stock = Column(Integer, nullable=False, default=10)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
