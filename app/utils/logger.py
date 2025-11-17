"""
Sistema de logging estruturado usando structlog.
"""
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Log, LogLevel
import json
from typing import Optional


# Configurar structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def log_to_db(
    db: AsyncSession,
    source: str,
    level: str,
    message: str,
    payload: Optional[dict] = None,
    user_id: Optional[int] = None
):
    """
    Registra log no banco de dados para auditoria.
    """
    try:
        log_entry = Log(
            source=source,
            level=LogLevel(level.lower()),
            message=message,
            payload=json.dumps(payload) if payload else None,
            user_id=user_id
        )
        db.add(log_entry)
        await db.commit()
    except Exception as e:
        logger.error("failed_to_log_to_db", error=str(e))
