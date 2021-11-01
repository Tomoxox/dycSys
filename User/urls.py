from django.urls import path
from . import views,schedule
from utils.general import user_login_required
urlpatterns = [
    path('login', views.login,name='user-login'),
    path('register', views.register,name='user-register'),
    path('code', views.code,name='user-code'),
    path('logout', views.logout,name='user-logout'),
    path('GETOUTTHERENSCRAWLMF', schedule.commentTasks,name='user-commentTasks'),
    path('test', schedule.updateHotTopics),

    path('index', user_login_required(views.index),name='user-index'),
    path('home', user_login_required(views.home),name='user-home'),
    path('leftMenus', user_login_required(views.leftMenus),name='user-leftMenus'),
    path('search', user_login_required(views.search),name='user-search'),


    path('commentPage/<str:videoId>', user_login_required(views.commentPage),name='user-commentPage'),
    path('commentPageByID/<int:videoId>', user_login_required(views.commentPageByID),name='user-commentPageByID'),
    path('userPage/<str:userId>', user_login_required(views.userPage),name='user-userPage'),
    path('searchVideo/<str:words>', user_login_required(views.searchVideo),name='user-userPage'),


    path('myHotWord', user_login_required(views.myHotWord),name='user-myHotWord'),
    path('addWord', user_login_required(views.addWord),name='user-addWord'),
    path('chooseTask', user_login_required(views.chooseTask),name='user-chooseTask'),
    path('addVideo', user_login_required(views.addVideo),name='user-addVideo'),
    path('addPeer', user_login_required(views.addPeer),name='user-addPeer'),
    path('updateTask/<int:taskId>', user_login_required(views.updateTask),name='user-updateTask'),
    path('operateTask', user_login_required(views.operateTask),name='user-operateTask'),


    path('douyinHot', user_login_required(views.douyinHot),name='user-douyinHot'),
    path('peerMonitor', user_login_required(views.peerMonitor),name='user-peerMonitor'),
    path('videoMonitor', user_login_required(views.videoMonitor),name='user-videoMonitor'),
    path('taskCenter', user_login_required(views.taskCenter),name='user-taskCenter'),
    path('marketingClue', user_login_required(views.marketingClue),name='user-marketingClue'),


    path('aiClue', user_login_required(views.aiClue),name='user-aiClue'),
    path('addConsumers', user_login_required(views.addConsumers),name='user-addConsumers'),
    path('clientProfile', user_login_required(views.clientProfile),name='user-clientProfile'),
    path('followUpRec', user_login_required(views.followUpRec),name='user-followUpRec'),


    path('basicInfo', user_login_required(views.basicInfo),name='user-basicInfo'),
    path('balance', user_login_required(views.balance),name='user-balance'),
    path('updatePass', user_login_required(views.updatePass),name='user-updatePass'),
    path('loginLogging', user_login_required(views.loginLogging),name='user-loginLogging'),
]
