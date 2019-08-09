import asyncio
import uuid
from aio_pika import connect, IncomingMessage, Message

from abc import ABC

import json

from settings import settings, rabbit_settings

class RPCClient(ABC):
    def __init__(self, loop):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = loop

    async def connect(self, host, port):
        self.connection = await connect(host=host, port=port, loop=self.loop)
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(
            exclusive=True
        )
        await self.callback_queue.consume(self.on_response)

        return self

    def on_response(self, message: IncomingMessage):
        future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, routing_key, **kwargs):
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(kwargs).encode(),
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=routing_key,
        )

        return await future

class AuthRPCClient(RPCClient):
    def __init__(self, loop):
        super().__init__(loop)

    async def register(self, **kwargs):
        return await super().call(settings['reg_queue_name'], **kwargs)

    async def authorize(self, **kwargs):
        return await super().call(settings['auth_queue_name'], **kwargs)


class AuthRPC:
    client = AuthRPCClient(None)
    connected = False

    @classmethod
    async def check_conn(cls):
        if not cls.connected:
            cls.client.loop = asyncio.get_running_loop()
            await cls.client.connect(**rabbit_settings)
            cls.connected = True

    async def register(self, **kwargs):
        await self.check_conn()
        return await self.client.register(**kwargs)

    async def authorize(self, **kwargs):
        await self.check_conn()
        return await self.client.authorize(**kwargs)


        
