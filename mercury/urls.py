from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^mercuryadmin/', include(admin.site.urls)),
    url(r'^mercuryservices/', include('mercuryservices.urls')),# namespace="mercuryservices")),
    url(r'^mercuryauth/', include('djoser.urls', namespace="mercuryauth")),
    url(r'^merlin/', include('merlin.urls', namespace="merlin")),
]
