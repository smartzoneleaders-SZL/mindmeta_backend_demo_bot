from sqlalchemy import Column, ForeignKey, String, DateTime
# for data and time attributes in patient class
from datetime import datetime,timezone

from db.base import Base
import uuid
from sqlalchemy.orm import relationship


def generate_uuid():
    return str(uuid.uuid4())

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id", ondelete="CASCADE"))
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
