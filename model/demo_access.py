from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta, timezone

Base = declarative_base()

class DemoAccess(Base):
    __tablename__ = "demo_user"
    name = Column(String, nullable=False)
    email = Column(String, primary_key=True) 
    phone_number = Column(String, nullable=False)
    access_upto = Column(DateTime(timezone=True), nullable=False,
                         default=lambda: datetime.now(timezone.utc) + timedelta(days=2))
    access = Column(Boolean, nullable=False, default= False)
    total_time = Column(Integer, nullable=False)