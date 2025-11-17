"""
Cliente para integração com a API SMS-Activate.
Documentação: https://sms-activate.io/api2
"""
import httpx
from typing import Dict, Optional
from ..config import settings
from ..utils.logger import logger
import asyncio


class SMSActivateClient:
    """Cliente da API SMS-Activate"""

    def __init__(self):
        self.base_url = settings.SMS_ACTIVATE_BASE_URL
        self.api_key = settings.SMS_ACTIVATE_API_KEY

    async def get_number(
        self,
        service: str,
        country: str = "0"  # 0 = Russia (padrão)
    ) -> Dict:
        """
        Obtém um número para receber SMS.

        Params:
            service: Código do serviço (wa=WhatsApp, tg=Telegram, go=Google, etc)
            country: Código do país

        Returns:
            {
                "success": True,
                "activation_id": "123456",
                "phone_number": "+79001234567"
            }
        """
        params = {
            "api_key": self.api_key,
            "action": "getNumber",
            "service": service,
            "country": country
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.base_url, params=params)
                response_text = response.text

                # API retorna formato: ACCESS_NUMBER:activation_id:phone_number
                if response_text.startswith("ACCESS_NUMBER"):
                    parts = response_text.split(":")
                    if len(parts) == 3:
                        logger.info(
                            "sms_activate_number_obtained",
                            activation_id=parts[1],
                            phone=parts[2],
                            service=service
                        )
                        return {
                            "success": True,
                            "activation_id": parts[1],
                            "phone_number": parts[2]
                        }

                # Erros comuns
                error_messages = {
                    "NO_NUMBERS": "Números indisponíveis para este serviço",
                    "NO_BALANCE": "Saldo insuficiente na conta SMS-Activate",
                    "BAD_SERVICE": "Serviço inválido",
                    "BAD_KEY": "API key inválida"
                }

                error_msg = error_messages.get(response_text, response_text)
                logger.error("sms_activate_error", error=error_msg, service=service)

                return {
                    "success": False,
                    "error": error_msg
                }

            except Exception as e:
                logger.error("sms_activate_request_failed", error=str(e))
                return {
                    "success": False,
                    "error": str(e)
                }

    async def get_status(self, activation_id: str) -> Dict:
        """
        Verifica status de uma ativação e obtém código SMS se disponível.

        Returns:
            {
                "success": True,
                "status": "STATUS_OK",
                "code": "123456"
            }
        """
        params = {
            "api_key": self.api_key,
            "action": "getStatus",
            "id": activation_id
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.base_url, params=params)
                response_text = response.text

                # STATUS_OK:code - Código recebido
                if response_text.startswith("STATUS_OK"):
                    code = response_text.split(":")[1] if ":" in response_text else None
                    logger.info(
                        "sms_code_received",
                        activation_id=activation_id,
                        code=code
                    )
                    return {
                        "success": True,
                        "status": "STATUS_OK",
                        "code": code
                    }

                # STATUS_WAIT_CODE - Aguardando código
                if response_text == "STATUS_WAIT_CODE":
                    return {
                        "success": True,
                        "status": "STATUS_WAIT_CODE",
                        "code": None
                    }

                # STATUS_WAIT_RETRY - Aguardar antes de checar novamente
                if response_text == "STATUS_WAIT_RETRY":
                    return {
                        "success": True,
                        "status": "STATUS_WAIT_RETRY",
                        "code": None
                    }

                # STATUS_CANCEL - Ativação cancelada
                if response_text == "STATUS_CANCEL":
                    return {
                        "success": True,
                        "status": "STATUS_CANCEL",
                        "code": None
                    }

                return {
                    "success": False,
                    "error": response_text
                }

            except Exception as e:
                logger.error("sms_activate_status_failed", error=str(e))
                return {
                    "success": False,
                    "error": str(e)
                }

    async def set_status(self, activation_id: str, status: int) -> Dict:
        """
        Altera status da ativação.

        Status codes:
        1 - Pronto (SMS chegou, aguardando mais)
        3 - Solicitar outro código
        6 - Concluir ativação
        8 - Cancelar ativação (reembolso)
        """
        params = {
            "api_key": self.api_key,
            "action": "setStatus",
            "id": activation_id,
            "status": status
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(self.base_url, params=params)
                response_text = response.text

                if response_text == "ACCESS_READY":
                    return {"success": True}
                elif response_text == "ACCESS_RETRY_GET":
                    return {"success": True}
                elif response_text == "ACCESS_ACTIVATION":
                    return {"success": True}
                elif response_text == "ACCESS_CANCEL":
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "error": response_text
                    }

            except Exception as e:
                logger.error("sms_activate_set_status_failed", error=str(e))
                return {
                    "success": False,
                    "error": str(e)
                }

    async def poll_for_code(
        self,
        activation_id: str,
        max_attempts: int = 60,
        interval_seconds: int = 10
    ) -> Dict:
        """
        Faz polling até receber o código SMS ou expirar.

        Params:
            activation_id: ID da ativação
            max_attempts: Máximo de tentativas (padrão: 60 = 10 minutos)
            interval_seconds: Intervalo entre tentativas

        Returns:
            {
                "success": True,
                "code": "123456"
            }
        """
        for attempt in range(max_attempts):
            result = await self.get_status(activation_id)

            if result.get("success"):
                status = result.get("status")

                if status == "STATUS_OK" and result.get("code"):
                    return {
                        "success": True,
                        "code": result.get("code")
                    }
                elif status == "STATUS_CANCEL":
                    return {
                        "success": False,
                        "error": "Ativação cancelada"
                    }

            await asyncio.sleep(interval_seconds)

        # Timeout - cancelar e reembolsar
        await self.set_status(activation_id, 8)
        return {
            "success": False,
            "error": "Timeout aguardando código SMS"
        }


sms_activate_client = SMSActivateClient()
