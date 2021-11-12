from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from random import randint
import redis,json

def admin_login_required(view_func):
    '''登录判断装饰器'''

    def wrapper(request, *view_args, **view_kwargs):
        if request.session.has_key('delegateId'):
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

def android_login_required(view_func):
    '''登录判断装饰器'''
    def wrapper(request, *view_args, **view_kwargs):
        if request.body:
            data = json.loads(request.body)
            token = data.get('token')
            if token:
                red = redis.Redis(host='localhost', port=6379, decode_responses=True)
                customerId = red.get(token)
                red.close()
                if customerId:
                    return view_func(request, *view_args, **view_kwargs)

        return AjaxReturn(0,'登录过期')

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
    str = '0123456789ABCDEFGHJKLMNPQRTUVWXY'
    end = 9 if onlyNum else 31
    return str[randint(0, end)] + str[randint(0, end)] + str[randint(0, end)] + str[randint(0, end)]
