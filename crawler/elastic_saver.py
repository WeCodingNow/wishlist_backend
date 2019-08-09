from components import Saver
from aioelasticsearch import Elasticsearch

class ElasticSaver(Saver):
    def __init__(self, host='localhost', port='9200'):
        self.host = host
        self.port = port

    async def save(self, product: dict):
        async with Elasticsearch([{'host': self.host, 'port': self.port}]) as es:
            print(product)
            await es.index(
                index='obi',
                doc_type='product',
                id=product['prod_id'],
                body={
                    'name': product['name'],
                    'image_link': product['image_link'],
                    'price': product['price']
                },
            )
