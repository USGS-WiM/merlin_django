from django.conf.urls import include, url
from django.contrib import admin
#from rest_framework.authtoken import views


urlpatterns = [
    url(r'^mercuryadmin/', include(admin.site.urls)),
    url(r'^mercuryservices/', include('mercuryservices.urls')),# namespace="mercuryservices")),
    url(r'^mercuryauth/', include('djoser.urls', namespace="mercuryauth")),
    url(r'^merlin/', include('merlin.urls', namespace="merlin")),
    url(r'^docs/', include('rest_framework_docs.urls')),
    #url(r'^api-token-auth/', views.obtain_auth_token),
]
