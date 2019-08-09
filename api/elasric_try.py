# from aioelasticsearch import Elasticsearch
# import asyncio
# from settings import elastic_settings
# from json_handler import jsoner

# async def foo():
#     async with Elasticsearch(host='localhost',port=9200) as es:
#         await es.index(
#                 index='obi',
#                 doc_type='product',
#                 id='999',
#                 body={
#                     'name': 'name2 name3',
#                     'image_link': 'image_link2',
#                     'price': 321
#                 },
#             )
#         await es.index(
#             index='obi',
#             doc_type='product',
#             id='678',
#             body={
#                 'name': 'name1',
#                 'image_link': 'image_link1',
#                 'price': 668
#             },
#         )
#         await es.index(
#             index='obi',
#             doc_type='product',
#             id='352',
#             body={
#                 'name': 'name2',
#                 'image_link': 'image_link2',
#                 'price': 987
#             },
#             )
    # data = {}
    # result= {'15987669': ['678']}
    # async with Elasticsearch(elastic_settings) as es:
    #     for user, lst in result.items(): 
    #         prod_list = []              
    #         for prod_id in lst:
    #             prod={"product_id":prod_id}
    #             res = await es.get(index='obi',doc_type='product', id=prod_id)
    #             prod.update(res['_source'])
    #             prod_list.append(prod)
    #         data[user]=prod_list
    # print(jsoner(status=200,giftlist=data))
    
        # print(jsoner(status=200,user_giftlist=data))
    # data = []
    # async with Elasticsearch(elastic_settings) as es:
    #         res = await es.search(index='obi',doc_type='product', body={"query":{"term":{"name":'name2 name3'}}})
    #         if len(res['hits']['hits']) == 0:
    #             res = await es.search(index='obi',doc_type='product', body={"query":{"match":{"name":'name2 name3'}}})
    #         for prod in res['hits']['hits']:
    #             dic={"product_id":prod['_id']}
    #             dic.update(prod['_source'])
    #             data.append(dic)
    #         print(jsoner(status=200,searchlist=data))
            

# asyncio.run(foo())
