from django.conf.urls import url, include
from rest_framework import routers

from app.views import SearchUser, SearchUser2

router_v1 = routers.DefaultRouter()
router_v1.register(r'user', SearchUser, base_name='user')
router_v1.register(r'user2', SearchUser2, base_name='user2')

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include(router_v1.urls), name='api-index'),
]
