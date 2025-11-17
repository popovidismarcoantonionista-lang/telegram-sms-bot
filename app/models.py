"""
Modelos de banco de dados usando SQLAlchemy ORM.
Define as tabelas: users, orders, sms_rents, followers_orders, logs
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SMSStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CODE_RECEIVED = "code_received"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class FollowersOrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class LogLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class User(Base):
    """Tabela de usuários do Telegram"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    balance = Column(Numeric(10, 2), default=0.00, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="user")
    sms_rents = relationship("SMSRent", back_populates="user")
    followers_orders = relationship("FollowersOrder", back_populates="user")


class Order(Base):
    """Tabela de pedidos de compra de créditos"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    pixintegra_charge_id = Column(String, unique=True, nullable=True, index=True)
    pixintegra_response = Column(Text, nullable=True)  # JSON da resposta completa
    package_type = Column(String, nullable=True)  # economico, padrao, premium
    idempotency_key = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="orders")

    # Indexes
    __table_args__ = (
        Index('idx_order_status_created', 'status', 'created_at'),
    )


class SMSRent(Base):
    """Tabela de aluguel de números SMS"""
    __tablename__ = "sms_rents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    number_id = Column(String, nullable=True)  # ID retornado pela SMS-Activate
    phone = Column(String, nullable=True)
    service = Column(String, nullable=False)  # Serviço (ex: wa, tg, go)
    country = Column(String, nullable=False)  # Código do país
    status = Column(Enum(SMSStatus), default=SMSStatus.PENDING, nullable=False)
    sms_code = Column(String, nullable=True)
    cost = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sms_rents")

    # Indexes
    __table_args__ = (
        Index('idx_sms_status_created', 'status', 'created_at'),
        Index('idx_sms_user_status', 'user_id', 'status'),
    )


class FollowersOrder(Base):
    """Tabela de pedidos de seguidores"""
    __tablename__ = "followers_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # instagram, tiktok, youtube, etc
    quantity = Column(Integer, nullable=False)
    target_url = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(FollowersOrderStatus), default=FollowersOrderStatus.PENDING, nullable=False)
    apex_order_id = Column(String, nullable=True, index=True)
    apex_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="followers_orders")

    # Indexes
    __table_args__ = (
        Index('idx_followers_status_created', 'status', 'created_at'),
    )


class Log(Base):
    """Tabela de logs para auditoria"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)  # telegram, pixintegra, sms_activate, apex
    level = Column(Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(Text, nullable=True)  # JSON dos dados relevantes
    user_id = Column(Integer, nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Indexes
    __table_args__ = (
        Index('idx_logs_source_timestamp', 'source', 'timestamp'),
        Index('idx_logs_level_timestamp', 'level', 'timestamp'),
    )
