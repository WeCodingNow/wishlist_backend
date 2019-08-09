import asyncio
import async_orm
import asyncpg

from settings import postgres_settings

class bd_handler:

    @classmethod
    async def set_connection(self, db='postgres', user_='postgres', password_='', host_=postgres_settings['host'], port_=postgres_settings['port']):
        print(f'attempting to connect at {host_}')
        await async_orm.PGConnector.connect_(db=db, user_=user_, password_=password_, host_=host_,port_=port_)
        print(f'connected to db at {host_}')
        # PGConnector.conn = await asyncpg.connect(database=db,user=user_,password=password_,host=host_,port=port_)

    @classmethod
    async def getting_id(self, vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = async_orm.User.objects.select('user_id').filter(vk_id=vk_id)
        result = [line async for line in res]
        return result

    @classmethod
    async def getting_products(self, user_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()
        
        res = async_orm.Wish.objects.select('product_id','gift_id').filter(user_id = user_id)
        # print(res.query)
        result = [line async for line in res]
        # print(result)
        return result 

    @classmethod
    async def checking_log(self, user_id, product_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = async_orm.Wish.objects.select('product_id','gift_id').filter(user_id = user_id).filter(product_id=product_id)
        result = [line async for line in res]
        return result 

    @classmethod
    async def adding_user(self,vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        await async_orm.User.objects.create(vk_id=vk_id)

    @classmethod
    async def addingwish(self,product_id,user_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        try:
            await async_orm.Wish.objects.create(product_id=product_id,user_id=user_id)
        except asyncpg.exceptions.ForeignKeyViolationError:
            raise ValueError('There is no such user')

    @classmethod
    async def updating(self,user_id, product_id, vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        await async_orm.Wish.objects.update(user_id = user_id,product_id = product_id, gift_id = vk_id)

    @classmethod
    async def get_vk(self,user_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = async_orm.User.objects.select('vk_id').filter(user_id=user_id)
        result = [line async for line in res]
        return result

    @classmethod
    async def giftlist(self,vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = async_orm.Wish.objects.select('product_id','user_id').filter(gift_id = vk_id)
        result = [line async for line in res]
        return result 

    @classmethod
    async def giftlist_for_user(self,vk_id,user_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = async_orm.Wish.objects.select('product_id').filter(gift_id = vk_id).filter(user_id=user_id)
        result = [line async for line in res]
        return result 

    @classmethod
    async def get_list_of_products(self,vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = await self.getting_id(vk_id)
        id = int(res[0]['user_id'])
        res = await self.getting_products(user_id = id) 
        return res

    @classmethod
    async def add_wish_to_list(self,vk_id,product_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = await self.getting_id(vk_id)
        if len(res) == 0:
            raise asyncpg.exceptions.NoDataFoundError('No users found')
        id = res[0]['user_id']
        await self.addingwish(product_id=product_id,user_id=id)

    @classmethod
    async def to_gift(self,my_id,friend_id,product_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()
                
        res = await self.getting_id(vk_id=friend_id)
        if len(res) == 0:
            raise asyncpg.exceptions.NoDataFoundError(f'No user with vk_id = {friend_id} found')
        id = res[0]['user_id']

        await self.updating(user_id=id,product_id=product_id,vk_id=my_id)

    @classmethod
    async def watch_gift_list(self,my_id,friend_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        if friend_id is None:
            res = await self.giftlist(vk_id=my_id)
            result = {}
            for record in res: 
                res2 = await self.get_vk(user_id=record['user_id'])
                vk = res2[0]['vk_id']
                if vk not in result.keys():
                    lst = [record['product_id']]
                    result[vk] = lst
                else:
                    result[vk].append(record['product_id'])
        else:
            res = await self.getting_id(vk_id=friend_id)
            id = res[0]['user_id']
            res = await self.giftlist_for_user(vk_id=my_id,user_id = id)
            result=[]
            for prod in res:
                result.append(prod['product_id'])
        return result

    @classmethod
    async def deleting_log(self,product_id,user_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        await async_orm.Wish.objects.deleting(product_id=product_id,user_id=user_id)

    @classmethod
    async def delete_wish(self,product_id,vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = await self.getting_id(vk_id=vk_id)
        id=res[0]['user_id']

        res = await self.checking_log(product_id=product_id,user_id = id)
        if len(res) !=0:
            await self.deleting_log(product_id=product_id, user_id = id)
        else: 
            raise asyncpg.exceptions.NoData('There id no wishes to delete')

    @classmethod
    async def authorisation(self,vk_id):
        if async_orm.PGConnector.conn == None:
            await self.set_connection()

        res = await self.getting_id(vk_id=vk_id)

        if len(res) == 0: 
            await self.adding_user(vk_id=vk_id)
