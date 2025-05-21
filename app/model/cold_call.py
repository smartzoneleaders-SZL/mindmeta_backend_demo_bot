from sqlalchemy import Column, String, Integer
from db.base import Base




class ColdCall(Base):
    __tablename__ = "cold_call_script"

    id = Column(Integer, primary_key=True, default=1)
    cold_call_message = Column(String, nullable=False)
    