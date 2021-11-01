from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from random import randint


def admin_login_required(view_func):
    '''登录判断装饰器'''

    def wrapper(request, *view_args, **view_kwargs):
        if request.session.has_key('adminId'):
            # 用户已登录
            return view_func(request, *view_args, **view_kwargs)
        else:
            # 跳转到登录页面
            return redirect(reverse('dyadmin-login'))

    return wrapper

def user_login_required(view_func):
    '''登录判断装饰器'''

    def wrapper(request, *view_args, **view_kwargs):
        if request.session.has_key('customer'):
            # 用户已登录
            return view_func(request, *view_args, **view_kwargs)
        else:
            # 跳转到登录页面
            return redirect(reverse('user-login'))

    return wrapper


def AjaxReturn(code, msg, data=(), count=False):
    dic = {
        'code': code,
        'msg': msg,
        'data': data,
    }
    if count != False:
        dic['count'] = count
    return JsonResponse(dic, safe=False)


def randomCode(onlyNum=True):
    str = '0123456789ABCDEFGHJKLMNPQRSTUVWXY'
    end = 9 if onlyNum else 32
    return str[randint(0, end)] + str[randint(0, end)] + str[randint(0, end)] + str[randint(0, end)]
