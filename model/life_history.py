from sqlalchemy import Column, ForeignKey, String, DateTime
# for data and time attributes in patient class
from datetime import datetime,timezone

from db.base import Base
import uuid
from sqlalchemy.orm import relationship



def generate_uuid():
    return str(uuid.uuid4())

class LifeHistory(Base):
    __tablename__ = "life_histories"

    id = Column(String, primary_key=True, default=generate_uuid)
    history = Column(String)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"))
    family_member_id = Column(String, ForeignKey("family_members.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))