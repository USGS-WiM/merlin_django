from django.conf import settings
from django.conf.urls import patterns, url, include
from mercurylab import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^restricted/$', views.restricted, name='restricted'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^cooperators/$', views.cooperators_list, name='cooperators_list'),
    url(r'^cooperators/(?P<pk>\d+)/$', views.cooperators_detail, name='cooperators_detail'),
    url(r'^cooperator_add/$', views.cooperator_add, name='cooperator_add'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )