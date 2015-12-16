from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewset


router = DefaultRouter()
router.register('account', AccountViewset, base_name='account')


urlpatterns = [
    url(r'^api/', include(router.urls))
]