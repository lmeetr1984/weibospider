import os

# 安装pymysql， 因为python3 这是唯一的mysql驱动
# 固定写法，这样就可以在django中直接使用mysql / mariadb了
import pymysql
pymysql.install_as_MySQLdb()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = ')eh35!-%(@%o0q6unr8#a$44l6+&y14(5m#y&ug)-h@#usy=x3'

DEBUG = True

# 允许所有的访问
ALLOWED_HOSTS = [
    '*',
]

INSTALLED_APPS = [
    'suit', #admin-suit
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weibo_config.apps.WeiboConfig', # weibo配置app
    'weibo_data.apps.WeiboDataConfig' # weibo数据app
]
MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 配置url
ROOT_URLCONF = 'weibo_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# wsgi入口文件
WSGI_APPLICATION = 'weibo_admin.wsgi.application'


# 配置数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'weibo',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# 密码验证器，用来测试django user 的密码其强度的
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# 设置中文的
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# suit在admin里设置时间的一个小bug。需要把时间格式指定一下
# 参考https://django-suit.readthedocs.io/en/develop/

# 设置日期/时间戳的格式
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'

SUIT_CONFIG = {
  'ADMIN_NAME': '微博爬虫平台',
  'LIST_PER_PAGE': 10,
  'MENU': (
    'sites',
    {'app': 'weibo_config', 'label': '微博配置'},
    {'app': 'weibo_data', 'label': '微博数据'},
    {'app': 'auth', 'label': '认证管理'},
  ),
}

# URL to use when referring to static files located in STATIC_ROOT.
STATIC_URL = '/static/'
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')