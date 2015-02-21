from django.conf import settings
from django.conf.urls import patterns, url, include
from mercurylab import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
#    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
#    url(r'^profile/$', views.profile, name='profile'),
    url(r'^logout/$', views.user_logout, name='logout'),

#    url(r'^sample_login_a/$', views.sample_login_a, name='sample_login_a'),
    url(r'^sample_login/$', views.sample_login, name='sample_login'),
    url(r'^sample_login/save$', views.sample_login_save, name='sample_login_save'),
    url(r'^sample_search/$', views.sample_search, name='sample_search'),
    url(r'^sample_search/search$', views.sample_search, name='sample_search_search'),
    url(r'^sample_search/save$', views.sample_search_save, name='sample_search_save'),
    url(r'^result_search/$', views.result_search, name='result_search'),
    url(r'^result_search/search$', views.result_search, name='result_search_search'),

#    url(r'^cooperators_list/$', views.cooperators_list, name='cooperators_list'),
#    url(r'^cooperators_formset/$', views.cooperators_formset, name='cooperators_formset'),

    url(r'^cooperators/$', views.cooperators, name='cooperators'),
    url(r'^cooperators/save$', views.cooperators_save, name='cooperators_save'),
    url(r'^cooperators/load$', views.cooperators_load, name='cooperators_load'),
    url(r'^cooperator_add/$', views.cooperator_add, name='cooperator_add'),
#    url(r'^cooperators/(?P<pk>\d+)/$', views.cooperator, name='cooperator'),
#    url(r'^cooperators/(?P<pk>\d+)/save$', views.cooperator_save, name='cooperator_save'),
#    url(r'^cooperators_list/(?P<pk>\d+)/$', views.cooperator_detail, name='cooperator_detail'),
#    url(r'^cooperators_list/(?P<pk>\d+)/edit/$', views.CooperatorEdit.as_view(), name='cooperator_edit'),
#    url(r'^cooperators_list/(?P<pk>\d+)/delete/$', views.cooperator_delete, name='cooperator_delete'),

    url(r'^projects/$', views.projects, name='projects'),
    url(r'^projects/save$', views.projects_save, name='projects_save'),
    url(r'^projects/load$', views.projects_load, name='projects_load'),
    url(r'^project_add/$', views.project_add, name='project_add'),

    url(r'^sites/$', views.sites, name='sites'),
    url(r'^sites/save$', views.sites_save, name='sites_save'),
    url(r'^sites/load$', views.sites_load, name='sites_load'),
    url(r'^site_add/$', views.site_add, name='site_add'),

    url(r'^acids/$', views.acids, name='acids'),
    url(r'^acids/save$', views.acids_save, name='acids_save'),
    url(r'^acids/load$', views.acids_load, name='acids_load'),
    url(r'^acid_add/$', views.acid_add, name='acid_add'),

    url(r'^blankwaters/$', views.blankwaters, name='blankwaters'),
    url(r'^blankwaters/save$', views.blankwaters_save, name='blankwaters_save'),
    url(r'^blankwaters/load$', views.blankwaters_load, name='blankwaters_load'),
    url(r'^blankwater_add/$', views.blankwater_add, name='blankwater_add'),

    url(r'^brominations/$', views.brominations, name='brominations'),
    url(r'^brominations/save$', views.brominations_save, name='brominations_save'),
    url(r'^brominations/load$', views.brominations_load, name='brominations_load'),
    url(r'^bromination_add/$', views.bromination_add, name='bromination_add'),
    url(r'^samplebottlebromination_add/$', views.samplebottlebromination_add, name='samplebottlebromination_add'),
    url(r'^samplebottlebromination_search/$', views.samplebottlebromination_search, name='samplebottlebromination_search'),

    url(r'^bottles/$', views.bottles, name='bottles'),
    url(r'^bottles/save$', views.bottles_save, name='bottles_save'),
    url(r'^bottleprefixes/save$', views.bottle_prefixes_save, name='bottle_prefixes_save'),
    url(r'^bottles/load$', views.bottles_load, name='bottles_load'),
    url(r'^bottleprefix_add/$', views.bottle_prefix_add, name='bottle_prefix_add'),
    url(r'^bottleprefix_range_add/$', views.bottle_prefix_range_add, name='bottle_prefix_range_add'),
    url(r'^bottles_add/$', views.bottles_add, name='bottles_add'),


)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )