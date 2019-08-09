from aiohttp import web
import asyncio
import asyncpg
from auth_client import AuthRPC
from bd_handler import bd_handler 
from json_handler import jsoner
import sys
sys.path.append('../')
from aioelasticsearch import Elasticsearch

from settings import elastic_settings


class Handler:

    
    auth_=AuthRPC()
    # FULL READY
    async def auth(self,request):
        try:
            data = await request.json()
            vk_id = data['vk_id']
            access_token = data['access_token']
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        token = await self.auth_.register(user_id = vk_id, access_token = access_token)
        token = token.decode()

        try: 
            await bd_handler.authorisation(vk_id=vk_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        # response = jsoner(status=200,token=token)
        response = jsoner(status=200,token=token)
        return web.json_response(response)

    # FULL READY
    async def my_wishlist(self,request):
        
        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            result= await bd_handler.get_list_of_products(vk_id=vk_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)
        
        data = []
        # async with Elasticsearch([{'host': 'localhost', 'port': 9200}]) as es:
        try: 
            async with Elasticsearch(elastic_settings) as es:
                for rec in result:
                    prod = {'product_id':rec['product_id'],'gift':rec['gift_id']}
                    res = await es.get(index='obi',doc_type='product', id=rec['product_id'])
                    prod.update(res['_source'])
                    data.append(prod)
        except: 
            return web.json_response({'status':'404','text':'NOT FOUND'})

        response = jsoner(status=200,wishlist=data)
        return web.json_response(response)

    # FULL READY
    async def search(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            search_querry = str(data['search']) 
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        data = []
        try:
            async with Elasticsearch(elastic_settings) as es:
                    res = await es.search(index='obi',doc_type='product', body={"query":{"terms":{"name":[search_querry]}}})
                    if len(res['hits']['hits']) == 0:
                        res = await es.search(index='obi',doc_type='product', body={"query":{"match":{"name":'name2 name3'}}})
                    for prod in res['hits']['hits']:
                        dic={"product_id":prod['_id']}
                        dic.update(prod['_source'])
                        data.append(dic)
        except: 
            return web.json_response({'status':'404','text':'NOT FOUND'})
        
        response = jsoner(status=200,searchlist=data)
        return web.json_response(response)

    # FULL READY
    async def adding_wish(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            product_id = data['product'] 
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            await bd_handler.add_wish_to_list(vk_id=vk_id, product_id=product_id)
        except asyncpg.exceptions.DuplicateObjectError:
            return web.json_response({'status':'409','text':'Conflict'})
        except:
            response = jsoner(status=400)
            return web.json_response(response)
            
        response = jsoner(status=200)
        return web.json_response(response)

    # FULL READY   
    async def friend_wishlist(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            friend_id = data['friend_id'] 
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            result= await bd_handler.get_list_of_products(vk_id=friend_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)
        
        try:
            data = []
            async with Elasticsearch(elastic_settings) as es:
                for rec in result:
                    prod = {'product_id':rec['product_id'],'gift':rec['gift_id']}
                    res = await es.get(index='obi',doc_type='product', id=rec['product_id'])
                    prod.update(res['_source'])
                    data.append(prod)
        except: 
            return web.json_response({'status':'404','text':'NOT FOUND'})
        
        response = jsoner(status=200,wishlist=data,vk_id=vk_id)
        return web.json_response(response)
        # response = jsoner(status=200)
        # return web.json_response(response)

    # FULL READY
    async def gift(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            friend_id = data['friend_id']  
            product_id = data['product'] 
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            await bd_handler.to_gift(my_id=vk_id,friend_id=friend_id,product_id=product_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        response = jsoner(status=200)
        return web.json_response(response)

    # FULL READY
    async def user_gftlist(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            friend_id = data['friend_id']
            
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            result= await bd_handler.watch_gift_list(my_id= vk_id,friend_id = friend_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)
        print('friend',result)
        
        try:
            data = []
            async with Elasticsearch(elastic_settings) as es:
                for rec in result:
                    prod = {'product_id':rec}
                    res = await es.get(index='obi',doc_type='product', id=rec)
                    prod.update(res['_source'])
                    data.append(prod)
        except: 
            return web.json_response({'status':'404','text':'NOT FOUND'})

        response = jsoner(status=200,user_giftlist=data)
        return web.json_response(response)

    # TODO FULL READY
    async def giftlist(self, request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            result= await bd_handler.watch_gift_list(my_id= vk_id,friend_id = None)
            print('all',result)
        except:
            response = jsoner(status=400)
            return web.json_response(response)
        try:
            data = {}
            result= {'15987669': ['678']}
            async with Elasticsearch(elastic_settings) as es:
                for user, lst in result.items(): 
                    prod_list = []              
                    for prod_id in lst:
                        prod={"product_id":prod_id}
                        res = await es.get(index='obi',doc_type='product', id=prod_id)
                        prod.update(res['_source'])
                        prod_list.append(prod)
                    data[user]=prod_list
        except: 
            return web.json_response({'status':'404','text':'NOT FOUND'})

        response = jsoner(status=200,giftlist=data)
        return web.json_response(response)

    # FULL READY
    async def cancel_gift(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            friend_id = data['friend_id']  
            product_id = data['product'] 
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            await bd_handler.to_gift(my_id=None,friend_id=friend_id,product_id=product_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)
        
        response = jsoner(status=200)
        return web.json_response(response)

    # FULL READY
    async def cansel_wish(self,request):

        try:
            data = await request.json()
            vk_id = data['vk_id']
            token = data['app_token']
            access_token = data['access_token']
            product_id = data['product'] 
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        correct = await self.auth_.authorize(user_id = vk_id, access_token = access_token,sign=token)
        if correct.decode() == 'False':
            response = jsoner(status=403)
            return web.json_response(response)

        try: 
            await bd_handler.delete_wish(vk_id=vk_id,product_id=product_id)
        except:
            response = jsoner(status=400)
            return web.json_response(response)

        
        response = jsoner(status=200)
        return web.json_response(response)





app = web.Application()
handler = Handler()
app.add_routes([web.post('/signin', handler.auth),
                web.get('/mywishlist', handler.my_wishlist),
                web.post('/mywishlist', handler.adding_wish),
                web.delete('/mywishlist', handler.cansel_wish),
                web.get('/friendwishlist', handler.friend_wishlist),
                web.post('/friendwishlist',handler.gift),
                web.delete('/friendwishlist',handler.cancel_gift),
                web.get('/giftlist',handler.giftlist),
                web.get('/usergiftlist',handler.user_gftlist),
                web.get('/search',handler.search)])

web.run_app(app, port=3000)
