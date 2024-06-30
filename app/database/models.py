# bot/database/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime, timedelta

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    subscription_end = Column(DateTime, default=datetime.utcnow() + timedelta(days=30))

    def is_subscription_active(self):
        return self.subscription_end > datetime.utcnow()
