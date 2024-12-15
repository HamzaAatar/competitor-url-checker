from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    input_data = Column(JSON)
    result = Column(JSON)
    created_at = Column(
        default=datetime.now(timezone.utc), type_=TIMESTAMP(timezone=True)
    )
    updated_at = Column(
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
        type_=TIMESTAMP(timezone=True),
    )

    user = relationship("User")
