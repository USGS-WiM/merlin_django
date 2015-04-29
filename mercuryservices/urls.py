from django.conf.urls import patterns, url, include
from mercuryservices import views
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter


#router = DefaultRouter()
router = BulkRouter()

router.register(r'acids', views.AcidViewSet, 'acids')
router.register(r'blankwaters', views.BlankWaterViewSet, 'blankwaters')
router.register(r'bottles', views.BottleViewSet, 'bottles')
router.register(r'bottleprefixes', views.BottlePrefixViewSet, 'bottleprefixes')
router.register(r'bottletypes', views.BottleTypeViewSet, 'bottletypes')
router.register(r'brominations', views.BrominationViewSet, 'brominations')
router.register(r'constituents', views.ConstituentTypeViewSet, 'constituents')
router.register(r'cooperators', views.CooperatorViewSet, 'cooperators')
router.register(r'detectionflags', views.DetectionFlagViewSet)
router.register(r'filters', views.FilterTypeViewSet)
router.register(r'isotopeflags', views.IsotopeFlagViewSet)
router.register(r'mediums', views.MediumTypeViewSet)
router.register(r'methods', views.MethodTypeViewSet, 'methods')
router.register(r'procedures', views.ProcedureTypeViewSet)
router.register(r'preservations', views.PreservationTypeViewSet)
router.register(r'projects', views.ProjectViewSet, 'projects')
router.register(r'projectssites', views.ProjectSiteViewSet, 'projectssites')
router.register(r'processings', views.ProcessingTypeViewSet)
router.register(r'qualityassurances', views.QualityAssuranceViewSet)
router.register(r'qualityassurancetypes', views.QualityAssuranceTypeViewSet, 'qualityassurancetypes')
router.register(r'results', views.ResultViewSet, 'results')
router.register(r'samples', views.SampleViewSet, 'samples')
router.register(r'samplebottles', views.SampleBottleViewSet, 'samplebottles')
router.register(r'samplebottlebrominations', views.SampleBottleBrominationViewSet, 'samplebottlebrominations')
router.register(r'sites', views.SiteViewSet, 'sites')
router.register(r'statuses', views.StatusTypeViewSet)
router.register(r'units', views.UnitTypeViewSet)
router.register(r'users', views.UserViewSet, 'users')

router.register(r'fullresults', views.FullResultViewSet, 'fullresults')
router.register(r'fullsamplebottles', views.FullSampleBottleViewSet, 'fullsamplebottles')

router.register(r'bulkacids', views.AcidBulkUpdateViewSet)
router.register(r'bulkblankwaters', views.BlankWaterBulkUpdateViewSet)
router.register(r'bulkbottles', views.BottleBulkCreateUpdateViewSet)
router.register(r'bulkbottleprefixes', views.BottlePrefixBulkCreateUpdateViewSet)
router.register(r'bulkbrominations', views.BrominationBulkUpdateViewSet)
router.register(r'bulkcooperators', views.CooperatorBulkUpdateViewSet)
router.register(r'bulkprojects', views.ProjectBulkUpdateViewSet)
router.register(r'bulkprojectssites', views.ProjectBulkUpdateViewSet)
router.register(r'bulkresults', views.ResultBulkCreateUpdateViewSet)
router.register(r'bulksamples', views.SampleBulkCreateUpdateViewSet)
router.register(r'bulksamplebottles', views.SampleBottleBulkCreateUpdateViewSet)
router.register(r'bulksamplebottlebrominations',
                views.SampleBottleBrominationBulkCreateUpdateViewSet, 'bulksamplebottlebrominations')
router.register(r'bulksites', views.SiteBulkUpdateViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       url(r'^batchupload', views.BatchUpload.as_view(), name='batchupload'),
                       url(r'^reportresultscooperator/',
                           views.ReportResultsCooperator.as_view(), name='reportresultscooperator'),
                       url(r'^reportresultsnwis/', views.ReportResultsNwis.as_view(), name='reportresultsnwis'),
                       url(r'^reportsamplesnwis/', views.ReportSamplesNwis.as_view(), name='reportsamplesnwis'),
                       url(r'^resultcountprojects/',
                           views.ReportResultsCountProjects.as_view(), name='resultcountprojects'),
                       url(r'^resultcountnawqa/', views.ReportResultsCountNawqa.as_view(), name='resultcountnawqa'),
                       )
