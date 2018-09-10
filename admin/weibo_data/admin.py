from django.contrib import admin

from .models import WbUser, WeiboData


class ReadOnlyModelAdmin(admin.ModelAdmin):
    actions = None

    def get_readonly_fields(self, request, obj=None):
        # 注意self.model 会获取这个admin绑定的模型
        # model._meta 可以获取模型的meta信息

        # 这个钩子方法是返回readonly字段
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        # 这个部分是查看定时任务爬去的数据的，肯定不允许手工添加数据了
        return False

    def has_change_permission(self, request, obj=None):
        if request.method not in ('GET', 'HEAD'):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # 不允许删除
        return False


class WbUserAdmin(ReadOnlyModelAdmin):
    list_display = ('uid', 'name', 'gender', 'location', 'description', 'register_time', 'verify_type',
                    'follows_num', 'fans_num', 'wb_num')
    search_fields = ['name', 'uid']
    list_per_page = 20


class WeiboDataAdmin(ReadOnlyModelAdmin):
    list_display = ('weibo_id', 'uid', 'create_time', 'weibo_cont', 'repost_num', 'comment_num', 'praise_num')
    search_fields = ['weibo_cont', 'weibo_id']
    list_per_page = 20


admin.site.register(WbUser, WbUserAdmin)
admin.site.register(WeiboData, WeiboDataAdmin)