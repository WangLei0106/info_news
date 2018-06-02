import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect,generate_csrf
from redis import StrictRedis
from config import configs
from info.utils.comment import do_rank
import pymysql
pymysql.install_as_MySQLdb()
# 创建SQLAlchemy对象
db = SQLAlchemy()


def setup_log(level):
    """根据创建app时的配置环境加载日志等级"""
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


redis_store = None


def create_app(config_name):

    # 创建app
    app = Flask(__name__)


    # 设置ＤＥＢＵＧ等级
    setup_log(configs[config_name].LEVE_LOG)

    # 获取配置信息
    app.config.from_object(configs[config_name])

    # 创建连接到Mysql数据库对象
    # db = SQLAlchemy(app)
    db.init_app(app)
    # 创建连接到redis数据库对象
    global redis_store
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT, decode_responses=True)

    # 创建CSRF保护
    CSRFProtect(app)
    # 使用请求钩子实现每个响应中写入ｃｏｏｋｉｅ
    @app.after_request
    def setup_csrftoken(response):
        # 生成csrf_token的值
        csrf_token = generate_csrf()
        # 将csrf_token的值写入cookie
        response.set_cookie('csrf_token',csrf_token)
        return response


    # 将自定义的过滤器添加到指定的过滤器列表中
    app.add_template_filter(do_rank, 'rank')

    # 指定Session数据存储在后端的位置
    Session(app)

    # 注册蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    from info.modules.news import news_blue
    app.register_blueprint(news_blue)

    return app
