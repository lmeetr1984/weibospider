from django.apps import AppConfig

# 正常的配置管理应该是WeboConfigConfig 。。。
# 被这么一改，就不能被makemigraitons 同步了
class WeiboConfig(AppConfig):
    name = 'weibo_config'
    verbose_name = '微博配置'
