"""促销模型"""

from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(30), nullable=False)  # full_reduction/percentage
    rules_json = Column(Text, nullable=False)  # JSON string
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    status = Column(String(20), default="active")
