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
    url(r'^cooperators_grid/save$', views.cooperators_grid_save, name='cooperators_grid_save'),
    url(r'^cooperators_grid/load$', views.cooperators_grid_load, name='cooperators_grid_load'),
    url(r'^cooperators_grid/(?P<pk>\d+)/$', views.cooperator_grid, name='cooperator_grid'),
    url(r'^cooperators_grid/(?P<pk>\d+)/save$', views.cooperator_grid_save, name='cooperator_grid_save'),
    url(r'^cooperators/(?P<pk>\d+)/$', views.cooperator_detail, name='cooperator_detail'),
    url(r'^cooperator_add/$', views.cooperator_add, name='cooperator_add'),
    url(r'^cooperators/(?P<pk>\d+)/cooperator_edit/$', views.CooperatorEdit.as_view(), name='cooperator_edit'),
    url(r'^cooperators/(?P<pk>\d+)/cooperator_delete/$', views.cooperator_delete, name='cooperator_delete'),
    url(r'^acids/$', views.acids, name='acids'),
    url(r'^acids/save$', views.acids_save, name='acids_save'),
    url(r'^blankwaters/$', views.blankwaters, name='blankwaters'),
    url(r'^blankwaters/save$', views.blankwaters_save, name='blankwaters_save'),
    url(r'^brominations/$', views. brominations, name='brominations'),
    url(r'^brominations/save$', views.brominations_save, name='brominations_save'),
    url(r'^bottles/$', views.bottles, name='bottles'),
    url(r'^bottles/save$', views.bottles_save, name='bottles_save')

)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )