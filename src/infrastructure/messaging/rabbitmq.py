"""
Módulo de mensajería RabbitMQ.

Maneja la publicación y consumo de eventos a través de RabbitMQ.
Se usa en el flujo de login: el API publica el evento de login,
un consumer lo procesa validando contra MySQL.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable, Any

import aio_pika
from aio_pika import Message, DeliveryMode

from src.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Nombres de las colas
AUTH_LOGIN_QUEUE = "auth_login"
AUTH_EVENTS_QUEUE = "auth_events"


class RabbitMQConnection:
    """Gestiona la conexión a RabbitMQ."""

    _connection: Optional[aio_pika.RobustConnection] = None
    _channel: Optional[aio_pika.Channel] = None

    @classmethod
    async def connect(cls):
        """Establece conexión con RabbitMQ."""
        if cls._connection is None or cls._connection.is_closed:
            try:
                cls._connection = await aio_pika.connect_robust(
                    settings.rabbitmq_url,
                    timeout=10,
                )
                cls._channel = await cls._connection.channel()
                
                # Declarar las colas
                await cls._channel.declare_queue(AUTH_LOGIN_QUEUE, durable=True)
                await cls._channel.declare_queue(AUTH_EVENTS_QUEUE, durable=True)
                
                logger.info("✅ Conectado a RabbitMQ exitosamente")
            except Exception as e:
                logger.error(f"❌ Error conectando a RabbitMQ: {e}")
                raise
        return cls._channel

    @classmethod
    async def disconnect(cls):
        """Cierra la conexión con RabbitMQ."""
        if cls._connection and not cls._connection.is_closed:
            await cls._connection.close()
            cls._connection = None
            cls._channel = None
            logger.info("🔌 Desconectado de RabbitMQ")

    @classmethod
    async def get_channel(cls) -> aio_pika.Channel:
        """Obtiene el canal activo, reconectando si es necesario."""
        if cls._channel is None or cls._channel.is_closed:
            await cls.connect()
        return cls._channel


class RabbitMQPublisher:
    """Publica mensajes/eventos a RabbitMQ."""

    @staticmethod
    async def publish(queue_name: str, data: dict) -> None:
        """
        Publica un mensaje a una cola de RabbitMQ.

        Args:
            queue_name: Nombre de la cola destino
            data: Datos a enviar en formato diccionario
        """
        try:
            channel = await RabbitMQConnection.get_channel()

            message = Message(
                body=json.dumps(data, default=str).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
            )

            await channel.default_exchange.publish(
                message,
                routing_key=queue_name,
            )

            logger.info(f"📤 Mensaje publicado en '{queue_name}': {data.get('event_type', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Error publicando mensaje en RabbitMQ: {e}")
            raise

    @staticmethod
    async def publish_login_event(user_id: str, email: str, success: bool) -> None:
        """Publica un evento de login."""
        await RabbitMQPublisher.publish(
            AUTH_EVENTS_QUEUE,
            {
                "event_type": "user_login",
                "user_id": user_id,
                "email": email,
                "success": success,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @staticmethod
    async def publish_register_event(user_id: str, email: str) -> None:
        """Publica un evento de registro."""
        await RabbitMQPublisher.publish(
            AUTH_EVENTS_QUEUE,
            {
                "event_type": "user_register",
                "user_id": user_id,
                "email": email,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
