import asyncpg
import asyncio

from settings import postgres_settings

class PGConnector:

    conn = None
    database = 'postgres'
    user = "postgres"
    password = ""
    # host = "localhost"
    # port = "5432"
    host = postgres_settings['host']
    port = postgres_settings['port']

    @classmethod
    async def connect_(self, db=database,
                       user_=user,
                       password_=password,
                       host_=host,
                       port_=port):

        PGConnector.conn = await asyncpg.connect(database=db,
                                                 user=user_,
                                                 password=password_,
                                                 host=host_,
                                                 port=port_)

        # PGConnector.conn = await asyncpg.connect("postgresql://localhost:5432/vk_users",user = "postgres")


class Field():
    def __init__(self, f_type, required=False, default=None, pk=False):
        self.f_type = f_type
        self.required = required
        self.default = default
        self.pk = pk

    def validate(self, value):
        if value is None:
            if self.default is None and not self.required:
                return None
            elif self.default is None and self.required:
                raise ValueError("Field is required")
            elif self.default is not None:
                value = self.default
        try:
            self.f_type(value)
        except:
            raise TypeError(
                f"Value '{value}' cannot be converted to type '{self.f_type}'")
        return self.f_type(value)


class IntField(Field):

    pg_type = 'int'

    def __init__(self, required=False, default=None, pk=False):
        super().__init__(int, required, default, pk)


class StringField(Field):

    pg_type = 'text'

    def __init__(self, required=False, default=None, pk=False):
        super().__init__(str, required, default, pk)


class MetaModel(type):

    def __new__(mcs, name, bases, namespace):

        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')
        if not hasattr(meta, 'table_name'):
            raise ValueError('table_name is empty')
        if meta.table_name == "":
            meta.table_name = namespace.get("__qualname__")

        fields = {k: v for base in bases for k,
                  v in base.__dict__.items() if isinstance(v, Field)}
        new_fields = {k: v for k, v in namespace.items()
                      if isinstance(v, Field)}
        fields.update(new_fields)

        namespace['_fields'] = fields
        namespace['_table_name'] = meta.table_name
        namespace['objects'] = Manage()
        # print(namespace['_fields'])
        return super().__new__(mcs, name, bases, namespace)


class queryset():

    def __init__(self):
        self.query = ''
        self.table_name = ''
        self.cache = []
        self.filt = []
        self.current_item = 0
        self.num = 0

    def __aiter__(self):
        self.cache = []
        self.current_item = 0
        return self

    async def __anext__(self):

        if self.cache == []:
            self.cache = await PGConnector.conn.fetch(self.query, *self.filt)

        if self.current_item >= len(self.cache):
            raise StopAsyncIteration

        current = dict(self.cache[self.current_item])
        self.current_item += 1
        return current

    def get_all(self, *args,  table_name_):
        self.num = 0
        self.filt = []

        if self.table_name == '':
            self.table_name = table_name_
        if len(args) == 0:
            self.query = f'SELECT * FROM {self.table_name}'
        else:
            self.query = f"SELECT {', '.join(*args)} FROM {self.table_name}"
        return self

    def filter(self, dic=None, **kwargs):

        if len(kwargs) != 0:
            lst = []
            if 'WHERE' not in self.query:
                self.query += ' WHERE'
            else:
                self.query += ' AND'
            for key, value in kwargs.items():
                self.num += 1
                lst.append(f' {key} = ${self.num}')
                self.filt.append(value)
            self.query += ' AND'.join(lst)
        elif dic != None:
            lst = []
            if 'WHERE' not in self.query:
                self.query += ' WHERE'
            else:
                self.query += ' AND'
            for key, value in dic.items():
                self.num += 1
                lst.append(f' {key} = ${self.num}')
                self.filt.append(value)
            self.query += ' AND'.join(lst)
        return self

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.start != None:
                self.query += f' OFFSET {key.start}'
            if key.stop != None:
                self.query += f' LIMIT {key.stop}'
            if key.step != None:
                raise IndexError('Action is not allowed')
        else:
            raise IndexError('Action is not allowed')
        return self


