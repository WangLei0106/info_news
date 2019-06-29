import logging
from redis import StrictRedis





class Config():
    """配置文件的加载"""

    # 项目密钥
    SECRET_KEY = 'ehiLjcHpZ/UuWKecpFlqI+zQ5JnFkYfJH/PXd2sW91ok/kdhirOjxbaIhyokqQcl'

    # 开启调试模式
    DEBUG = True

    # 配置链接到MySQL数据库对象
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/info_29'
    a = 14
    # 不去追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis数据库:redis模块自己配置的参数
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # Session配置指定使用类型存储
    SESSION_TYPE = 'redis'
    # 指定Session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否使用secret_key签名ｓｅｓｓｉｏｎ
    SESSION_USE_SIGNER = True
    # 设置过期时间，要求'SESSION_PERMANENT'Ture,默认３１天
    PERMANENT_SESSION_LIFETIME = 60*60*24 # 一天有效


# 以下代码封装不同的开发环境下的配置信息

class DevlopmentConfig(Config):
    """开发环境"""

    LEVE_LOG = logging.DEBUG #　开发环境与父类一致


class ProductionConfig(Config):
    """生产环境"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql:root:mysql@127.0.0.1:3306/info_pro_29'
    LEVE_LOG = logging.ERROR


class UnittestConfig(Config):
    """测试环境"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql:root:mysql@127.0.0.1:3306/info_test_29'
LEVE_LOG = logging.DEBUG


# 定义字典，存储关键字存储不同的配置类类名
configs = {
    'dev':DevlopmentConfig,
    'pro':ProductionConfig,
    'unit':UnittestConfig
}

