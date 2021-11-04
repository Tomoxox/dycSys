from django.urls import path
from . import loginViews
from . import indexViews
from utils.general import admin_login_required

urlpatterns = [
    path('login', loginViews.login, name='dyadmin-login'),
    path('cap', loginViews.cap, name='dyadmin-cap'),

    path('logout', admin_login_required(indexViews.logout), name='dyadmin-logout'),
    path('index', admin_login_required(indexViews.index), name='dyadmin-index'),
    path('home', admin_login_required(indexViews.home), name='dyadmin-home'),
    path('leftMenus', admin_login_required(indexViews.leftMenus), name='dyadmin-leftMenus'),
    path('config', admin_login_required(indexViews.config), name='dyadmin-config'),

    path('table/<str:model>', admin_login_required(indexViews.table), name='dyadmin-table'),
    path('add/<str:model>', admin_login_required(indexViews.add), name='dyadmin-add'),
    path('update/<str:model>', admin_login_required(indexViews.update), name='dyadmin-update'),
    path('delete/<str:model>', admin_login_required(indexViews.delete), name='dyadmin-delete'),
    path('other/<str:model>', admin_login_required(indexViews.other), name='dyadmin-other'),

]
