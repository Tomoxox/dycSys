from django.shortcuts import render, HttpResponse,redirect
from django.http import JsonResponse
from utils.general import AjaxReturn, randomCode
from utils.aliSMS import AliSMS
from django.views.decorators.http import require_POST
from DYAdmin.models import *
from django.forms.models import model_to_dict
from .API import dy_sign
import json,redis
import datetime
from .schedule import addTask

@require_POST
def login(request):
    data = json.loads(request.body)
    phone = data.get('phone')
    password = data.get('password')
    customer = Customer.objects.filter(phone=phone, password=password).all()[:1]
    if customer:
        customer = customer[0]
        if customer.status == 0:
            return AjaxReturn(0, '账号未激活')
        if customer.status == 2:
            return AjaxReturn(0, '账号已封禁')
        now = datetime.datetime.now()
        if now >= customer.available_till:
            return AjaxReturn(0,'账号已过期')
        # 返回 token 并保存
        red = redis.Redis(host='localhost', port=6379, decode_responses=True)
        token = randomCode()+randomCode()
        red.set(token,customer.id)
        red.close()

        return AjaxReturn(1, '登录成功',{'token':token})
    else:
        return AjaxReturn(0, '账号或密码错误')

@require_POST
def home(request):
    customerId = getCustomerId(request)
    totalComment = Comment.objects.filter(Customer_id=customerId).count()
    handledComment = Comment.objects.filter(Customer_id=customerId,status=1).count()
    peerNum = Peer.objects.filter(Customer_id=customerId).count()
    taskNum = Task.objects.filter(Customer_id=customerId).count()
    aiClue = Comment.objects.filter(Customer_id=customerId,is_ai=True).all()[:5]
    arr = []
    for ai in aiClue:
        dic = model_to_dict(ai)
        dic['created_at'] = datetime.datetime.strftime(ai.created_at,'%Y-%m-%d %H:%M:%S')
        arr.append(dic)
    return AjaxReturn(1,'获取数据成功',{
        'totalComment':totalComment,
        'handledComment':handledComment,
        'peerNum':peerNum,
        'taskNum':taskNum,
        'aiClue':arr,
    })

@require_POST
def peers(request):
    customerId = getCustomerId(request)
    data = Peer.objects.filter(Customer_id=customerId).values('nickname','avatar_thumb','uid').all()
    data = list(data.values())
    if hasattr(Peer, 'formatData'):
        data = getattr(Peer, 'formatData')(data)
    return AjaxReturn(1, '获取成功', data)

@require_POST
def tasks(request):
    customerId = getCustomerId(request)
    tasks = Task.objects.filter(Customer_id=customerId).all()
    taskArr = []
    for task in tasks:
        taskArr.append({
            'title': task.title,
            'taskId': task.id,
            'status': task.status,
            'created_at': datetime.datetime.strftime(task.created_at,'%Y-%m-%d %H:%M:%S'),
            'video': task.video_set.count(),
            'comment': task.comment_set.filter(is_ai=False).count(),
        })
    return AjaxReturn(1,'获取成功',taskArr)


def marketingClue(request):
    if request.method == 'POST':
        dic = {
            'Customer_id': request.session.get('customer')['id'],
            # 'Video__isnull': False,
            'is_ai': False
        }
        task = request.POST.get('task')
        contact = request.POST.get('contact')
        hit_word = request.POST.get('hit_word')
        if task:
            dic['Task_id'] = task
        if contact == '1':
            dic['vx__isnull'] = False
            dic['phone__isnull'] = False
        elif contact == '2':
            dic['phone__isnull'] = False
        elif contact == '3':
            dic['vx__isnull'] = False
        if hit_word:
            dic['hit_word__contains'] = hit_word
        page = int(request.POST.get('page', 1))
        nums = int(request.POST.get('limit', 20))
        count = Comment.objects.filter(**dic).count()
        data = Comment.objects.filter(**dic).all()[(page - 1) * nums: page * nums]
        data = list(data.values())
        if hasattr(Comment, 'formatData'):
            data = getattr(Comment, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    taskList = Task.objects.filter(Customer_id=request.session.get('customer')['id']).all()
    return render(request, 'user/monitor/marketingClue.html', locals())

@require_POST
def clue(request):
    customerId = getCustomerId(request)
    data = json.loads(request.body)
    page = data.get('page',1)
    isAi = data.get('isAi',False)
    data = Comment.objects.filter(status=0,Customer_id=customerId,is_ai=isAi).all()[(page - 1)*20: page*20]
    data = list(data.values('nickname','text','created_at','uid'))
    for d in data:
        d['created_at'] = datetime.datetime.strftime(d['created_at'],'%Y-%m-%d %H:%M:%S')
        d['selected'] = False
    return AjaxReturn(1, '获取成功', data)

@require_POST
def clients(request):
    customerId = getCustomerId(request)
    data = json.loads(request.body)
    page = data.get('page',1)
    data = Consumer.objects.filter(Customer_id=customerId).all()[(page - 1)*20: page*20]
    data = list(data.values('nickname','avatar_thumb','created_at','uid'))
    for d in data:
        d['created_at'] = datetime.datetime.strftime(d['created_at'],'%Y-%m-%d %H:%M:%S')
        d['selected'] = False
    return AjaxReturn(1, '获取成功', data)

@require_POST
def updateClue(request):
    customerId = getCustomerId(request)
    data = json.loads(request.body)
    ids = data.get('ids', [])
    Comment.objects.filter(Customer_id=customerId,uid__in=ids).update(status=1)
    return AjaxReturn(1,'success')


def clientProfile(request):
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        nums = int(request.POST.get('limit', 20))
        count = Consumer.objects.filter(Customer_id=request.session.get('customer')['id']).count()
        data = Consumer.objects.filter(Customer_id=request.session.get('customer')['id']).all()[(page - 1)*nums: page*nums]
        data = list(data.values())
        if hasattr(Consumer, 'formatData'):
            data = getattr(Consumer, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    return render(request, 'user/sphere/clientProfile.html', locals())


@require_POST
def switchTask(request):
    data = json.loads(request.body)
    taskId = data.get('taskId')
    customerId = getCustomerId(request)
    task = Task.objects.filter(Customer_id=customerId, id=taskId).get()
    if task:
        task.status = (not task.status)
        task.save()
    return AjaxReturn(1, '切换成功')


def getCustomerId(request):
    data = json.loads(request.body)
    token = data.get('token')
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    customerId = red.get(token)
    red.close()
    return customerId