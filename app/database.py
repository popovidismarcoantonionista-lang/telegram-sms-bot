from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="user")
    sms_rents = relationship("SMSRent", back_populates="user")
    follower_orders = relationship("FollowerOrder", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    credits = Column(Float, nullable=False)
    package_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    pluggy_charge_id = Column(String, unique=True, nullable=True)
    pluggy_payment_id = Column(String, unique=True, nullable=True)
    qr_code_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="orders")

class SMSRent(Base):
    __tablename__ = "sms_rents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activation_id = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    country = Column(String, nullable=False)
    service = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    status = Column(String, default="active")
    sms_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="sms_rents")

class FollowerOrder(Base):
    __tablename__ = "followers_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    platform = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    profile_url = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, default="pending")
    apex_order_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="follower_orders")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    payload = Column(Text, nullable=True)
    level = Column(String, default="info")
    message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
