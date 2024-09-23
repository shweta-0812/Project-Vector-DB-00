"""
URL configuration for berry_information_engine main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import JsonResponse
from django.urls import path
from django.conf import settings
from graphene_django.views import GraphQLView


def health_check():
    return JsonResponse({"status": "ok"})


urlpatterns = []

# Enable DEBUG to serve static files from Django Server
if settings.DEBUG:
    from django.conf.urls.static import static

    # Return a URL pattern for serving static files from Django server.
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('health_check', health_check, name='health_check'),
    path('graphql', GraphQLView.as_view(graphiql=True)),
]
