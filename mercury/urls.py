from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^mercuryadmin/', include(admin.site.urls)),
    url(r'^mercuryservices/', include('mercuryservices.urls')),# namespace="mercuryservices")),
    url(r'^mercuryauth/', include('djoser.urls', namespace="mercuryauth")),
    url(r'^mercurydocs/', include('rest_framework_swagger.urls')),
    url(r'^merlin/', include('merlin.urls', namespace="merlin")),
    url(r'^mercurybatchupload/', include('mercurybatchupload.urls', namespace="mercurybatchupload")),
)
