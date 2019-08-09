from typing import *

import asyncio
import aio_pika

from rabbit_adapters import RabbitConsumerAdapter
from components import Fetcher, Saver

import json

class RabbitFetcherWrapper(RabbitConsumerAdapter):
    fetcher: Fetcher

    def __init__(self, fetcher: Fetcher, html_queue: asyncio.Queue):
        self.fetcher = fetcher
        self.html_queue = html_queue

    async def work(self, message: aio_pika.IncomingMessage):
        url = message.body.decode()
        html = await self.fetcher.fetch(url)
        await self.html_queue.put((url, html))

class RabbitSaverWrapper(RabbitConsumerAdapter):
    saver: Saver

    def __init__(self, saver: Saver):
        self.saver = saver

    async def work(self, message: aio_pika.IncomingMessage):
        product = json.loads(message.body.decode())
        await self.saver.save(product)

class ProductPublisher:
    async def publish_links(self, links: List[str]):
        for link in links:
                await self.exchange.publish(
                    aio_pika.Message(
                        body=link.encode(),
                    ),
                    routing_key=self.links_queue
                )

    async def publish_product(self, product: dict):
        await self.exchange.publish(
            aio_pika.Message(
                body=json.dumps(product).encode()
            ),
            routing_key=self.product_queue
        )

async def make_publisher(channel: aio_pika.Channel, links_queue: str, product_queue: str) -> ProductPublisher:
    ret_publisher = ProductPublisher()

    ret_publisher.exchange = channel.default_exchange

    ret_publisher.links_queue = links_queue
    await channel.declare_queue(links_queue, durable=True)

    ret_publisher.product_queue = product_queue
    await channel.declare_queue(product_queue, durable=True)

    return ret_publisher
