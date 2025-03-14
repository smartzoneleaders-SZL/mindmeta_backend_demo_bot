from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from db.base import Base

import uuid

def generate_uuid():
    return str(uuid.uuid4())

class ScheduledCall(Base):
    __tablename__ = "scheduled_calls"
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"))
    call_time = Column(DateTime, nullable=False)
    call_end_time = Column(DateTime)
    call_duration = Column(Integer, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="scheduled")  # can be 'scheduled', 'completed', 'failed'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    mongo_chat_id = Column(String, nullable=True,default=None) # New Column added By manan
