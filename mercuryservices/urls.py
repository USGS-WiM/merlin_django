from django.conf.urls import patterns, url, include
from mercuryservices import views
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter


#router = DefaultRouter()
router = BulkRouter()
router.register(r'bulkcooperators', views.CooperatorBulkUpdateViewSet)
router.register(r'cooperators', views.CooperatorViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'sites', views.SiteViewSet)
router.register(r'samples', views.FieldSampleViewSet)
router.register(r'samplebottles', views.FieldSampleBottleViewSet)
router.register(r'bottles', views.BottleViewSet)
router.register(r'filters', views.FilterTypeViewSet)
router.register(r'preservations', views.PreservationTypeViewSet)
router.register(r'mediums', views.MediumTypeViewSet)
router.register(r'units', views.UnitTypeViewSet)
router.register(r'methods', views.MethodTypeViewSet)
router.register(r'results', views.ResultViewSet)
router.register(r'constituents', views.ConstituentTypeViewSet)
router.register(r'qualityassurances', views.QualityAssuranceViewSet)
router.register(r'detectionlimits', views.DetectionLimitViewSet)
router.register(r'acids', views.AcidViewSet)
router.register(r'blankwaters', views.BlankWaterViewSet)
router.register(r'brominations', views.BrominationViewSet)
#router.register(r'roles', views.RoleViewSet)
#router.register(r'users', views.UserViewSet)
router.register(r'statuses', views.StatusTypeViewSet)
router.register(r'procedures', views.ProcedureTypeViewSet)

urlpatterns = patterns('',
                       url(r'^', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
                       )
