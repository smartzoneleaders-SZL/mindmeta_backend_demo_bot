from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, BigInteger
from sqlalchemy.orm import relationship
from db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class CareHome(Base):
    __tablename__ = "care_homes"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    carehome_name = Column(String, unique=True)
    administrator_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(BigInteger, unique=True)
    address = Column(String)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    is_verify = Column(Boolean, default=False)
    role = Column(String, default="care_home")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    patient = relationship("Patient", back_populates="carehome")