import sys

# to work well inside config module or outsize config module
# 把本层和上层都当做系统package目录
sys.path.append('..')
sys.path.append('.')

from db.tables import *
from db.basic import metadata

# 创建爬虫用的表
def create_all_table():
    metadata.create_all()


if __name__ == "__main__":
    create_all_table()
