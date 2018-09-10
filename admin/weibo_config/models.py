from django.db import models

# 主要是配合做微博话题搜索使用
class Keywords(models.Model):
    keyword = models.CharField('关键词', max_length=200, unique=True)
    enable = models.IntegerField('是否启用', default=1)

    def __str__(self):
        return self.keyword

    class Meta:
        # 数据库表
        db_table = 'keywords'
        verbose_name = '关键词'
        verbose_name_plural = '关键词'
        app_label = 'weibo_config' # 告诉django，这个model属于哪个app

# 该表主要管理微博账号和密码
class LoginInFo(models.Model):
    name = models.CharField('用户名', max_length=100, unique=True)
    password = models.CharField('密码', max_length=200)
    enable = models.IntegerField('是否启用', default=1)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'login_info'
        verbose_name = '微博登陆账号'
        verbose_name_plural = '微博登陆账号'
        app_label = 'weibo_config'

# 主要存储种子用户，根据该表可抓取种子用户信息、
# 种子用户的主页所有原创微博及其相关粉丝和关注
class Seeds(models.Model):
    uid = models.CharField('用户ID', max_length=20, unique=True, blank=False)
    is_crawled = models.IntegerField('是否已采集个人信息', default=0)
    other_crawled = models.IntegerField('是否已采集粉丝和关注', default=0)
    home_crawled = models.IntegerField('是否已采集主页', default=0)

    def __str__(self):
        return self.uid

    class Meta:
        db_table = 'seed_ids'
        verbose_name = '要采集的账号'
        verbose_name_plural = '要采集的账号'
        app_label = 'weibo_config'



