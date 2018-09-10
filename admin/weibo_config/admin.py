from django.contrib import admin

from .models import Keywords, LoginInFo, Seeds


class KeywordsAdmin(admin.ModelAdmin):
    # 列表的字段
    list_display = ('keyword', 'enable')
    # 可以被搜索的字段
    search_fields = ['keyword']
    # 每页的个数
    list_per_page = 20


class LoginInFoAdmin(admin.ModelAdmin):
    list_display = ('name', 'password', 'enable')
    search_fields = ['name', 'enable']
    list_per_page = 20


class SeedsAdmin(admin.ModelAdmin):
    list_display = (
        'uid', 'is_crawled', 'other_crawled', 'home_crawled')
    search_fields = ['uid']
    list_per_page = 20
    # 排序
    ordering = ['is_crawled']

# 注册admin
admin.site.register(Keywords, KeywordsAdmin)
admin.site.register(Seeds, SeedsAdmin)
admin.site.register(LoginInFo, LoginInFoAdmin)
