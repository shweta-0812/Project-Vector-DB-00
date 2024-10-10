"""
ASGI config for berry_information_engine project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from main.routing import websocket_urlpatterns  # Import your routing file

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

# default
# application = get_asgi_application()


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Define websocket URL patterns or websocket routes in your app
        )
    ),
})
