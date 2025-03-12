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


    # Relationship to FamilyMember, Chat and Summary
    carehome = relationship("CareHome", back_populates="patient")
    family_members = relationship("FamilyMember", back_populates="patient", order_by=asc("created_at"), cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="patient", cascade="all, delete-orphan")
    calls = relationship("Call", back_populates="patient", cascade="all, delete-orphan")
    call_topic = relationship("CallTopic", back_populates="patient", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="patient", cascade="all, delete-orphan")
    scheduled_calls = relationship("ScheduledCall", back_populates="patient", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="patient", cascade="all, delete-orphan")
    media_uploads = relationship("MediaUpload", back_populates="patient", cascade="all, delete-orphan")
    instruction = relationship("Instruction", back_populates="patient", cascade="all, delete-orphan")
    description = relationship("Description", back_populates="patient", cascade="all, delete-orphan")
    life_history = relationship("LifeHistory", back_populates="patient", cascade="all, delete-orphan")

