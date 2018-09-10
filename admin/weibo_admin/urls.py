from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static

from . import view

# 很简单的url：admin页面 + 静态页面

# 静态页面的配置：只能在debug方式用
# Helper function to return a URL pattern for serving files in debug mode.

urlpatterns = [
    url(r'^$', view.index),
    url(r'^admin/', admin.site.urls)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
