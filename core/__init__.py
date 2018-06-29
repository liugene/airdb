import json
from enum import Enum

#数据库核心模块序列化接口

class SerializedInterface:

    json : json

    #反序列化方法
    def deserialized(data):
        raise NotImplementedError

    #序列化方法
    def serialized(self):
        raise NotImplementedError


#字段类型枚举
class FieldType(Enum):

    INT = int = 'int'

    VARCHAR = varchar = 'varchar'

    FLOAT = float = 'float'


#数据类型映射

TYPE_MAP = {

    'int' : int,
    'float' : float,
    'str' : str,
    'INT' : int,
    'FLOAT' : float,
    'VARCHAR' : str

}


#字段主键枚举

class FieldKey(Enum):

    PRIMARY : 'PRIMARY KEY'

    INCREMENT : 'AUTO_INCREMENT'

    UNIQUE : 'UNIQUE'

    NOT_NULL : 'NOT NULL'

    NULL : 'NULL'