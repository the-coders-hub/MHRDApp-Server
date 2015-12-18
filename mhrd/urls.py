"""mhrd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import re

import rest_framework_swagger.urls
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from account.views import AccountViewset, UserViewset
from college.views import CollegeViewset
from core.views import TagViewset
from .views import media_file_view

router = DefaultRouter()
router.register('account', AccountViewset, base_name='account')
router.register('college', CollegeViewset, base_name='college')
router.register('user', UserViewset, base_name='user')
router.register('tag', TagViewset, base_name='tag')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api-docs/', include(rest_framework_swagger.urls, namespace='api-docs')),
]

# Fail safe! If nginx is down, this might come handy.
urlpatterns += [
    url(r'^%s(?P<path>.*)$' % re.escape(settings.STATIC_URL.lstrip('/')), serve,
        kwargs={
            'document_root': settings.STATIC_ROOT,
        }
        ),
    url(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')), media_file_view),
]
