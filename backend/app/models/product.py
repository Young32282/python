"""商品模型"""

from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # T恤/衬衫/裤装/外套/配饰
    price = Column(Float, nullable=False)
    image_url = Column(String(255), default=None)
    status = Column(String(20), default="active")
