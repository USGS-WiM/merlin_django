from django.conf import settings
from django.conf.urls import url
from django.views.static import serve
from merlin import views

app_name = 'merlin'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    url(r'^sample_login/$', views.sample_login, name='sample_login'),
    url(r'^samples_create/$', views.samples_create, name='samples_create'),
    url(r'^samples_search/$', views.samples_search, name='samples_search'),
    url(r'^samples_update/$', views.samples_update, name='samples_update'),
    url(r'^results_search/$', views.results_search, name='results_search'),

    url(r'^results_count_projects/$', views.results_count_projects, name='results_count_projects'),
    url(r'^results_count_nawqa/$', views.results_count_nawqa, name='results_count_nawqa'),
    url(r'^samples_nwis_report/$', views.samples_nwis_report, name='samples_nwis_report'),
    url(r'^results_nwis_report/$', views.results_nwis_report, name='results_nwis_report'),
    url(r'^results_cooperator_report/$', views.results_cooperator_report, name='results_cooperator_report'),

    url(r'^cooperators/$', views.cooperators, name='cooperators'),
    url(r'^cooperators_update/$', views.cooperators_update, name='cooperators_update'),
    url(r'^cooperators_create/$', views.cooperators_create, name='cooperators_create'),
    url(r'^cooperators_delete/$', views.cooperators_delete, name='cooperators_delete'),

    url(r'^projects/$', views.projects, name='projects'),
    url(r'^projects_update/$', views.projects_update, name='projects_update'),
    url(r'^projects_create/$', views.projects_create, name='projects_create'),
    url(r'^projects_delete/$', views.projects_delete, name='projects_delete'),

    url(r'^sites/$', views.sites, name='sites'),
    url(r'^sites_update/$', views.sites_update, name='sites_update'),
    url(r'^sites_create/$', views.sites_create, name='sites_create'),
    url(r'^sites_delete/$', views.sites_delete, name='sites_delete'),

    url(r'^projectssites/$', views.projectssites, name='projectssites'),
    url(r'^projectssites_create/$', views.projectssites_create, name='projectssites_create'),
    url(r'^projectssites_delete/$', views.projectssites_delete, name='projectssites_delete'),

    url(r'^acids/$', views.acids, name='acids'),
    url(r'^acids_update/$', views.acids_update, name='acids_update'),
    url(r'^acids_create/$', views.acids_create, name='acids_create'),
    url(r'^acids_delete/$', views.acids_delete, name='acids_delete'),

    url(r'^blankwaters/$', views.blankwaters, name='blankwaters'),
    url(r'^blankwaters_update/$', views.blankwaters_update, name='blankwaters_update'),
    url(r'^blankwaters_create/$', views.blankwaters_create, name='blankwaters_create'),
    url(r'^blankwaters_delete/$', views.blankwaters_delete, name='blankwaters_delete'),

    url(r'^brominations/$', views.brominations, name='brominations'),
    url(r'^brominations_update/$', views.brominations_update, name='brominations_update'),
    url(r'^brominations_create/$', views.brominations_create, name='brominations_create'),
    url(r'^brominations_delete/$', views.brominations_delete, name='brominations_delete'),
    url(r'^samplebottlebrominations_create/$',
        views.samplebottlebrominations_create, name='samplebottlebrominations_create'),
    url(r'^samplebottlebrominations_search/$',
        views.samplebottlebrominations_search, name='samplebottlebrominations_search'),
    url(r'^samplebottlebrominations_delete/$',
        views.samplebottlebrominations_delete, name='samplebottlebrominations_delete'),

    url(r'^bottles/$', views.bottles, name='bottles'),
    url(r'^bottles_update/$', views.bottles_update, name='bottles_update'),
    url(r'^bottles_create/$', views.bottles_create, name='bottles_create'),
    url(r'^bottles_delete/$', views.bottles_delete, name='bottles_delete'),
    url(r'^bottle_prefixes_update/$', views.bottle_prefixes_update, name='bottle_prefixes_update'),
    url(r'^bottle_prefixes_create/$', views.bottle_prefixes_create, name='bottle_prefixes_create'),
    url(r'^bottle_prefixes_range_create/$', views.bottle_prefixes_range_create, name='bottle_prefixes_range_create'),
    url(r'^bottle_prefixes_delete/$', views.bottle_prefixes_delete, name='bottle_prefixes_delete'),

    url(r'^balanceverifications/$', views.balanceverifications, name='balanceverifications'),
    url(r'^balanceverifications_update/$', views.balanceverifications_update, name='balanceverifications_update'),
    url(r'^balanceverifications_create/$', views.balanceverifications_create, name='balanceverifications_create'),
    url(r'^balanceverifications_delete/$', views.balanceverifications_delete, name='balanceverifications_delete'),

]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]