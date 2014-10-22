from django.conf.urls import patterns, url, include
from mercuryservices import views
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter


#router = DefaultRouter()
router = BulkRouter()
router.register(r'bulkcooperators', views.CooperatorBulkUpdateViewSet)
router.register(r'cooperators', views.CooperatorViewSet, 'cooperators')
router.register(r'bulkprojects', views.ProjectBulkUpdateViewSet)
router.register(r'projects', views.ProjectViewSet, 'projects')
router.register(r'bulksites', views.SiteBulkUpdateViewSet)
router.register(r'sites', views.SiteViewSet, 'sites')
router.register(r'samples', views.FieldSampleViewSet)
router.register(r'samplebottles', views.FieldSampleBottleViewSet)
router.register(r'bottles', views.BottleViewSet, 'bottles')
router.register(r'bulkbottles', views.BottlesBulkUpdateViewSet)
router.register(r'filters', views.FilterTypeViewSet)
router.register(r'preservations', views.PreservationTypeViewSet)
router.register(r'mediums', views.MediumTypeViewSet)
router.register(r'units', views.UnitTypeViewSet)
router.register(r'methods', views.MethodTypeViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'constituents', views.ConstituentTypeViewSet)
router.register(r'qualityassurances', views.QualityAssuranceViewSet)
router.register(r'detectionlimits', views.DetectionLimitViewSet)
router.register(r'acids', views.AcidViewSet, 'acids')
router.register(r'bulkacids', views.AcidsBulkUpdateViewSet)
router.register(r'blankwaters', views.BlankWaterViewSet, 'blankwaters')
router.register(r'bulkblankwaters', views.BlankWatersBulkUpdateViewSet)
router.register(r'brominations', views.BrominationViewSet, 'brominations')
router.register(r'bulkbrominations', views.BrominationsBulkUpdateViewSet)
#router.register(r'roles', views.RoleViewSet)
#router.register(r'users', views.UserViewSet)
router.register(r'statuses', views.StatusTypeViewSet)
router.register(r'procedures', views.ProcedureTypeViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       )
