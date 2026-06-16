"""订单模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, nullable=False)
    store_id = Column(Integer, nullable=False, default=1)
    member_id = Column(Integer, ForeignKey("members.id"), default=None)
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0)
    payment_amount = Column(Float, nullable=False)
    payment_method = Column(String(20), nullable=False, default="wechat")  # cash/wechat/alipay/card
    status = Column(String(20), nullable=False, default="completed")  # completed/voided
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
