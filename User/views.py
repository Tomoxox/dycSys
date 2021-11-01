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

def login(request):
    if request.method == 'POST':
        captcha = request.POST.get('captcha')
        if captcha.upper() != request.session['captcha']:
            return AjaxReturn(0, '验证码错误')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        customer = Customer.objects.filter(phone=phone, password=password)
        print(customer)
        if len(customer) > 0:
            customer = customer[0]
        if customer:
            request.session['customer'] = model_to_dict(customer)
            logging = CustomerLoginLogging(Customer=customer,ip=request.META.get('REMOTE_ADDR'),browser=request.META.get('HTTP_USER_AGENT'))
            logging.save()
            return AjaxReturn(1, '登录成功')
        else:
            del request.session['captcha']
            return AjaxReturn(0, '账号或密码错误')
    return render(request, 'user/login.html', locals())


def register(request):
    id = request.GET.get('id', 1)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        code = request.POST.get('code')
        if len(phone) != 11 or password != password2 or len(password) < 6 or len(password) > 16 or len(code) != 4:
            return AjaxReturn(0, '请规范填写信息')
        if code != request.session.get('code'):
            return AjaxReturn(0, '验证码错误')
        count = Customer.objects.filter(phone=phone).count()
        if count:
            return AjaxReturn(0, '用户已存在')
        cus = Customer(phone=phone, password=password, Delegate_id=id)
        cus.save()
        return AjaxReturn(1, '注册成功，请先激活')
    return render(request, 'user/register.html', locals())


@require_POST
def code(request):
    request.session['code'] = randomCode(True)
    phone = request.POST.get('phone')
    res = AliSMS.sendCode(phone, request.session['code'])
    print(request.session['code'])
    return AjaxReturn(1, res.body.to_map()['Message'])


def logout(request):
    request.session.flush()
    return redirect('/login')


def index(request):
    phone = request.session.get('customer')['phone']
    return render(request, 'user/index.html', locals())


def home(request):
    now = datetime.datetime.now()
    totalComment = Comment.objects.filter(Customer_id=request.session.get('customer')['id']).count()
    unhandledComment = Comment.objects.filter(Customer_id=request.session.get('customer')['id'],status=0).count()
    peerNum = Peer.objects.filter(Customer_id=request.session.get('customer')['id']).count()
    videoNum = Video.objects.filter(Customer_id=request.session.get('customer')['id']).count()
    clientNum = Consumer.objects.filter(Customer_id=request.session.get('customer')['id']).count()
    taskNum = Task.objects.filter(Customer_id=request.session.get('customer')['id']).count()
    commentList = Comment.objects.filter(Customer_id=request.session.get('customer')['id'],is_ai=False).all()[:9]
    return render(request, 'user/home.html', locals())


def leftMenus(request):
    return JsonResponse([
        {
            'title': "数据看板",
            'icon': "&#xe68e;",
            'href': "/home",
            'fontFamily': "layui-icon",
            'isCheck': "true",
            'spread': "true"
        },
        {
            'title': "客户挖掘",
            'icon': "&#xe615;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "热词搜索",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/search",
                },
                {
                    'title': "我的热词",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/myHotWord",
                },
                {
                    'title': "抖音热点",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/douyinHot",
                },
            ]
        },
        {
            'title': "行业监控",
            'icon': "&#xe66f;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "同行监控",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/peerMonitor",
                },
                {
                    'title': "视频监控",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/videoMonitor",
                },
                {
                    'title': "任务中心",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/taskCenter",
                },
                {
                    'title': "市场线索",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/marketingClue",
                },
            ]
        },
        {
            'title': "私域运营",
            'icon': "&#xe609;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "AI推线索",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/aiClue",
                },
                {
                    'title': "客户档案",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/clientProfile",
                },
                # {
                #     'title': "跟进记录",
                #     'icon': "&#xe623;",
                #     'fontFamily': "layui-icon",
                #     'href': "/followUpRec",
                # },
            ]
        },
        {
            'title': "个人中心",
            'icon': "&#xe735;",
            'href': "/",
            'fontFamily': "layui-icon",
            'children': [
                {
                    'title': "基本信息",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/basicInfo",
                },
                {
                    'title': "账户余额",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/balance",
                },
                {
                    'title': "修改密码",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/updatePass",
                },
                {
                    'title': "登录日志",
                    'icon': "&#xe623;",
                    'fontFamily': "layui-icon",
                    'href': "/loginLogging",
                },
            ]
        },
    ], safe=False)


'''
------------------------------------------客户挖掘----------------------------------------------------------
'''


def search(request):
    scene = request.POST.get('scene', '')
    keyword = request.POST.get('keyword', '')
    if scene == 'hot_words':
        return AjaxReturn(1, '获取成功', dy_sign('search_sug', keyword))
    if scene == 'hot_videos':
        return AjaxReturn(1, '获取成功', dy_sign('search_video', keyword))
    if scene == 'hot_experts':
        return AjaxReturn(1, '获取成功', dy_sign('search_expert', keyword))
    tasks = Task.objects.filter(Customer_id=request.session.get('customer')['id']).all()
    return render(request, 'user/customer/searchA.html', locals())


def myHotWord(request):
    if request.method == 'POST':
        dic = {
            'Customer_id':request.session.get('customer')['id']
        }
        input_type = request.POST.get('input_type')
        input_text = request.POST.get('input_text')
        if input_type and len(input_type) > 0 and input_text and len(input_text) > 0:
            dic[input_type] = input_text
        curr = int(request.POST.get('curr', 1))
        nums = int(request.POST.get('nums', 20))
        count = MyHotWord.objects.filter(**dic).count()
        data = MyHotWord.objects.filter(**dic).all()[curr - 1: nums]
        data = list(data.values())
        if hasattr(MyHotWord, 'formatData'):
            data = getattr(MyHotWord, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    return render(request, 'user/customer/myHotWord.html', locals())


@require_POST
def addWord(request):
    words = request.POST.get('words')
    index = request.POST.get('index')
    customer = request.session['customer']
    if MyHotWord.objects.filter(words=words, Customer_id=customer['id']).count() == 0:
        newWord = MyHotWord(words=words, index=index, Customer_id=customer['id'])
        newWord.save()
    return AjaxReturn(1, '添加成功')

@require_POST
def deleteMyHotWord(request):
    id = request.POST.get('idsStr')
    customer = request.session['customer']
    word = MyHotWord.objects.filter(id=id, Customer_id=customer['id']).get()
    if word:
        word.delete()
    return AjaxReturn(1, '删除成功')


@require_POST
def addVideo(request):
    # print(request.POST)
    dict = {
        'aweme_id': request.POST.get('aweme_id'),
        'desc': request.POST.get('desc'),
        'create_time': datetime.datetime.fromtimestamp(int(request.POST.get('create_time'))),
        'cover': request.POST.get('video[cover][url_list][]'),
        'like_num': request.POST.get('statistics[digg_count]'),
        'Customer_id':request.session.get('customer')['id'],
    }
    if Video.objects.filter(Customer_id=request.session.get('customer')['id'],aweme_id=dict['aweme_id']).count() == 0:
        newVideo = Video(**dict)
        newVideo.save()
    else:
        # 修改所在任务
        video = Video.objects.filter(Customer_id=request.session.get('customer')['id'], aweme_id=dict['aweme_id']).get()
        video.Tasks.clear()

    task_ids = request.POST.get('task_ids')
    task_ids = task_ids.split(',')
    taskArr = Task.objects.filter(pk__in=task_ids).all()
    print(taskArr)
    video = Video.objects.filter(Customer_id=request.session.get('customer')['id'], aweme_id=dict['aweme_id']).get()
    for task in taskArr:
        video.Tasks.add(task.id)

    return AjaxReturn(1, '添加成功')


@require_POST
def addPeer(request):
    customer = request.session['customer']
    if Peer.objects.filter(uid=request.POST.get('uid'), Customer_id=customer['id']).count() == 0:
        newPeer = Peer(uid=request.POST.get('uid'), unique_id=request.POST.get('unique_id'),
                       nickname=request.POST.get('nickname'), signature=request.POST.get('signature'),
                       avatar_thumb=request.POST.get('avatar_thumb[url_list][]'),
                       follower_count=request.POST.get('follower_count'),
                       total_favorited=request.POST.get('total_favorited'),
                       custom_verify=request.POST.get('custom_verify'), sec_uid=request.POST.get('sec_uid'),
                       Customer_id=customer['id'])
        newPeer.save()
    return AjaxReturn(1, '添加成功')


def douyinHot(request):
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    topicData = json.loads(red.get('HOT_TOPIC'))
    # print(topicData)
    # return AjaxReturn(1,'',topicList)
    return render(request, 'user/customer/douyinHot.html', locals())


'''
-----------------------------------------行业监控----------------------------------------------------------
'''


def peerMonitor(request):
    if request.method == 'POST':
        dic = {}
        input_type = request.POST.get('input_type')
        input_text = request.POST.get('input_text')
        if input_type and len(input_type) > 0 and input_text and len(input_text) > 0:
            dic[input_type] = input_text
        page = int(request.POST.get('page', 1))
        limit = int(request.POST.get('limit', 20))
        count = Peer.objects.filter(**dic).count()
        data = Peer.objects.filter(**dic).all()[(page - 1)*limit: page * limit]
        data = list(data.values())
        if hasattr(Peer, 'formatData'):
            data = getattr(Peer, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    return render(request, 'user/monitor/peerMonitor.html', locals())


@require_POST
def deleteMyHotWord(request):
    id = request.POST.get('idsStr')
    customer = request.session['customer']
    peer = Peer.objects.filter(id=id, Customer_id=customer['id']).get()
    if peer:
        peer.delete()
    return AjaxReturn(1, '删除成功')

def videoMonitor(request):
    if request.method == 'POST':
        curr = int(request.POST.get('curr', 1))
        nums = int(request.POST.get('nums', 20))
        count = Video.objects.filter(Customer_id=request.session.get('customer')['id']).count()
        data = Video.objects.filter(Customer_id=request.session.get('customer')['id']).all()[curr - 1: nums]
        data = list(data.values())
        if hasattr(Video, 'formatData'):
            data = getattr(Video, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    return render(request, 'user/monitor/videoMonitor.html', locals())


def taskCenter(request):
    tasks = Task.objects.filter(Customer_id=request.session.get('customer')['id']).all()
    taskArr = []
    for task in tasks:
        taskArr.append({
            'task': task,
            'video': task.video_set.count(),
            'comment': task.comment_set.count(),
        })
    return render(request, 'user/monitor/taskCenter.html', locals())


def marketingClue(request):
    if request.method == 'POST':
        dic = {
            'Customer_id': request.session.get('customer')['id'],
            'Video__isnull': False,
            'is_ai': False
        }
        task = request.POST.get('task')
        contact = request.POST.get('contact')
        if task:
            dic['Task_id'] = task
        if contact == '1':
            dic['vx__isnull'] = False
            dic['phone__isnull'] = False
        elif contact == '2':
            dic['phone__isnull'] = False
        elif contact == '3':
            dic['vx__isnull'] = False
        print(dic)
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


'''
----------------------------------------私域运营----------------------------------------------------------
'''


def aiClue(request):
    if request.method == 'POST':
        dic = {
            'Customer_id' : request.session.get('customer')['id'],
            'PeerVideo__isnull' : False,
            'is_ai' : True
        }
        task = request.POST.get('task')
        contact = request.POST.get('contact')
        if task:
            dic['Task_id'] = task
        if contact == '1':
            dic['vx__isnull'] = False
            dic['phone__isnull'] = False
        elif contact == '2':
            dic['phone__isnull'] = False
        elif contact == '3':
            dic['vx__isnull'] = False
        print(dic)
        page = int(request.POST.get('page', 1))
        nums = int(request.POST.get('limit', 20))
        count = Comment.objects.filter(**dic).count()
        data = Comment.objects.filter(**dic).all()[(page - 1)*nums: page*nums]
        data = list(data.values())
        if hasattr(Comment, 'formatData'):
            data = getattr(Comment, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    taskList = Task.objects.filter(Customer_id=request.session.get('customer')['id']).all()
    return render(request, 'user/sphere/aiClue.html', locals())

@require_POST
def updateStatusOfClue(request):
    clueId = request.POST.get('clue')
    comm = Comment.objects.filter(Customer_id=request.session.get('customer')['id'],id=clueId).get()
    if comm:
        comm.status = 1
        comm.save()
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
def deleteMyClient(request):
    id = request.POST.get('idsStr')
    customer = request.session['customer']
    con = Consumer.objects.filter(id=id, Customer_id=customer['id']).get()
    if con:
        con.delete()
    return AjaxReturn(1, '删除成功')

def updateClientProfile(request,clientId):
    customer = request.session['customer']
    client = Consumer.objects.filter(id=clientId,Customer_id=customer['id']).get()
    if client:
        if request.method == 'POST':
            Consumer.objects.filter(id=clientId, Customer_id=customer['id']).update(**{
                'name':request.POST.get('name'),
                'phone':request.POST.get('phone'),
                'type':request.POST.get('type'),
                'company':request.POST.get('company'),
                'address':request.POST.get('address'),
                'remark':request.POST.get('remark'),
            })
            return AjaxReturn(1,'提交成交')
        return render(request,'user/sphere/updateClientProfile.html',locals())

def followUpRec(request):
    if request.method == 'POST':
        return AjaxReturn(1, 'success', [], 0)
    return render(request, 'user/sphere/followUpRec.html', locals())

@require_POST
def addConsumers(request):
    customerId = request.session.get('customer')['id']
    arr = request.POST.get('idsStr','')[0:-1].split(',')
    commArr = Comment.objects.filter(pk__in=arr).all()
    if len(commArr) > 0:
        for comm in commArr:
            consumer = Consumer(Customer_id=customerId,uid=comm.uid,sec_uid=comm.sec_uid,nickname=comm.nickname,avatar_thumb=comm.avatar_thumb,phone=comm.phone)
            consumer.save()
    return AjaxReturn(1,'添加成功')

'''
------------------------------------------个人中心------------------------------------------------------------
'''


def basicInfo(request):
    customer = request.session.get('customer')
    return render(request, 'user/userCenter/basicInfo.html', locals())


def balance(request):
    customer = request.session.get('customer')
    return render(request, 'user/userCenter/balance.html', locals())


def updatePass(request):
    if request.method == 'POST':
        oldPass = request.POST.get('oldPass','')
        newPass = request.POST.get('newPass','')
        newPass2 = request.POST.get('newPass2','')
        if len(newPass) < 6:
            return AjaxReturn(0,'请输入6位及以上密码')
        if newPass != newPass2:
            return AjaxReturn(0,'新密码不一致')
        customer = request.session.get('customer')
        if oldPass != customer['password']:
            return AjaxReturn(0, '原密码错误')
        customer['password'] = newPass
        request.session['customer'] = customer
        customer = Customer.objects.filter(id=customer['id']).update(password=newPass)
        return AjaxReturn(1,'修改成功')
    return render(request, 'user/userCenter/updatePass.html', locals())


def loginLogging(request):
    if request.method == 'POST':
        dic = {
            'Customer_id': request.session.get('customer')['id']
        }
        curr = int(request.POST.get('curr', 1))
        nums = int(request.POST.get('nums', 20))
        count = CustomerLoginLogging.objects.filter(**dic).count()
        data = CustomerLoginLogging.objects.filter(**dic).all()[curr - 1: nums]
        data = list(data.values())
        if hasattr(CustomerLoginLogging, 'formatData'):
            data = getattr(CustomerLoginLogging, 'formatData')(data)
        return AjaxReturn(1, 'success', data, count)
    return render(request, 'user/userCenter/loginLogging.html', locals())


'''
-----------------------------------------次级页面------------------------------------------------------------
'''


def commentPage(request, videoId):
    if request.method == 'POST':
        if len(videoId) == 19:
            page = request.POST.get('page', 1)
            return AjaxReturn(1, '获取成功', dy_sign('comment', videoId, page))
    return render(request, 'user/common/commentPageA.html', locals())

def commentPageByID(request, videoId):
    if request.method == 'POST':
        video = Video.objects.filter(id=videoId,Customer_id=request.session.get('customer')['id']).get()
        if video:
            page = request.POST.get('page', 1)
            return AjaxReturn(1, '获取成功', dy_sign('comment', video.aweme_id, page))
    return render(request, 'user/common/commentPageA.html', locals())


def userPage(request, userId):
    if request.method == 'POST':
        if len(request.POST.get('id')) > 40:
            return AjaxReturn(1, '获取成功', dy_sign('aweme_post', request.POST.get('id')))

    peer = Peer.objects.get(id=userId)
    return render(request, 'user/common/userPageA.html', locals())


def searchVideo(request, words):
    if request.method == 'POST':
        return AjaxReturn(1, '获取成功', dy_sign('search_video', request.POST.get('keyword')))
    words = MyHotWord.objects.filter(id=words, Customer_id=request.session.get('customer')['id']).get()
    if words:
        words = words.words
    else:
        return HttpResponse('')
    return render(request, 'user/common/searchVideoA.html', locals())

def searchVideoByWords(request, words):
    if request.method == 'POST':
        return AjaxReturn(1, '获取成功', dy_sign('search_video', request.POST.get('keyword')))
    return render(request, 'user/common/searchVideoA.html', locals())


def chooseTask(request):
    if request.method == 'POST':
        pass
        return AjaxReturn(1, '添加成功')

    return render(request, 'user/common/searchVideoA.html', locals())


def updateTask(request, taskId):
    if request.method == 'POST':
        peer_monitor_ids = []
        for key in request.POST.keys():
            if 'expert' in key:
                peer_monitor_ids.append(int(key.split('-')[-1]))
        if taskId == 0:
            task = Task(Customer_id=request.session.get('customer')['id'], title=request.POST.get('title', ''),
                        within_days=request.POST.get('day', 0),
                        filter_words=request.POST.get('words', ''), remark=request.POST.get('desc', ''),
                        peer_monitor_ids=json.dumps(peer_monitor_ids))
        else:
            task = Task.objects.filter(Customer_id=request.session.get('customer')['id'], id=taskId).get()
            task.Customer_id = request.session.get('customer')['id']
            task.title = request.POST.get('title', '')
            task.within_days = request.POST.get('day', 0)
            task.filter_words = request.POST.get('words', '')
            task.remark = request.POST.get('desc', '')
            task.peer_monitor_ids = json.dumps(peer_monitor_ids)
        task.save()

        return AjaxReturn(1, '提交成功')

    peerArr = Peer.objects.filter(Customer_id=request.session.get('customer')['id']).all()
    task = None
    if taskId != 0:
        task = Task.objects.filter(Customer_id=request.session.get('customer')['id'], id=taskId).get()
    return render(request, 'user/common/updateTask.html', locals())


@require_POST
def operateTask(request):
    op = request.POST.get('op', '')
    id = request.POST.get('id', 0)
    task = Task.objects.filter(Customer_id=request.session.get('customer')['id'], id=id).get()
    if task:
        if op == 'delete':
            task.delete()
        if op == 'status':
            task.status = (not task.status)
            task.save()
        if op == 'execute':
            task.status = 1
            task.save()
            addTask(task)
            return AjaxReturn(1,'执行中')
    return AjaxReturn(1, '删除成功')


'''
------------------------------------操作动作--------------------------------------------
'''
