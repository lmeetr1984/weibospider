import re
import os
import rsa
import math
import time
import random
import base64
import binascii
from urllib.parse import quote_plus

import requests

from config import headers
from utils import (code_verificate, getip)
from page_parse import is_403
from exceptions import LoginException
from db.redis_db import Cookies
from db.dao import LoginInfoOper
from config import (
    get_code_username, get_code_password)
from logger import (
    crawler, other)

# 验证码的路径
VERIFY_CODE_PATH = './{}{}.png'

YUMDAMA_USERNAME = os.getenv('YUMDAMA_ACCOUNT') or get_code_username()
YUMDAMA_PASSWORD = os.getenv('YUMDAMA_PASS') or get_code_password()

# 获取验证码url
def get_pincode_url(pcid):
    size = 0
    url = "http://login.sina.com.cn/cgi/pin.php"
    pincode_url = '{}?r={}&s={}&p={}'.format(url, math.floor(random.random() * 100000000), size, pcid)
    return pincode_url


def get_img(url, name, retry_count, proxy):
    """
    :param url: url for verification code
    :param name: login account
    :param retry_count: retry number for getting verfication code
    :return: 
    """
    pincode_name = VERIFY_CODE_PATH.format(name, retry_count)
    # 获取验证码图片
    resp = requests.get(url, headers=headers, stream=True, proxies=proxy)

    # 保存图片
    with open(pincode_name, 'wb') as f:
        for chunk in resp.iter_content(1000):
            f.write(chunk)

    # 返回验证码保存的图片在本地的名称路径
    return pincode_name


def get_encodename(name):
    # name must be string
    # 把空格、& * 这样的符号进行转义
    username_quote = quote_plus(str(name))
    # base64 加密
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))

    # 然后再还原成字符串
    return username_base64.decode("utf-8")


# prelogin for servertime, nonce, pubkey, rsakv
# 预登陆
def get_server_data(su, session, proxy):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_="

    # 请求的时间戳
    prelogin_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(prelogin_url, headers=headers, proxies=proxy)

    # 把返回的数据变成python的dict类型
    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


# 加密password
# var f = new sinaSSOEncoder.RSAKey;
# f.setPublic(me.rsaPubkey, "10001");
# b = f.encrypt([me.servertime, me.nonce].join("\t") + "\n" + b)
def get_password(password, servertime, nonce, pubkey):
    # 根据js的翻译，就是把2个字符串用16进制转换成数字
    rsa_publickey = int(pubkey, 16)
    key = rsa.PublicKey(rsa_publickey, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)
    passwd = binascii.b2a_hex(passwd)
    return passwd


# post data and get the next url
# 执行登录post，然后获取wiebo的最后一个需要redirect的url
def get_redirect(name, data, post_url, session, proxy):
    # 提交登录请求，在session中
    logining_page = session.post(post_url, data=data, headers=headers, proxies=proxy)

    # 解析登录信息
    login_loop = logining_page.content.decode("GBK")

    # if name or password is wrong, set the value to 2
    if 'retcode=101' in login_loop:
        crawler.error('invalid password for {}, please ensure your account and password'.format(name))
        LoginInfoOper.freeze_account(name, 2)
        return ''

    if 'retcode=2070' in login_loop:
        crawler.error('invalid verification code')
        return 'pinerror'

    if 'retcode=4049' in login_loop:
        crawler.warning('account {} need verification for login'.format(name))
        return 'login_need_pincode'

    if '正在登录' in login_loop or 'Signing in' in login_loop:
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        return re.findall(pa, login_loop)[0]
    else:
        return ''


def login_no_pincode(name, password, session, server_data, proxy):
    # 直接登录，不需要pincode
    post_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    servertime = server_data["servertime"]
    nonce = server_data['nonce']
    rsakv = server_data["rsakv"]
    pubkey = server_data["pubkey"]
    sp = get_password(password, servertime, nonce, pubkey)

    data = {
        'encoding': 'UTF-8',
        'entry': 'weibo',
        'from': '',
        'gateway': '1',
        'nonce': nonce,
        'pagerefer': "",
        'prelt': 67,
        'pwencode': 'rsa2',
        "returntype": "META",
        'rsakv': rsakv,
        'savestate': '7',
        'servertime': servertime,
        'service': 'miniblog',
        'sp': sp,
        'sr': '1920*1080',
        'su': get_encodename(name),
        'useticket': '1',
        'vsnf': '1',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'
    }

    rs = get_redirect(name, data, post_url, session, proxy)

    return rs, None, '', session


