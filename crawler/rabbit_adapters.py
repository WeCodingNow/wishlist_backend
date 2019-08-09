from functools import partial
from abc import ABC, abstractmethod, abstractstaticmethod
from typing import *

import asyncio
import asyncpool
import aio_pika

class RabbitConsumerAdapter(ABC):
    async def ready(
        self,
        channel: aio_pika.Channel,
        queue_name: str,
        durable=None,
        exclusive=None,
        exchange: aio_pika.Exchange = None
    ):
        queue = await channel.declare_queue(queue_name, durable=durable, exclusive=exclusive)

        async def worker() -> asyncio.Task:
            # while True:
            await queue.consume(
                partial(
                    self.message_consume,
                    exchange or channel.default_exchange
                )
            )

        return worker

    @abstractmethod
    async def work(self, message: aio_pika.IncomingMessage):
        ...

    async def message_consume(self, exchange: aio_pika.Exchange, message: aio_pika.IncomingMessage):
        await self.work(message)
        message.ack()


async def main(loop):
    class HelloWorldConsumer(RabbitConsumerAdapter):
        async def work(self, message: aio_pika.IncomingMessage):
            print(message.body.decode())

    connection = await aio_pika.connect(loop=loop)
    channel = await connection.channel()

    test_consumer = HelloWorldConsumer()
    worker = await test_consumer.ready(channel, "hello", durable=True)

    await worker()

    await connection.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    loop.run_forever()
