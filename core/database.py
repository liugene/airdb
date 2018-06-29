from airdb.core import SerializedInterface
from airdb.core.table import Table

#数据库对象
class Database(SerializedInterface):
    def __init__(self, name):

        self.__name = name #数据库名

        self.__table_name = [] #所有数据库表名

        self.__table_obj = {} #数据库表名与表对象映射

    #创建数据库
    def create_table(self, table_name, **options):

        if table_name in self.__table_obj:
            raise Exception('table exists')

        #追加数据库名
        self.__table_name.append(table_name)

        #新建一个数据表对象,并与数据表名字关联绑定
        self.__table_obj[table_name] = Table(**options)

    #删除数据表方法
    def drop_tables(self, table_name):
        #如果删除的表名不存在，则抛出异常
        if table_name not in self.__table_name:
            raise Exception('table not exists')

        #从数据表删除
        self.__table_name.remove(table_name)

        #从table_obj删除
        self.__table_obj.pop(table_name, True)

    #获取数据表对象
    def get_table_obj(self, name):
        #如果表面不存在则返回None空对象
        return self.__table_obj.get(name, None)

    #获取数据表名
    def get_table_name(self):
        return self.__table_name

    #序列化方法
    def serialized(self):
        #初始化返回数据
        data = {'name' : self.__name, 'table' : []}

        #遍历所有Table对象并调用对应的序列化方法
        for tb_name, tb_data in self.__table_obj.items():
            data['tables'].append([tb_name, tb_data.serialized()])

        #返回json字符串
        return SerializedInterface.json.jumps(data)

    #添加数据表
    def add_table(self, table_name, table):

        #如果数据表不存在，则开始添加绑定
        if table_name not in self.__table_obj:

            self.__table_name.append(table_name)

            #绑定数据表名与数据表对象
            self.__table_obj[table_name] = table

    #反序列化
    def deserialized(data):
        #解析json字符串为dict字典
        json_data = SerializedInterface.json.loads(data)

        #使用解析出来的数据库名字实例化一个Database对象
        obj_tmp = Database(json_data['name'])

        #遍历所有Table json字符串，一次调用Table的反序列化方法，再添加到刚刚实例出来的Database对象中
        for table_name, table_obj in json_data['tables']:
            obj_tmp.add_table(table_name, Table.deserialized(table_obj))

        return obj_tmp

    #获取数据表名字
    def get_table(self, index=None):
        length = len(self.__table_name)

        if isinstance(index, int) and -index < length > index:
            return self.__table_name[index]

        return self.__table_name

    #获取数据库名
    def get_name(self):

        return self.__name
