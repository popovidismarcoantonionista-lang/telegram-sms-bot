import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import Log

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def log_to_db(db: Session, source: str, level: str, message: str, payload: str = None):
    try:
        log_entry = Log(source=source, payload=payload, level=level, message=message, timestamp=datetime.utcnow())
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar log no banco: {str(e)}")
