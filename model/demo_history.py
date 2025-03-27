from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class DemoHistory(Base):
    __tablename__ = "demo_history"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    name= Column(String, nullable= False)
    phone_number = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

