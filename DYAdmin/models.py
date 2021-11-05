from django.db import models
from db.base_model import BaseModel
from django.shortcuts import reverse
from django.db import DatabaseError,transaction
from utils.general import AjaxReturn

ACCOUNT_STATUS = {
    0: "未启用",
    1: "生效中",
    2: "已封禁",
}
COMMENT_STATUS = {
    0: "未处理",
    1: "已处理",
}
TASK_STATUS = {
    0: "停止",
    1: "运行",
}


class BaseManager(models.Manager):
    def get_queryset(self):
        try:
            data = super().get_queryset().filter(is_deleted=False)
        except self.model.DoesNotExist:
            data = None
        return data

    class Meta:
        abstract = True


class AdminAccount(BaseModel):
    username = models.CharField(max_length=11)
    password = models.CharField(max_length=32)
    objects = BaseManager()

    @staticmethod
    def seek():
        return {
            'text': [
                {'field': 'id', 'title': '编号'},
            ],
        }

    @staticmethod
    def checkNewParam(param):
        count = AdminAccount.objects.filter(username=param['username']).count()
        if count:
            return
        return param

    @staticmethod
    def head():
        return [
            {
                'width': 50,
                'minWidth': 50,
                'type': 'checkbox',
                'fixed': 'left',
                'align': 'center'
            },
            {
                'field': 'id',
                'title': '编号',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'username',
                'title': '编号',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'password',
                'title': '编号',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'created_at',
                'title': '编号',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'updated_at',
                'title': '编号',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'title': '操作',
                'width': 100,
                'minWidth': 100,
                'fixed': 'right',
                'align': 'center',
                'templet': '#listTpl'
            },
        ]

    @staticmethod
    def hand():
        return tableMenus('AdminAccount', ('other', 'updateData', 'deleteData'))

    @staticmethod
    def menus():
        return tableMenus('AdminAccount', ('addData', 'batchMove'))

    @staticmethod
    def field(param={}):
        return [
            {
                'field': 'username',
                'title': '手机账号',
                'types': 'input',
                'class': 'text',
                'warns': '请填写登录手机号',
                'musts': 'required'
            },
            {
                'field': 'password',
                'title': '密码',
                'types': 'input',
                'class': 'password',
                'warns': '',
                'musts': 'nothing' if len(param) else 'required'
            },
        ]


class Delegate(BaseModel):
    phone = models.CharField(max_length=11)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=16, null=True)
    status = models.SmallIntegerField(default=0)
    available_till = models.DateTimeField(null=True)
    comment_num_left = models.IntegerField(default=0, null=True)
    remark = models.CharField(max_length=50, default='', null=True)
    objects = BaseManager()

    @staticmethod
    def seek():
        return {
            'text': [
                {'field': 'id', 'title': '编号'},
            ],
        }

    @staticmethod
    def head():
        return [
            {
                'width': 50,
                'minWidth': 50,
                'type': 'checkbox',
                'fixed': 'left',
                'align': 'center'
            },
            {
                'field': 'id',
                'title': '编号',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'phone',
                'title': '手机号码',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'name',
                'title': '姓名',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'status',
                'title': '状态',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'comment_num_left',
                'title': '剩余评论数',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'available_till',
                'title': '有效期',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'remark',
                'title': '备注',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'created_at',
                'title': '创建日期',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'updated_at',
                'title': '更新日期',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'title': '操作',
                'width': 100,
                'minWidth': 100,
                'fixed': 'right',
                'align': 'center',
                'templet': '#listTpl'
            },
        ]

    @staticmethod
    def hand():
        return tableMenus('Delegate', ('other', 'updateData', 'deleteData'))

    @staticmethod
    def menus():
        return tableMenus('Delegate', ('addData', 'batchMove'))

    @staticmethod
    def field(param={}):
        return [
            {
                'field': 'phone',
                'title': '手机账号',
                'types': 'input',
                'class': 'text',
                'warns': '请填写登录手机号',
                'musts': 'required'
            },
            {
                'field': 'password',
                'title': '密码',
                'types': 'input',
                'class': 'password',
                'warns': '编辑可不填写密码',
                'musts': 'nothing' if len(param) else 'required'
            },
            {
                'field': 'name',
                'title': '名字',
                'types': 'input',
                'class': 'text',
                'warns': '请填写名字',
                'musts': 'required'
            },
            {
                'field': 'status',
                'title': '账号状态',
                'types': 'select',
                'warns': '请选择账号状态',
                'quick': ACCOUNT_STATUS
            },
            {
                'field': 'available_till',
                'title': '有效期',
                'types': 'datetime',
                'class': 'text',
                'warns': '请填写有效期',
                'musts': 'required'
            },
            {
                'field': 'remark',
                'title': '备注',
                'types': 'input',
                'class': 'text',
                'warns': '请填写备注',
                'musts': 'nothing'
            },
        ]

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = ACCOUNT_STATUS[d['status']]
        return data

    @staticmethod
    def checkNewParam(param):
        count = Delegate.objects.filter(phone=param['phone']).count()
        if count:
            return
        return param

    @staticmethod
    def other(id,request):
        try:
            with transaction.atomic():
                num = abs(int(request.POST.dict().get('number')))
                dele = Delegate.objects.filter(id=id).get()
                dele.comment_num_left += num
                dele.save()
                return AjaxReturn(1, '增加成功')
        except DatabaseError:
            return AjaxReturn(0,'操作失败，请重试')


class Customer(BaseModel):
    phone = models.CharField(max_length=11)
    password = models.CharField(max_length=32)
    name = models.CharField(max_length=16, null=True)
    Delegate = models.ForeignKey('Delegate', on_delete=models.SET_NULL, null=True)
    set_meal = models.CharField(max_length=16, null=True, default='基础版')
    status = models.SmallIntegerField(default=0)
    available_till = models.DateTimeField(null=True)
    task_num_left = models.SmallIntegerField(default=3, null=True)
    comment_num_left = models.IntegerField(default=0, null=True)
    peer_num_left = models.IntegerField(default=3, null=True)
    email = models.EmailField(max_length=20, null=True)
    remark = models.CharField(max_length=50, null=True)
    objects = BaseManager()

    @staticmethod
    def seek():
        return {
            'text': [
                {'field': 'name', 'title': '姓名'},
                {'field': 'phone', 'title': '手机号'},
            ],
        }

    @staticmethod
    def head():
        return [
            {
                'width': 50,
                'minWidth': 50,
                'type': 'checkbox',
                'fixed': 'left',
                'align': 'center'
            },
            {
                'field': 'delegate',
                'title': '代理',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'phone',
                'title': '手机号',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'name',
                'title': '姓名',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'status',
                'title': '状态',
                'width': 80,
                'minWidth': 80,
                'align': 'center'
            },
            {
                'field': 'available_till',
                'title': '有效期',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'comment_num_left',
                'title': '剩余评论数',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'remark',
                'title': '备注',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'created_at',
                'title': '创建日期',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'updated_at',
                'title': '更新日期',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'title': '操作',
                'width': 100,
                'minWidth': 100,
                'fixed': 'right',
                'align': 'center',
                'templet': '#listTpl'
            },
        ]

    @staticmethod
    def hand():
        return tableMenus('Customer', ('other', 'updateData', 'deleteData'))

    @staticmethod
    def menus():
        return tableMenus('Customer', ('batchMove'))

    @staticmethod
    def field(param={}):
        return [
            {
                'field': 'phone',
                'title': '手机账号',
                'types': 'input',
                'class': 'text',
                'warns': '请填写登录手机号',
                'musts': 'required'
            },
            {
                'field': 'password',
                'title': '密码',
                'types': 'input',
                'class': 'password',
                'warns': '编辑可不填写密码',
                'musts': 'nothing' if len(param) else 'required'
            },
            {
                'field': 'name',
                'title': '名字',
                'types': 'input',
                'class': 'text',
                'warns': '请填写名字',
                'musts': 'nothing'
            },
            {
                'field': 'status',
                'title': '账号状态',
                'types': 'select',
                'warns': '请选择账号状态',
                'quick': ACCOUNT_STATUS
            },
            {
                'field': 'available_till',
                'title': '有效期',
                'types': 'datetime',
                'class': 'text',
                'warns': '请填写有效期',
                'musts': 'required'
            },
        ]

    @staticmethod
    def formatData(data=[]):
        delePhone = None
        for d in data:
            if not delePhone:
                self = Customer.objects.filter(id=d['id']).get()
                delePhone = self.Delegate.phone
            d['status'] = ACCOUNT_STATUS[d['status']]
            d['delegate'] = delePhone
        return data

    @staticmethod
    def checkNewParam(param):
        count = Delegate.objects.filter(phone=param['phone']).count()
        if count:
            return
        return param

    @staticmethod
    def other(id, request):
        try:
            with transaction.atomic():
                num = abs(int(request.POST.dict().get('number')))
                cus = Customer.objects.filter(id=id).get()
                if request.session.get('delegateId') != 0:
                    dele = cus.Delegate
                    # 检查代理剩余
                    if dele.comment_num_left < num:
                        return AjaxReturn(0, '代理剩余线索数量不足')
                    # 扣除
                    dele.comment_num_left -= num
                    dele.save()
                # 增加
                cus.comment_num_left += num
                cus.save()
                return AjaxReturn(1, '增加成功')
        except DatabaseError:
            return AjaxReturn(0, '操作失败，请重试')


