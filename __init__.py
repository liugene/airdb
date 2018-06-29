import base64,os,prettytable
from airdb.core import SerializedInterface
from airdb.core.database import Database
from airdb.parser import SQLParser

#解码数据
def _decode_db(content):
    b_content = base64.decodebytes(content)
    return b_content.decode()[::-1]

#编码数据
def _encode_db(content):
    b_content = content[::-1].encode()
    return base64.encodebytes(b_content)

#数据库引擎
class Engine:

    def __init__(self, db_name=None, format_type='dict', path='db.data'):

        self.__database_obj = {}  # 数据库映射表

        self.__database_name = []  # 数据库名字集合

        self.__current_db = None # 标示当前使用的数据库

        self.path = path  # 数据库存放路径名

        self.__format_type = format_type  # 数据默认返回格式

        self.__load_databases()

        #数据库映射表
        self.__action_map = {

            'search': self.__search,
            'update': self.__update,
            'delete': self.__delete,
            'insert': self.__insert,
            'use': self.__use,
            'exit': self.__exit,
            'show': self.__show,
            'drop': self.__drop

        }

        # 如果初始化时数据库名字参数不为空，调用 select_db 方法选中数据库
        if db_name is not None:
            self.select_db(db_name)

    #创建数据库
    def create_database(self, database_name):

        # 判断数据库名字是否存在，如果存在，抛出数据库已存在异常
        if database_name in self.__database_name:
            raise Exception('')

        # 追加数据库名字
        self.__database_name.append(database_name)

        # 关联数据库对象和数据库名
        self.__database_name[database_name] = Database(database_name)

    #删除数据库
    def drop_database(self, database_name):

        # 如果数据库名字不存在，则抛出数据库不存在异常
        if database_name not in self.__database_obj:

            raise Exception('')

        # 从数据库名字集合中移除
        self.__database_name.remove(database_name)

        # 移除数据库名和对象的映射
        self.__database_obj.pop(database_name, True)

    #选择数据库
    def select_db(self, db_name):

        # 如果不存在该数据库索引，抛出数据库不存在异常
        if db_name not in self.__database_obj:
            raise Exception('')

        # 将对应名字的 Database 对象赋值给 __current_db
        self.__current_db = self.__database_obj[db_name]

    #序列化数据库
    def serialized(self):

        return SerializedInterface.json.dumps([
            database.serialized() for database in self.__database_obj.values()
        ])

    #保存数据库
    def __dump_databases(self):

        with open(self.path, 'wb') as f:

            # 编码 Json 字符串
            content = _encode_db(self.serialized())

            # 保存数据到本地
            f.write(content)

    #反序列化数据库
    def deserialized(self, data):

        #解析Json数据
        json_data = SerializedInterface.json.loads(data)

        # 因为每一条就是一个 Database 对象的 Json 数据，所以直接遍历再调用 Database 的反序列化方法就行了
        for obj in json_data:

            # 实例化 Database
            database = Database.deserialized(obj)

            # 获取数据库名字
            db_name = database.get_name()

            # 追加数据库名字和绑定数据库对象
            self.__database_name.append(db_name)

            self.__database_obj[db_name] = database

    #加载数据库
    def __load_databases(self):

        # 如果数据文件不存在，则直接退出
        if not os.path.exists(self.path):
            return

        # 读取文件数据
        with open(self.path, 'rb') as f:
            content = f.read()

            # 如果数据不为空
            if content:

                # 解码数据，并把数据传给反序列化函数
                self.deserialized(_decode_db(content))

    # 提交数据库改动
    def commit(self):
        self.__dump_databases()

    # 回滚数据库改动
    def rollback(self):
        self.__load_databases()

    # 查询指定数据表数据
    def search(self, table_name, field='*', sort='ASC', **conditions):
        # 通过数据表名字获取指定的 Table 对象，再调用它的 search 方法获取查询结果
        return self.__get_table(table_name).search(field, sort, format_type= self.__format_type, **conditions)

    # 获取数据表
    def __get_table(self, table_name):

        # 判断当前是否有选中的数据库
        self.__check_is_choose()

        # 获取对应的 Table 对象
        table = self.__current_db.get_table_obj(table_name)

        # 如果 Table 对象为空，抛出异常
        if table is None:
            raise Exception('')

        #返回Table对象
        return table

    def __check_is_choose(self):

        # 如果当前没有选中的数据库，抛出为选择数据库异常
        if not self.__current_db or not isinstance(self.__current_db, Database):
            raise Exception('No Database Choose')

    #插入数据
    def insert(self, table_name, **data):
        return self.__get_table(table_name).insert(**data)

    #更新数据
    def update(self, table_name, data, **conditions):
        return self.__get_table(table_name).update(data, **conditions)

    #删除数据
    def delete(self, table_name, **conditions):
        return self.__get_table(table_name).delete(**conditions)

    #创建数据表
    def create_table(self, name, **options):
        self.__check_is_choose()
        self.__current_db.create_table(name, **options)

    #获取数据库名
    def get_database(self, format_type='list'):
        databases = self.__database_name

        if format_type == 'dict':
            tmp = []
            for database in databases:
                tmp.append({'name':database})

            databases = tmp

        return databases

    #根据指定的返回格式获取当前使用数据库的所有数据表
    def get_table(self, format_type='list'):
        self.__check_is_choose()

        tables = self.__current_db.get_table()

        if format_type == 'dict':
            tmp = []

            for table in tables:
                tmp.append({'name':table})

            tables = tmp

        return tables

    def __insert(self, action):

        table = action['table']
        data = action['data']

        return self.insert(table, data=data)

    def __update(self, action):

        table = action['table']
        data = action['data']
        conditions = action['conditions']

        return self.update(table, data, conditions=conditions)

    def __delete(self, action):

        table = action['table']
        conditions = action['conditions']

        return self.delete(table, conditions=conditions)

    def __search(self, action):

        table = action['table']
        fields = action['fields']
        conditions = action['conditions']

        return self.search(table, fields, conditions=conditions)

    def __drop(self, action):
        if action['kind'] == 'database':
            return self.drop_database(action['name'])

        return self.drop_table(action['name'])

    def __show(self, action):
        if action['kind'] == 'database':
            return self.get_database(format_type='dict')

        return self.get_table(format_type='dict')

    def __use(self, action):
        return self.select_db(action['database'])

    def __exit(self, _):
        return 'exit'

    def execute(self, statement):

        action = SQLParser.parse(statement)

        ret = None

        if action['type'] in self.__action_map:

            ret = self.__action_map.get(action['type'])(action)

            if action['type'] in ['insert', 'update', 'delete', 'create', 'drop']:
                self.commit()

        #返回执行结果
        return ret

    def run(self):

        while True:
            #获取sql语句
            statement = input('\033[00;37misadb> ')

            try:
                ret = self.execute(statement)

                if ret in ['exit', 'quit']:
                    print('GoodBye')
                    return

                if ret:
                    pt = prettytable.PrettyTable(ret[0].key())
                    pt.align = 'l'
                    for line in ret:
                        pt.align = 'r'
                        pt.add_row(line.values())

                    print(pt)

            except Exception as exc:
                print('\033[00;31m' + str(exc))
