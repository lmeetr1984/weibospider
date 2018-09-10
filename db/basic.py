import os

from sqlalchemy import (
    create_engine, MetaData)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import get_db_args


def get_engine():
    args = get_db_args()
    password = os.getenv('DB_PASS', args['password'])
    connect_str = "{}+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(args['db_type'], args['user'], password,
                                                             args['host'], args['port'], args['db_name'])

    # 创建引擎，返回
    engine = create_engine(connect_str, encoding='utf-8')
    return engine

# sqlalchemy engine
eng = get_engine()

# 声明base
Base = declarative_base()

# session类
Session = sessionmaker(bind=eng)

# 创建一个session
db_session = Session()

# meta
metadata = MetaData(get_engine())

# 声明需要export的变量
__all__ = ['eng', 'Base', 'db_session', 'metadata']
