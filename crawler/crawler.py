from typing import *

import asyncio
import aio_pika

from settings import crawler_settings, elastic_settings, rabbit_settings

from simple_fetcher import SimpleFetcherRPSC
from obi_parser import ObiParser
from elastic_saver import ElasticSaver

from rabbit_wrappers import RabbitFetcherWrapper, RabbitSaverWrapper, ProductPublisher, make_publisher

class Crawler:
    def __init__(
        self,
        domain_name: str,
        rabbit_connection: aio_pika.RobustConnection,
        rps: int = 1,
        elastic_host: str = "localhost",
        elastic_port: int = 9200,
        fetchers: int = 1,
        parser_publishers: int = 1,
        savers: int = 1,
        visited_urls_max: int = None,
    ):
        self.domain_name = domain_name
        self.rps = rps
        self.fetchers = fetchers
        self.parser_publishers = parser_publishers
        self.elastic_host = elastic_host
        self.elastic_port = elastic_port
        self.savers = savers
        self.visited_urls_max = visited_urls_max

        self.connection = rabbit_connection
        self.visited_urls = []

    def cleanse_links(self, links: List[str]):
        indomain_urls = list(filter(
           lambda url: url and \
               url not in self.visited_urls \
               and self.domain_name in url,
               links
        ))

        self.visited_urls += indomain_urls
        if len(self.visited_urls) > self.visited_urls_max:
            print('exceeded max visited urls')
            self.visited_urls = self.visited_urls[len(self.visited_urls)//2:-1]
        return indomain_urls

    async def go(self):

        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=1)
        html_queue = asyncio.Queue(20)

        publisher = await make_publisher(channel, 'test_links', 'test_products')
        await publisher.publish_links(['https://' + self.domain_name])

        fetcher = SimpleFetcherRPSC().set_rps(self.rps)
        await fetcher.initialize()
        fetcher_wrapper = RabbitFetcherWrapper(fetcher, html_queue)

        fetcher_workers = []
        for _ in range(self.fetchers):
            fetcher_workers.append(await fetcher_wrapper.ready(channel, 'test_links', durable=True))
            print('created fetcher')

        parser = ObiParser()
        print('created parser')

        publisher_workers = []
        for _ in range(self.parser_publishers):
            publisher = await make_publisher(channel, 'test_links', 'test_products')

            async def parser_publisher():
                while True:
                    url, html = await html_queue.get()

                    parse_result = parser.parse(url, html)
                    links = self.cleanse_links(parse_result.links)

                    await publisher.publish_links(links)
                    if parse_result.product:
                        await publisher.publish_product(parse_result.product)

            publisher_workers.append(parser_publisher)
            print('created parser_publisher worker')

        saver = RabbitSaverWrapper(
            saver=ElasticSaver(host=self.elastic_host, port=self.elastic_port),
        )

        saver_workers = []
        for _ in range(self.savers):
            saver_worker = await saver.ready(channel, 'test_products', durable=True)
            print('created saver')
            saver_workers.append(saver_worker)

        workers = fetcher_workers + publisher_workers + saver_workers
        await asyncio.gather(
            *[worker() for worker in workers]
        )


async def main(loop):
    await asyncio.sleep(20)
    connection = await aio_pika.connect(**rabbit_settings, loop=loop)

    c = Crawler(**crawler_settings, **elastic_settings, rabbit_connection=connection)
    await c.go()

    await connection.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(loop))
    except KeyboardInterrupt:
        print("Received exit, exiting")
