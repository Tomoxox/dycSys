from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from .models import *
from utils.general import AjaxReturn
import importlib
from django.forms.models import model_to_dict
from datetime import datetime
from django.db.models import Sum


def index(request):
    if request.session.get('delegateId') == 0:
        role = '超级管理员'
    else:
        role = Delegate.objects.filter(id=request.session.get('delegateId')).values('phone')[0]['phone']
    return render(request, 'admin/index.html',locals())

def home(request):
    # 管理： 已售询盘(消耗的+客户的+代理的)、已消耗询盘、代理数量、客户数量
    # 代理： 已售询盘(消耗的+客户的)、剩余询盘、已消耗询盘(消耗的)、客户数量
    delegateId = request.session.get('delegateId')
    if delegateId == 0:
        total_comment = Comment.objects.all().count()
        customer_left = Customer.objects.aggregate(total=Sum('comment_num_left'))
        delegate_left = Delegate.objects.aggregate(total=Sum('comment_num_left'))
        customers = Customer.objects.all().count()
        delegates = Delegate.objects.all().count()
        dict = [
            {
               'title':'已售询盘',
               'num':total_comment+customer_left['total']+delegate_left['total'],
            },
            {
               'title':'已消耗询盘',
               'num':total_comment
            },
            {
               'title':'代理数量',
               'num':delegates
            },
            {
               'title':'客户数量',
               'num':customers
            },
        ]
    else:
        dele = Delegate.objects.filter(id=delegateId).get()
        arr = dele.customer_set.all().values('id')
        customerArr = []
        for a in arr:
            customerArr.append(a['id'])
        total_comment = Comment.objects.filter(Customer_id__in=customerArr).all().count()

        customer_left = Customer.objects.filter(id__in=customerArr).aggregate(total=Sum('comment_num_left'))
        if not customer_left['total']:
            customer_left = 0
        else:
            customer_left = customer_left['total']
        customers = dele.customer_set.all().count()

        dict = [
            {
                'title': '已售询盘',
                'num': total_comment + customer_left,
            },
            {
                'title': '剩余询盘',
                'num': dele.comment_num_left
            },
            {
                'title': '已消耗询盘',
                'num': total_comment
            },
            {
                'title': '客户数量',
                'num': customers
            },
        ]
    commentList = Comment.objects.all()[:9]

    return render(request, 'admin/home.html', locals())

def leftMenus(request):
    arr = [
        {
            'title': "数据看板",
            'icon': "&#xe68e;",
            'href': '/',
            'fontFamily': "layui-icon",
            'isCheck': "true",
            'spread': "true"
        },
        {
            'title': "代理管理",
            'icon': "&#xe66f;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "代理列表",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': reverse('dyadmin-table', args=('Delegate',)),
                },
            ]
        },
        {
            'title': "客户管理",
            'icon': "&#xe770;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "客户列表",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': reverse('dyadmin-table', args=('Customer',)),
                },
            ]
        },
        {
            'title': "任务管理",
            'icon': "&#xe62a;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "任务列表",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': reverse('dyadmin-table', args=('Task',)),
                },
            ]
        },
        {
            'title': "顾客资料",
            'icon': "&#xe63c;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "顾客列表",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': reverse('dyadmin-table', args=('Consumer',)),
                },
            ]
        },
        {
            'title': "参数设置",
            'icon': "&#xe631;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "用户参数",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': reverse('dyadmin-config'),
                },
            ]
        }
    ]
    if request.session.get('delegateId') != 0:
        arr.pop(1)
        arr.pop(-1)

    return JsonResponse(arr, safe=False)


def logout(request):
    request.session.flush()
    return redirect('dyadmin-login')


def table(request, model):
    model_str = model
    model = checkModel(model)
    if request.method == 'POST':
        dic = getFilterDict(request,model_str)
        input_type = request.POST.get('input_type')
        input_text = request.POST.get('input_text')
        if input_type and len(input_type) > 0 and input_text and len(input_text) > 0 :
            dic[input_type] = input_text
        curr = int(request.POST.get('curr'))
        nums = int(request.POST.get('nums'))
        count = model.objects.filter(**dic).count()
        data = model.objects.filter(**dic).all()[curr-1: nums]
        data = list(data.values())
        if hasattr(model, 'formatData'):
            data = getattr(model, 'formatData')(data)
        return AjaxReturn(1,'success',data,count)

    links = {
        'table':reverse('dyadmin-table',args=(model_str,)),
        'add':reverse('dyadmin-add',args=(model_str,)),
        'update':reverse('dyadmin-update',args=(model_str,)),
        'delete':reverse('dyadmin-delete',args=(model_str,)),
    }
    return render(request, 'admin/table.html', context={
        'seek': model.seek(),
        'head': model.head(),
        'hand': model.hand(),
        'menu': model.menus(),
        'links': links,
        'lists': list_setup(),
    })


def add(request, model):
    model = checkModel(model)
    if request.method == 'POST':
        param = request.POST.dict()
        if hasattr(model, 'checkNewParam'):
            param = getattr(model, 'checkNewParam')(param)
            if not param:
                return AjaxReturn(0,'参数错误')
        new = model(**param)
        new.save()
        return AjaxReturn(1,'新增成功')

    return render(request,'admin/add.html',context={
        'field':model.field()
    })


def update(request, model):
    model = checkModel(model)
    id = request.GET.get('id')
    modelOne = model.objects.filter(id=id).get()
    if request.method == 'POST':
        param = request.POST.dict()
        if hasattr(model, 'checkParam'):
            param = getattr(model, 'checkParam')(param)
            if not param:
                return AjaxReturn(0,'数据错误')
        print(param)
        model.objects.filter(id=id).update(**param)
        return AjaxReturn(1, '修改成功')

    modelOne = model_to_dict(modelOne)
    modelOne['is_deleted'] = 1 if modelOne['is_deleted'] else 0
    if modelOne.get('available_till'):
        modelOne['available_till'] = datetime.strftime(modelOne['available_till'],"%Y-%m-%d %H:%M:%S", )
    return render(request, 'admin/add.html', context={
        'info':modelOne,
        'field': model.field()
    })


def delete(request, model):
    model = checkModel(model)
    id = request.POST.get('ids')
    model.objects.filter(id__in=id.split(',')).update(is_deleted=True)
    return AjaxReturn(1, '删除成功')

def other(request, model):
    if request.method == 'POST':
        model = checkModel(model)
        id = request.GET.get('id')
        if hasattr(model, 'other'):
            res = getattr(model, 'other')(id,request)
            return res
        else:
            return AjaxReturn(0,'err')

    return render(request,'admin/other/'+model+'.html')

def config(request):
    conf = Config.objects.filter(id=1).get()
    if request.method == 'POST':
        conf.video_num = request.POST.get('video',30)
        conf.task_num = request.POST.get('task',3)
        conf.peer_num = request.POST.get('peer',3)
        conf.save()
        return AjaxReturn(1,'修改成功')
    return render(request,'admin/other/config.html',locals())

def checkModel(modelStr):
    model = globals().get(modelStr)
    if not model:
        model = importlib.import_module("DYAdmin.models").__dict__.get(modelStr)
    return model

def getFilterDict(request, model_str):
    deleId = request.session.get('delegateId')
    print(deleId)
    if deleId == 0:
        return {}
    else:
        customerIds = Customer.objects.filter(Delegate_id=deleId).all().values('id')
        arr = []
        for cus in customerIds:
            arr.append(cus['id'])
        key = 'id__in'
        if model_str != 'Customer':
            key = 'Customer_id__in'
        return {
            key: arr
        }