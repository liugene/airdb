from airdb.core import FieldType,FieldKey,TYPE_MAP
from airdb.core import SerializedInterface

#数据字段对象
class Field(SerializedInterface):

    def __init__(self, data_type, keys=FieldKey.Null, default=None):

        self.__type = data_type

        self.__keys = keys

        self.__default = default

        self.__values = []

        self.__row = 0

        #如果约束只有一个，并非list类型，则转化为list

        if not isinstance(self.__keys, list):

            self.__keys = [self.__keys]

        #如果类型不数据FieldType，则抛出异常

        if not isinstance(self.__type, FieldType):

            raise TypeError('Data-Type require type of "FieldType"')

        # 如果类型不数据FieldKey，则抛出异常

        for key in self.__keys:
            if not isinstance(key, FieldKey):
                raise TypeError('Data-Type require type of "FieldKey"')

        #如果有自增约束,判断数据类型是否为整型和是否有主键约束

        if FieldKey.INCREMENT in self.__keys:

            #如果不是整型，抛出类型错误异常

            if self.__type != FieldType.INT:

                raise TypeError('Increment key require Data-Type is integer')

            #如果没有主键约束，则抛出无主键约束异常

            if FieldKey.PRIMARY not in self.__keys:

                raise Exception('')

            #如果默认值不为空并且设置了唯一约束，抛出唯一约束不能设置默认值异常

            if self.__default is not None and FieldKey.UNIQUE in self.__keys:

                raise Exception('')


    #获取有多少条数据
    def length(self):

        return self.__row

    #获取数据
    def get_data(self, index=None):

        #如果index为整型,则返回指定位置的数据，反之则返回所有数据
        if index is not None and self.__check_index(index):

            return self.__values[index]

        #返回所有数据
        return self.__values

    #添加数据
    def add(self, value):

        #如果插入的数据为空，则为默认值
        if value is None:

            value = self.__default

        #判断数据是否符合约束条件
        value = self.__check_keys(value)

        #追加数据
        self.__values.append(value)

        #数据长度加1
        self.__row += 1

    #删除指定位置数据
    def delete(self, index):

        #如果删除的位置数据不存在，则抛出异常
        self.__check_index(index)

        #删除数据
        self.__values.pop(index)

        #数据流长度减1
        self.__row -= 1

    #修改指定位置数据
    def modify(self, index, value):

        #如果修改的位置小于0或者大于数据总长度，则抛出异常
        self.__check_index(index)

        #判断数据是否符合约束要求
        value = self.__check_keys(value)

        #如果修改的值类型不符合定义好的类型，则抛出异常
        self.__check_type(value)

        #修改数据
        self.__values[index] = value


    #键值约束
    def __check_keys(self, value):

        #如果字段包含自增键，则选择合适的值自动自增
        if FieldKey.INCREMENT in self.__keys:

            #如果值为空，则字段数据长度作为基值自增
            if value is None:
                value = self.__row + 1

            #如果值已经存在，则抛出一个值已经存在的异常

            if value in self.__values:

                raise Exception('')

            #如果字段包含主键主键约束或者唯一约束，判断值是否存在
            if FieldKey.PRIMARY in self.__keys or FieldKey.UNIQUE in self.__keys:

                #如果值存在，则抛出异常
                if value in self.__values:
                    raise Exception('')

            #如果字段包含主键或者非空键，并且添加的值为空值，则抛出值不能为空的异常
            if (FieldKey.PRIMARY in self.__keys or FieldKey.NOT_NULL in self.__keys) and value is None:
                raise Exception('')

            return value

    #判断数据类型是否符合
    def __check_type(self, value):

        #如果该值的类型不符合定义好的类型，抛出类型错误异常
        if value is None and not isinstance(value, TYPE_MAP[self.__type.value]):

            raise TypeError('')

    #判断指定位置数据是否存在
    def __check_index(self, index):

        #如果指定位置值不存在，则抛出异常
        if not isinstance(index, int) or not -index < self.__row > index:
            raise Exception('')

        return True

    #获取字段数据约束
    def get_keys(self):
        return self.__keys

    #获取字段类型
    def get_type(self):
        return self.__type

    #序列化对象
    def serialized(self):
        return SerializedInterface.json.dumps({
            'key' : [key.value for key in self.__keys], #数据约束
            'type' : self.__type.value, #数据类型
            'values' : self.__values, #数据
            'default' : self.__default #默认值
        })

    #反序列化对象
    def deserialized(data):

        #将数据转化为json对象
        json_data = SerializedInterface.json.loads(data)

        #转化json对象中key的值为枚举类FieldKey中的属性
        keys = [FieldKey[key] for key in json_data['key']]

        #传入解析出来的数据类型和字段键并实例化一个Field对象
        obj = Field(FieldType(json_data['type']), keys, default=json_data['default'])

        #为Field对象绑定数据
        for value in json_data['values']:
            obj.add(value)

        return obj