class Manage:

    def __init__(self):
        self.model_cls = None
        self.queryset_ = queryset()
        self.queries = []
        self.querry = ''

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
            self.table_name = self.model_cls._table_name
        return self
        # self.model_cls = owner
        # self.table_name = self.model_cls._table_name
        # return self

    def select(self, *args):
        return self.queryset_.get_all(args, table_name_=self.table_name)

    async def create(self, **kwargs):

        self.queries = []
        keys = []

        for name_field, field in self.model_cls._fields.items():
            val = field.validate(kwargs.get(name_field))
            if val is not None:
                keys.append(name_field)
                self.queries.append(val)
        if len(self.queries) != 0:
            self.querry = f"INSERT INTO {self.table_name} ({', '.join(keys)}) VALUES ({', '.join([f'${n+1}' for n in range(len(self.queries))])});"
            # print(self.querry,keys,self.queries)
            await self.db_query()

    async def deleting(self, **kwargs):

        self.queries = []
        keys = []

        for name_field, field in self.model_cls._fields.items():
            val = field.validate(kwargs.get(name_field))
            if val is not None:
                keys.append(name_field)
                self.queries.append(val)
        if len(self.queries) != 0:
            self.querry = f"DELETE FROM {self.table_name} WHERE {' AND '.join([f'{keys[x]} = ${x+1}' for x in range(len(self.queries))])};"
            # print(self.querry, self.queries)
            await self.db_query()

    async def update(self, **kwargs):
        self.queries = []
        select = [x for x in kwargs.keys()]
        setting = select.pop()
        # n = 0
        try:
            field = self.model_cls._fields.get(setting)
        except:
            pass

        # print(sel.query)
        #  for name_field, field in self.model_cls._fields.items():
        self.queries.append(field.validate(kwargs.get(setting)))
        for value in select:
            self.queries.append(kwargs.get(value))
        self.querry = f"UPDATE {self.table_name} SET {setting} = $1 WHERE {' AND '.join([f'{select[x]} = ${x+2}' for x in range(len(select))])};"
        print(self.querry, self.queries)
        #
        #  await self.db_query()

        # if not field.pk:
        #     lol = {name_field:val}
        #     sel.filter(lol)
        #     kek = []
        #     async for res in sel:
        #         kek.append(res)
        #     if len(kek) != 0:
        #         select.append(name_field)
        #         # n+=1
        #     else:
        #         setting.append(name_field)
        #         self.queries.append(kwargs.get(name_field))
        # if len(setting) != 0:
        #     self.querry = f"UPDATE {self.table_name} SET {', '.join([f'{setting[x]} = ${x+1}' for x in range(len(setting))])}"
        #     # print(self.querry)
        # else:
        #     continue
        # if len(select) != 0:
        #     self.querry += f" WHERE {' AND '.join([f'{select[x]} = ${len(setting)+x+1}' for x in range(len(select))])};"
        #     for val in select:
        #         self.queries.append(kwargs.get(val))
        # print(self.querry, self.queries)
        await self.db_query()

    async def db_query(self):
        await PGConnector.conn.execute(self.querry, *self.queries)


class Model(metaclass=MetaModel):

    class Meta:
        table_name = ""

    # objects = Manage()

    def __init__(self, *_, **kwargs):

     # self.objects.create(bd,kwargs)
        for field_name, field in self._fields.items():
            value = field.validate(kwargs.get(field_name))
            setattr(self, field_name, value)

    # def save(self):
    #     for field_name, field in self._fields.items():
    #         if not field.pk:
    #             print(field_name)

    # async def update(self):
    #     pass

    # async def delete(self):
    #     pass


class User(Model):

    user_id = IntField(pk=True)
    vk_id = StringField()

    class Meta:
        table_name = "Users"


class Wish(Model):

    wish_id = IntField(pk=True)
    user_id = IntField()
    product_id = StringField(required=True)
    gift_id = StringField()

    class Meta:
        table_name = "Wish"