from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Boolean

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    subscription_end = Column(DateTime, default=datetime.utcnow())
    has_used_trial = Column(Boolean, default=False)

    def is_subscription_active(self):
        return self.subscription_end > datetime.utcnow()
