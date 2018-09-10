from django.shortcuts import redirect


def index(request):
    if not request.user.is_authenticated():
        # 如果用户没登录，那么跳转到admin的登录页面
        return redirect('/admin/login/?next=%s' % request.path)
    else:
        # 如果登录了，那么跳转到admin页面
        return redirect('/admin/')