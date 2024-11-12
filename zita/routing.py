from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from jobs.consumers import ChatConsumer


application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/chat/<str:chatname>/<int:jd_id>", ChatConsumer),
                ]
            )
        ),
    }
)
