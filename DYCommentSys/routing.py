# DYC/routing.py
from channels.auth import AuthMiddlewareStack
# 继承settings中的allow host
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from User import consumers

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(  # 中间件
            URLRouter([  # 路由列表
                path('ws/search/', consumers.SearchConsumer.as_asgi()),
            ])
        ),
    )
})
