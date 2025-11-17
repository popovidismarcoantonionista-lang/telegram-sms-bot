"""
Sistema de idempotência usando Redis para prevenir processamento duplicado.
"""
import redis.asyncio as redis
from typing import Optional
import json
from datetime import timedelta
from ..config import settings


class IdempotencyManager:
    """Gerenciador de idempotência"""

    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def check_and_lock(self, key: str, ttl_seconds: int = 300) -> bool:
        """
        Verifica se a chave já foi processada e cria um lock.
        Retorna True se pode processar (primeira vez), False se já processado.
        """
        result = await self.redis_client.set(
            f"idempotency:{key}",
            "processing",
            nx=True,  # Apenas se não existir
            ex=ttl_seconds
        )
        return result is not None

    async def mark_completed(self, key: str, result: dict, ttl_seconds: int = 86400):
        """Marca como completado e armazena resultado"""
        await self.redis_client.set(
            f"idempotency:{key}",
            json.dumps({"status": "completed", "result": result}),
            ex=ttl_seconds
        )

    async def get_result(self, key: str) -> Optional[dict]:
        """Recupera resultado se já processado"""
        data = await self.redis_client.get(f"idempotency:{key}")
        if data:
            try:
                parsed = json.loads(data)
                if parsed.get("status") == "completed":
                    return parsed.get("result")
            except json.JSONDecodeError:
                pass
        return None

    async def release_lock(self, key: str):
        """Libera lock em caso de erro"""
        await self.redis_client.delete(f"idempotency:{key}")

    async def close(self):
        """Fecha conexão Redis"""
        await self.redis_client.close()


idempotency_manager = IdempotencyManager()