def login_by_pincode(name, password, session, server_data, retry_count, proxy):
    # 登录url post
    post_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'

    servertime = server_data["servertime"]
    nonce = server_data['nonce']
    rsakv = server_data["rsakv"]
    pubkey = server_data["pubkey"]
    pcid = server_data['pcid']

    # 登录的password需要特别处理一下
    sp = get_password(password, servertime, nonce, pubkey)

    data = {
        'encoding': 'UTF-8',
        'entry': 'weibo',
        'from': '',
        'gateway': '1',
        'nonce': nonce,
        'pagerefer': "",
        'prelt': 67,
        'pwencode': 'rsa2',
        "returntype": "META",
        'rsakv': rsakv,
        'savestate': '7',
        'servertime': servertime,
        'service': 'miniblog',
        'sp': sp,
        'sr': '1920*1080',
        'su': get_encodename(name),
        'useticket': '1',
        'vsnf': '1',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'pcid': pcid  # 验证码id
    }

    if not YUMDAMA_USERNAME:
        raise LoginException('Login need verfication code, please set your yumdama info in config/spider.yaml')
    img_url = get_pincode_url(pcid)

    # 获取验证码图片
    pincode_name = get_img(img_url, name, retry_count, proxy)


    verify_code, yundama_obj, cid = code_verificate(YUMDAMA_USERNAME, YUMDAMA_PASSWORD, pincode_name)
    data['door'] = verify_code # 把识别的数据弄到post form中


    rs = get_redirect(name, data, post_url, session, proxy)

    # 删除图片
    os.remove(pincode_name)
    return rs, yundama_obj, cid, session


def login_retry(name, password, session, ydm_obj, cid, proxy, rs='pinerror', retry_count=0):
    while rs == 'pinerror':
        ydm_obj.report_error(cid)
        retry_count += 1
        session = requests.Session()
        su = get_encodename(name)
        server_data = get_server_data(su, session, proxy)
        rs, yundama_obj, cid, session = login_by_pincode(name, password, session, server_data, retry_count, proxy)
    return rs, ydm_obj, cid, session

# 执行登录
def do_login(name, password, proxy):
    # 创建一个requests的session
    session = requests.Session()

    # 获取加密好的用户名，也就是预登陆的su参数
    su = get_encodename(name)

    # 获取预登陆的服务器返回数据是
    server_data = get_server_data(su, session, proxy)

    # 如果返回数据显示需要pincode，那么需要云打码
    if server_data['showpin']:
        # 尝试使用云打码登录
        rs, yundama_obj, cid, session = login_by_pincode(name, password, session, server_data, 0, proxy)

        # 如果返回的是pincode error
        if rs == 'pinerror':
            # 循环尝试登录，知道登录为止
            rs, yundama_obj, cid, session = login_retry(name, password, session, yundama_obj, cid, proxy)

    else:
        rs, yundama_obj, cid, session = login_no_pincode(name, password, session, server_data, proxy)

        # 如果需要一个pincode
        if rs == 'login_need_pincode':
            session = requests.Session() #创建一个新的session
            su = get_encodename(name)

            # 开始云打码的方式运行登录
            server_data = get_server_data(su, session, proxy)
            rs, yundama_obj, cid, session = login_by_pincode(name, password, session, server_data, 0, proxy)

            if rs == 'pinerror':
                rs, yundama_obj, cid, session = login_retry(name, password, session, yundama_obj, cid, proxy)

    return rs, yundama_obj, cid, session


def get_session(name, password):
    proxy = getip.getIP("")

    url, yundama_obj, cid, session = do_login(name, password, proxy)

    # 这个url就是需要redirect的url
    if url != '':
        # 请求这个url
        rs_cont = session.get(url, headers=headers, proxies=proxy)
        login_info = rs_cont.text

        # 找到uniqueid 这个字段
        u_pattern = r'"uniqueid":"(.*)",'
        m = re.search(u_pattern, login_info)
        if m and m.group(1):
            # check if account is valid
            check_url = 'http://weibo.com/2671109275/about'
            resp = session.get(check_url, headers=headers, proxies=proxy)

            if is_403(resp.text):
                other.error('account {} has been forbidden'.format(name))
                LoginInfoOper.freeze_account(name, 0)
                return None
            other.info('Login successful! The login account is {}'.format(name))

            # 保存cookie信息 到redis中
            Cookies.store_cookies(name, session.cookies.get_dict(), proxy['http'])
            return session
        
    other.error('login failed for {}'.format(name))
    return None