class CustomerLoginLogging(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    location = models.CharField(max_length=50, null=True)
    browser = models.CharField(max_length=255)
    objects = BaseManager()

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['method'] = '账号密码登录'
        return data

class Config(BaseModel):
    video_num = models.IntegerField(default=30)
    task_num = models.IntegerField(default=3)
    peer_num = models.IntegerField(default=5)
    objects = BaseManager()


# --------------------------------------------------------------------------------
class MyHotWord(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    words = models.CharField(max_length=50, null=True)
    index = models.CharField(max_length=80)
    objects = BaseManager()

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = '关注中'
        return data

class Task(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    title = models.CharField(max_length=16, null=True)
    within_days = models.IntegerField(null=True)
    filter_words = models.CharField(max_length=255,null=True)
    peer_monitor_ids = models.CharField(max_length=255,null=True)
    status = models.SmallIntegerField(null=True,default=1)
    remark = models.CharField(max_length=255,null=True)
    objects = BaseManager()

    @staticmethod
    def seek():
        return {
            'text': [
                {'field': 'title', 'title': '任务名称'},
            ],
        }

    @staticmethod
    def head():
        return [
            {
                'width': 50,
                'minWidth': 50,
                'type': 'checkbox',
                'fixed': 'left',
                'align': 'center'
            },
            {
                'field': 'title',
                'title': '任务名',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
            {
                'field': 'filter_words',
                'title': '目标词',
                'width': 300,
                'minWidth': 300,
                'align': 'center'
            },
            {
                'field': 'status',
                'title': '任务状态',
                'width': 100,
                'minWidth': 100,
                'align': 'center'
            },
            {
                'field': 'remark',
                'title': '备注',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'created_at',
                'title': '创建日期',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
            {
                'field': 'updated_at',
                'title': '更新日期',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
        ]

    @staticmethod
    def hand():
        return tableMenus('Customer', ())

    @staticmethod
    def menus():
        return tableMenus('Customer', ())

    @staticmethod
    def field(param={}):
        return [
            {
                'field': 'phone',
                'title': '手机账号',
                'types': 'input',
                'class': 'text',
                'warns': '请填写登录手机号',
                'musts': 'required'
            },
            {
                'field': 'password',
                'title': '密码',
                'types': 'input',
                'class': 'password',
                'warns': '编辑可不填写密码',
                'musts': 'nothing' if len(param) else 'required'
            },
            {
                'field': 'name',
                'title': '名字',
                'types': 'input',
                'class': 'text',
                'warns': '请填写名字',
                'musts': 'nothing'
            },
            {
                'field': 'status',
                'title': '运行状态',
                'types': 'select',
                'warns': '请选择账号状态',
                'quick': TASK_STATUS
            },
            {
                'field': 'available_till',
                'title': '有效期',
                'types': 'datetime',
                'class': 'text',
                'warns': '请填写有效期',
                'musts': 'required'
            },
        ]

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = TASK_STATUS[d['status']]
        return data


class Peer(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    uid = models.CharField(max_length=20, null=True)
    sec_uid = models.CharField(max_length=120, null=True)
    unique_id = models.CharField(max_length=20, null=True)
    nickname = models.CharField(max_length=20, null=True)
    signature = models.CharField(max_length=255, null=True)
    avatar_thumb = models.URLField(max_length=200, null=True)
    follower_count = models.IntegerField(null=True)
    total_favorited = models.IntegerField(null=True)
    custom_verify = models.CharField(max_length=50, null=True)
    objects = BaseManager()

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = '关注中'
        return data

class Video(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    Tasks = models.ManyToManyField('Task')
    aweme_id = models.CharField(max_length=30, null=True)
    desc = models.CharField(max_length=150, null=True)
    create_time = models.DateTimeField(null=True)
    cover = models.CharField(max_length=455, null=True)
    like_num = models.IntegerField(null=True)
    comment_num = models.IntegerField(null=True)
    download_num = models.IntegerField(null=True)
    share_num = models.IntegerField(null=True)
    objects = BaseManager()

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = '关注中'
        return data

class PeerVideo(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    Task = models.ForeignKey('Task', on_delete=models.CASCADE)
    Peer = models.ForeignKey('Peer', on_delete=models.CASCADE, null=True)
    aweme_id = models.CharField(max_length=30, null=True)
    desc = models.CharField(max_length=150, null=True)
    comment_num = models.IntegerField(null=True,default=0)
    objects = BaseManager()


class Comment(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    Task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True)
    Video = models.ForeignKey('Video', on_delete=models.SET_NULL, null=True)
    PeerVideo = models.ForeignKey('PeerVideo', on_delete=models.SET_NULL, null=True)
    cid = models.CharField(max_length=20, null=True)
    uid = models.CharField(max_length=20, null=True)
    sec_uid = models.CharField(max_length=120, null=True)
    unique_id = models.CharField(max_length=20, null=True)
    nickname = models.CharField(max_length=50, null=True)
    avatar_thumb = models.URLField(max_length=255, null=True)
    like_num = models.IntegerField(null=True)
    vx = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=50, null=True)
    text = models.CharField(max_length=255, null=True)
    hit_word = models.CharField(max_length=20, null=True)
    status = models.SmallIntegerField(null=True,default=0,verbose_name='0 未处理 1 已处理')
    is_ai = models.SmallIntegerField(null=True,default=0,verbose_name='0 普通评论 1 智能推荐')
    objects = BaseManager()

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = COMMENT_STATUS[d['status']]
            d['TaskTitle'] = Task.objects.filter(id=d['Task_id']).get().title
            if d.get('Video_id'):
                d['VideoTitle'] = Video.objects.filter(id=d['Video_id']).get().desc
                d['VideoId'] = Video.objects.filter(id=d['Video_id']).get().aweme_id
            else:
                d['VideoTitle'] = PeerVideo.objects.filter(id=d['PeerVideo_id']).get().desc
                d['VideoId'] = PeerVideo.objects.filter(id=d['PeerVideo_id']).get().aweme_id
        return data

class Consumer(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    uid = models.CharField(max_length=20, null=True)
    sec_uid = models.CharField(max_length=120, null=True)
    nickname = models.CharField(max_length=25, null=True)
    avatar_thumb = models.URLField(max_length=150, null=True)
    name = models.CharField(max_length=20, null=True)
    phone = models.CharField(max_length=20, null=True)
    type = models.CharField(max_length=20, null=True)
    company = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=40, null=True)
    remark = models.CharField(max_length=255, null=True)
    objects = BaseManager()

    @staticmethod
    def seek():
        return {
            'text': [
                {'field': 'title', 'title': '客户昵称'},
            ],
        }

    @staticmethod
    def head():
        return [
            {
                'width': 50,
                'minWidth': 50,
                'type': 'checkbox',
                'fixed': 'left',
                'align': 'center'
            },
            {
                'field': 'nickname',
                'title': '昵称',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
            {
                'field': 'name',
                'title': '姓名',
                'width': 300,
                'minWidth': 300,
                'align': 'center'
            },
            {
                'field': 'phone',
                'title': '电话',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
            {
                'field': 'remark',
                'title': '备注',
                'width': 150,
                'minWidth': 150,
                'align': 'center'
            },
            {
                'field': 'created_at',
                'title': '创建日期',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
            {
                'field': 'updated_at',
                'title': '更新日期',
                'width': 200,
                'minWidth': 200,
                'align': 'center'
            },
        ]

    @staticmethod
    def hand():
        return tableMenus('Customer', ())

    @staticmethod
    def menus():
        return tableMenus('Customer', ())

    @staticmethod
    def formatData(data=[]):

        return data

class FollowUp(BaseModel):
    Customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    Consumer = models.ForeignKey('Consumer', on_delete=models.CASCADE)
    follow_up_person = models.CharField(max_length=10, null=True)
    content = models.CharField(max_length=40, null=True)
    remark = models.CharField(max_length=30, null=True)
    objects = BaseManager()

    @staticmethod
    def formatData(data=[]):
        for d in data:
            d['status'] = '关注中'
        return data

# --------------------------------------------------------------------------------
def list_setup():
    return {
        'id': '#tableId',  # 唯一标识
        'elem': '#tableId',  # 定义容器
        'method': 'post',  # 传输类型
        'left': '#headTpl',  # 头部工具栏
        'right': "'filter'",  # 默认工具栏
        'page': 'true',  # 开启分页
        'limit': '15',  # 每页数据
        'limits': '10,15,20,25,30',  # 分页选项
        'curr': 'curr',  # 页码参数[默认：page]
        'nums': 'nums',  # 每页参数[默认：limit]
        'load': 'true',  # 表格进度
        'sort': 'false',  # 自动排序
        'skin': 'none',  # 表格风格[line:行边风格/row:列边风格/nob:无边风格]
        'even': 'false',  # 隔行背景
        'size': 'sm',  # 表格尺寸[sm：小尺寸/lg：大尺寸]
        'none': 'none'  # 异常提醒
    }


def tableMenus(model_str, need=()):
    menus = []
    lists = []
    route = reverse('dyadmin-add', args=(model_str,))
    if checkPower(route):
        menus.append({
            'name': '添加',
            'icon': '#xe642;',
            'sign': 'addData',
            'size': 'layui-btn-sm',
            'face': '',
            'link': route
        })
    route = reverse('dyadmin-update', args=(model_str,))
    if checkPower(route):
        menus.append({
            'name': '编辑',
            'icon': '#xe642;',
            'sign': 'updateData',
            'size': 'layui-btn-sm',
            'face': 'layui-btn-normal',
            'link': route
        })
    route = reverse('dyadmin-delete', args=(model_str,))
    if checkPower(route):
        menus.append({
            'name': '删除',
            'icon': '#xe640;',
            'sign': 'deleteData',
            'size': 'layui-btn-sm',
            'face': 'layui-btn-normal',
            'link': route
        })
    route = reverse('dyadmin-delete', args=(model_str,))
    if checkPower(route):
        menus.append({
            'name': '批量删除',
            'icon': '#xe640;',
            'sign': 'batchMove',
            'size': 'layui-btn-sm',
            'face': 'layui-btn-danger',
            'link': route
        })
    route = reverse('dyadmin-other', args=(model_str,))
    if checkPower(route):
        menus.append({
            'name': '其他设置',
            'icon': '#xe63c;',
            'sign': 'other',
            'size': 'layui-btn-sm',
            'face': 'layui-btn-danger',
            'link': route
        })
    if len(need) and len(menus):
        for v in menus:
            if v['sign'] in need:
                lists.append(v)
    return lists


def checkPower(route):
    return True
