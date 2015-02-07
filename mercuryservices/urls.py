from django.conf.urls import patterns, url, include
from mercuryservices import views
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter


#router = DefaultRouter()
router = BulkRouter()
router.register(r'cooperators', views.CooperatorViewSet, 'cooperators')
router.register(r'bulkcooperators', views.CooperatorBulkUpdateViewSet)
router.register(r'projects', views.ProjectViewSet, 'projects')
router.register(r'bulkcooperators', views.CooperatorBulkUpdateViewSet)
router.register(r'sites', views.SiteViewSet, 'sites')
router.register(r'bulksites', views.SiteBulkUpdateViewSet)
router.register(r'samples', views.SampleViewSet, 'samples')
router.register(r'bulksamples', views.SampleBulkCreateUpdateViewSet)
router.register(r'samplebottles', views.SampleBottleViewSet, 'samplebottles')
router.register(r'bulksamplebottles', views.SampleBottleBulkCreateUpdateViewSet)
router.register(r'fullsamplebottles', views.FullSampleBottleViewSet, 'fullsamplebottles')
router.register(r'bulksamplebottlebrominations', views.SampleBottleBrominationBulkCreateUpdateViewSet, 'bulksamplebottlebrominations')
router.register(r'samplebottlebrominations', views.SampleBottleBrominationViewSet, 'samplebottlebrominations')
router.register(r'bottles', views.BottleViewSet, 'bottles')
router.register(r'bulkbottles', views.BottleBulkCreateUpdateViewSet)
router.register(r'bottletypes', views.BottleTypeViewSet, 'bottletypes')
router.register(r'filters', views.FilterTypeViewSet)
router.register(r'preservations', views.PreservationTypeViewSet)
router.register(r'processings', views.ProcessingTypeViewSet)
router.register(r'mediums', views.MediumTypeViewSet)
router.register(r'units', views.UnitTypeViewSet)
router.register(r'methods', views.MethodTypeViewSet)
router.register(r'bulkresults', views.ResultBulkCreateUpdateViewSet)
router.register(r'results', views.ResultViewSet, 'results')
router.register(r'fullresults', views.FullResultViewSet, 'fullresults')
router.register(r'constituents', views.ConstituentTypeViewSet, 'constituents')
router.register(r'qualityassurances', views.QualityAssuranceViewSet)
router.register(r'detectionflags', views.DetectionFlagViewSet)
router.register(r'isotopeflags', views.IsotopeFlagViewSet)
router.register(r'acids', views.AcidViewSet, 'acids')
router.register(r'bulkacids', views.AcidBulkUpdateViewSet)
router.register(r'blankwaters', views.BlankWaterViewSet, 'blankwaters')
router.register(r'bulkblankwaters', views.BlankWaterBulkUpdateViewSet)
router.register(r'brominations', views.BrominationViewSet, 'brominations')
router.register(r'bulkbrominations', views.BrominationBulkUpdateViewSet)
#router.register(r'roles', views.RoleViewSet)
router.register(r'users', views.UserViewSet, 'users')
router.register(r'statuses', views.StatusTypeViewSet)
router.register(r'procedures', views.ProcedureTypeViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       #url(r'^login/', views.UserLoginView.as_view(), name='login'),
                       #url(r'^logout/', views.UserLogoutView.as_view(), name='logout'),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       #url(r'^auth/', include('djoser.urls')),
                       #url(r'^testreport/', views.TestReport.as_view(), name='testreport'),
                       )
