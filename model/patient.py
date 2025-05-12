from sqlalchemy import Column, ForeignKey, String, Boolean, Integer, Date, DateTime, asc
# for data and time attributes in patient class
from datetime import datetime,timezone

from db.base import Base
import uuid
from sqlalchemy.orm import relationship



def generate_uuid():
    return str(uuid.uuid4())

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    carehome_id = Column(String, ForeignKey("care_homes.id", ondelete="CASCADE"))
    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    birthdate = Column(Date, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    medical_history = Column(String, nullable=True)
    gender = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    chat_group_id = Column(String,nullable=True)
    hume_config_id = Column(String)
    hume_voice = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    # Relation
    carehome = relationship("CareHome", back_populates="patient")
