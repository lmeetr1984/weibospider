import os
import random
from pathlib import Path

from yaml import load

# 构造爬虫用的配置文件路径
config_path = os.path.join(os.path.dirname(__file__), 'spider.yaml')

# 打开文件
with open(config_path, encoding='utf-8') as f:
    cont = f.read()

# 加载yaml
cf = load(cont)

# 获取db相关的配置信息
def get_db_args():
    return cf.get('db')

# 获取redis相关的配置信息
def get_redis_args():
    return cf.get('redis')

# 获取timeout的配置
def get_timeout():
    return cf.get('time_out')

# 获取多久爬去一次
def get_crawl_interal():
    interal = random.randint(cf.get('min_crawl_interal'), cf.get('max_crawl_interal'))
    return interal

# 如果得到了异常，睡眠多久才能再次爬取
def get_excp_interal():
    return cf.get('excp_interal')

# 最多爬取的微博信息
def get_max_repost_page():
    return cf.get('max_repost_page')

# 获取最大的search的页数
# 默认50页
def get_max_search_page():
    return cf.get('max_search_page')


def get_max_home_page():
    return cf.get('max_home_page')


def get_max_comment_page():
    return cf.get('max_comment_page')


def get_max_dialogue_page():
    return cf.get('max_dialogue_page')

# 最大的尝试次数
def get_max_retries():
    return cf.get('max_retries')


def get_broker_and_backend():
    redis_info = cf.get('redis')
    password = redis_info.get('password')

    # Redis Sentinel是一个分布式架构，包含若干个Sentinel节点和Redis数据节点，
    # 每个Sentinel节点会对数据节点和其余Sentinel节点进行监控，当发现节点不可达时，会对节点做下线标识。
    sentinel_args = redis_info.get('sentinel', '') #
    db = redis_info.get('broker', 5)
    if sentinel_args:
        broker_url = ";".join('sentinel://:{}@{}:{}/{}'.format(password, sentinel['host'], sentinel['port'], db) for
                              sentinel in sentinel_args)
        return broker_url
    else:
        host = redis_info.get('host')
        port = redis_info.get('port')
        backend_db = redis_info.get('backend', 6)
        broker_url = 'redis://:{}@{}:{}/{}'.format(password, host, port, db)
        backend_url = 'redis://:{}@{}:{}/{}'.format(password, host, port, backend_db)
        return broker_url, backend_url

# redis主节点
def get_redis_master():
    return cf.get('redis').get('master', '')

# 云打码的相关信息
def get_code_username():
    return cf.get('yundama_username')


def get_code_password():
    return cf.get('yundama_passwd')

# 运行方式：normal的话，被ban的概率会降低的
def get_running_mode():
    return cf.get('running_mode')

# 爬取模式：如果是normal， 不会触发点击查看的link，这样的话，速度快
def get_crawling_mode():
    return cf.get('crawling_mode')

# 用于爬取的登录账号个数
def get_share_host_count():
    return cf.get('share_host_count')

# cooki过期时间，单位：小时
def get_cookie_expire_time():
    return cf.get('cookie_expire_time')


def get_email_args():
    return cf.get('email')

# 是否下载图片
def get_images_allow():
    return cf.get('images_allow')

# 保存图片的位置
def get_images_path():
    img_dir = cf.get('images_path') if cf.get('images_path') else os.path.join(str(Path.home()), 'weibospider', 'images')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    return img_dir

# 保存图片的大小
def get_images_type():
    return cf.get('image_type')

# 获取after xxx时间的微博
def get_time_after():
    return cf.get('time_after')

def get_samefollow_uid():
    return cf.get('samefollow_uid')
