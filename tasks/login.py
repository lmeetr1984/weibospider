import time

from db.redis_db import Cookies
from logger import crawler
from login import get_session
from db.dao import LoginInfoOper
from .workers import app

# 通过@app.task创建一个任务
# ignore_result： 不保存返回值
# 这个任务，属于监听消息队列的任务，属于消费者
@app.task(ignore_result=True)
def login_task(name, password):
    get_session(name, password)


# 这个任务，属于消费者，负责生产消息的
# There should be login interval, if too many accounts login at the same time from the same ip, all the
# accounts can be banned by weibo's anti-cheating system
@app.task(ignore_result=True)
def execute_login_task():
    # 获取所有的需要登录的weibo账号信息
    infos = LoginInfoOper.get_login_info()
    # Clear all stacked login tasks before each time for login
    Cookies.check_login_task()
    crawler.info('The login task is starting...')
    for info in infos:
        # 对xx任务 发送参数args
        # 让这个任务启动
        # queue参数：表示通过这个队列来路由通知任务
        # 路由的key由参数routing_key 指定
        app.send_task('tasks.login.login_task', args=(info.name, info.password), queue='login_queue',
                      routing_key='for_login')
        time.sleep(10)

