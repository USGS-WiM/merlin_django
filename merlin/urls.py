from django.conf import settings
from django.conf.urls import patterns, url, include
from merlin import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^sample_login/$', views.sample_login, name='sample_login'),
    url(r'^samples_create/$', views.samples_create, name='samples_create'),
    url(r'^samples_search/$', views.samples_search, name='samples_search'),
    url(r'^samples_update/$', views.samples_update, name='samples_update'),
    url(r'^results_search/$', views.results_search, name='results_search'),

#    url(r'^cooperators_list/$', views.cooperators_list, name='cooperators_list'),
#    url(r'^cooperators_formset/$', views.cooperators_formset, name='cooperators_formset'),

    url(r'^cooperators/$', views.cooperators, name='cooperators'),
    url(r'^cooperators_update/$', views.cooperators_update, name='cooperators_update'),
    url(r'^cooperators_create/$', views.cooperators_create, name='cooperators_create'),
#    url(r'^cooperators/(?P<pk>\d+)/$', views.cooperator, name='cooperator'),
#    url(r'^cooperators/(?P<pk>\d+)/save$', views.cooperator_update, name='cooperator_update'),
#    url(r'^cooperators_list/(?P<pk>\d+)/$', views.cooperator_detail, name='cooperator_detail'),
#    url(r'^cooperators_list/(?P<pk>\d+)/edit/$', views.CooperatorEdit.as_view(), name='cooperator_edit'),
#    url(r'^cooperators_list/(?P<pk>\d+)/delete/$', views.cooperator_delete, name='cooperator_delete'),

    url(r'^projects/$', views.projects, name='projects'),
    url(r'^projects_update/$', views.projects_update, name='projects_update'),
    url(r'^projects_create/$', views.projects_create, name='projects_create'),

    url(r'^sites/$', views.sites, name='sites'),
    url(r'^sites_update/$', views.sites_update, name='sites_update'),
    url(r'^sites_create/$', views.sites_create, name='sites_create'),

    url(r'^acids/$', views.acids, name='acids'),
    url(r'^acids_update/$', views.acids_update, name='acids_update'),
    url(r'^acids_create/$', views.acids_create, name='acids_create'),

    url(r'^blankwaters/$', views.blankwaters, name='blankwaters'),
    url(r'^blankwaters_update/$', views.blankwaters_update, name='blankwaters_update'),
    url(r'^blankwaters_create/$', views.blankwaters_create, name='blankwaters_create'),

    url(r'^brominations/$', views.brominations, name='brominations'),
    url(r'^brominations_update/$', views.brominations_update, name='brominations_update'),
    url(r'^brominations_create/$', views.brominations_create, name='brominations_create'),
    url(r'^samplebottlebrominations_create/$', views.samplebottlebrominations_create, name='samplebottlebrominations_create'),
    url(r'^samplebottlebromination_search/$', views.samplebottlebromination_search, name='samplebottlebromination_search'),

    url(r'^bottles/$', views.bottles, name='bottles'),
    url(r'^bottles_update/$', views.bottles_update, name='bottles_update'),
    url(r'^bottles_create/$', views.bottles_create, name='bottles_create'),
    url(r'^bottle_prefixes_update/$', views.bottle_prefixes_update, name='bottle_prefixes_update'),
    url(r'^bottle_prefixes_create/$', views.bottle_prefixes_create, name='bottle_prefixes_create'),
    url(r'^bottle_prefixes_range_create/$', views.bottle_prefixes_range_create, name='bottle_prefixes_range_create'),


)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )