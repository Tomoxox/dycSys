from django.shortcuts import render, redirect
from django.http import HttpResponse
from captcha.image import ImageCaptcha
from utils.general import AjaxReturn,randomCode
from .models import Delegate
import datetime

def login(request):
    if request.method == 'POST':
        captcha = request.POST.get('code')
        if captcha.upper() != request.session.get('captcha'):
            return AjaxReturn(0,'验证码错误')
        username = request.POST.get('phone')
        password = request.POST.get('password')
        # 超级管理员 delegateId：0  代理 delegateId：代理ID
        if username == 'chuangding8899' and password == 'cdingchina888':
            request.session['delegateId'] = 0
            return AjaxReturn(1, '登录成功')

        dele = Delegate.objects.filter(phone=username,password=password).all()[:1]
        if len(dele) > 0:
            dele = dele[0]
            if dele.status == 1:
                now = datetime.datetime.now()
                if now >= dele.available_till:
                    return AjaxReturn(0, '账号已过期')

                request.session['delegateId'] = dele.id
                return AjaxReturn(1,'登录成功')
            else:
                return AjaxReturn(0, '账号已失效')
        else:
            request.session.flush()
            return AjaxReturn(0, '账号或密码错误')

    if request.session.get('delegateId'):
        return redirect('dyadmin-index')
    return render(request,'admin/login.html')

def cap(request):
    captcha = randomCode(False)
    request.session['captcha'] = captcha
    data = ImageCaptcha().generate(captcha)
    return HttpResponse(data)

