from django.shortcuts import render, redirect
from django.http import HttpResponse
from captcha.image import ImageCaptcha
from utils.general import AjaxReturn,randomCode
from .models import AdminAccount

def login(request):
    if request.method == 'POST':
        captcha = request.POST.get('code')
        if captcha.upper() != request.session['captcha']:
            return AjaxReturn(0,'验证码错误')
        username = request.POST.get('user')
        password = request.POST.get('pass')
        # 超级管理员 adminId：0  代理 adminId：代理ID
        admin = AdminAccount.objects.filter(username=username,password=password)
        # print(admin)
        if len(admin) > 0:
            admin = admin[0]
        if admin:
            request.session['adminId'] = admin.id
            return AjaxReturn(1,'登录成功')
        else:
            del request.session['captcha']
            return AjaxReturn(0, '账号或密码错误')
    if request.session.get('adminId'):
        return redirect('dyadmin-index')
    return render(request,'admin/login.html')

def cap(request):
    captcha = randomCode(False)
    request.session['captcha'] = captcha
    data = ImageCaptcha().generate(captcha)
    return HttpResponse(data)

