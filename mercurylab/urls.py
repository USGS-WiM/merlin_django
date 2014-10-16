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
    url(r'^cooperators/$', views.cooperators_list, name='cooperators'),
    url(r'^cooperators_formset/$', views.cooperators_formset, name='cooperators_formset'),
    url(r'^cooperators_grid/$', views.cooperators_grid, name='cooperators_grid'),
    url(r'^cooperators_grid/(?P<pk>\d+)/$', views.cooperator_grid, name='cooperator_grid'),
    url(r'^cooperators_grid/(?P<pk>\d+)/save$', views.cooperator_grid_save, name='cooperator_grid_save'),
    url(r'^cooperators/(?P<pk>\d+)/$', views.cooperator_detail, name='cooperator_detail'),
    url(r'^cooperator_add/$', views.cooperator_add, name='cooperator_add'),
    url(r'^cooperators/(?P<pk>\d+)/cooperator_edit/$', views.CooperatorEdit.as_view(), name='cooperator_edit'),
    url(r'^cooperators/(?P<pk>\d+)/cooperator_delete/$', views.cooperator_delete, name='cooperator_delete'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )