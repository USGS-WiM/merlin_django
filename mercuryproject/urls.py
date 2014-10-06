from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mercuryproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^mercuryadmin/', include(admin.site.urls)),
    url(r'^mercuryservices/', include('mercuryservices.urls')),# namespace="mercuryservices")),
    url(r'^mercurylab/', include('mercurylab.urls', namespace="mercurylab")),
)
