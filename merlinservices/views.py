import logging
from datetime import datetime as dt
from django.utils import timezone
from rest_framework import views, viewsets, generics, permissions, authentication, filters
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_bulk import BulkCreateModelMixin, BulkUpdateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from merlinservices.serializers import *
from merlinservices.models import *
from merlinservices.renderers import *
from merlinservices.paginations import *
from merlinservices.filters import *


########################################################################################################################
#
# copyright: 2015 WiM - USGS
# authors: Aaron Stephenson USGS WiM (Web Informatics and Mapping)
#
# In Django, a view is what takes a Web request and returns a Web response. The response can be many things, but most
# of the time it will be a Web page, a redirect, or a document. In this case, the response will almost always be data
# in JSON format.
#
# All these views are written as Class-Based Views (https://docs.djangoproject.com/en/1.8/topics/class-based-views/)
# because that is the paradigm used by Django Rest Framework (http://www.django-rest-framework.org/api-guide/views/)
# which is the toolkit we used to create web services in Django.
#
#
########################################################################################################################


logger = logging.getLogger(__name__)


######
#
#  Abstract Base Classes
#
######


class AuthLastLoginMixin(object):
    """
    This class will update the user's last_login field each time a request is received
    """

    def finalize_response(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
        return super(AuthLastLoginMixin, self).finalize_response(request, *args, **kwargs)


class ModelFilterView(AuthLastLoginMixin, viewsets.ModelViewSet):
    """
    This class will automatically allow filtering and apply permissions to model view sets
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]


class ListFilterView(AuthLastLoginMixin, generics.ListAPIView):
    """
    This class will automatically allow filtering and apply permissions to list API views
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]

######
#
# Project and Site
#
######


# TODO: create an abstract class for ModelViewSets
class CooperatorBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Cooperator.objects.all()
    serializer_class = CooperatorSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CooperatorViewSet(ModelFilterView):
    serializer_class = CooperatorSerializer
    pagination_class = None
    queryset = Cooperator.objects.all()
    filterset_class = CooperatorFilter


class ProjectBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProjectViewSet(ModelFilterView):
    serializer_class = ProjectSerializer
    pagination_class = None
    queryset = Project.objects.all()
    filterset_class = ProjectFilter


class SiteBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SiteViewSet(ModelFilterView):
    serializer_class = SiteSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Site.objects.all()
    filterset_class = SiteFilter

    # TODO: put this method in an abstract class
    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class ProjectSiteBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSiteSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProjectSiteViewSet(ModelFilterView):
    serializer_class = ProjectSiteSerializer
    pagination_class = StandardResultsSetPagination
    queryset = ProjectSite.objects.all()
    filterset_class = ProjectSiteFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


######
#
# Field Sample
#
######


class SampleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = (permissions.IsAuthenticated,)


# Note that a unique field sample is determined by project+site+time_stamp+depth+replicate
class SampleViewSet(ModelFilterView):
    serializer_class = SampleSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Sample.objects.all()
    filterset_class = SampleFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class SampleBottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = SampleBottle.objects.all()
    serializer_class = SampleBottleSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SampleBottleViewSet(ModelFilterView):
    serializer_class = SampleBottleSerializer
    pagination_class = StandardResultsSetPagination
    queryset = SampleBottle.objects.all()
    filterset_class = SampleBottleFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class FullSampleBottleViewSet(ModelFilterView):
    serializer_class = FullSampleBottleSerializer
    pagination_class = StandardResultsSetPagination
    queryset = SampleBottle.objects.all()
    filterset_class = SampleBottleFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class SampleBottleBrominationBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = SampleBottleBromination.objects.all()
    serializer_class = SampleBottleBrominationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SampleBottleBrominationViewSet(ModelFilterView):
    serializer_class = SampleBottleBrominationSerializer
    pagination_class = StandardResultsSetPagination
    queryset = SampleBottleBromination.objects.all()
    filterset_class = SampleBottleBrominationFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class BottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Bottle.objects.all()
    serializer_class = BottleSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BottleViewSet(ModelFilterView):
    serializer_class = BottleSerializer
    queryset = Bottle.objects.all()
    filterset_class = BottleFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class BottlePrefixBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = BottlePrefix.objects.all()
    serializer_class = BottlePrefixSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BottlePrefixViewSet(ModelFilterView):
    serializer_class = BottlePrefixSerializer
    queryset = BottlePrefix.objects.all()
    filterset_class = BottlePrefixFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class BottleTypeViewSet(ModelFilterView):
    serializer_class = BottleTypeSerializer
    pagination_class = None
    queryset = BottleType.objects.all()
    filterset_class = BottleTypeFilter


class FilterTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = FilterType.objects.all()
    serializer_class = FilterTypeSerializer


class PreservationTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = PreservationType.objects.all()
    serializer_class = PreservationTypeSerializer


class ProcessingTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ProcessingType.objects.all()
    serializer_class = ProcessingTypeSerializer


class MediumTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = MediumType.objects.all()
    serializer_class = MediumTypeSerializer


######
#
# Method Analysis
#
######


class UnitTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer


class MethodTypeViewSet(ModelFilterView):
    serializer_class = MethodTypeSerializer
    queryset = MethodType.objects.all()
    filterset_class = MethodTypeFilter


class ResultBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ResultViewSet(ModelFilterView):
    serializer_class = ResultSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Result.objects.all()
    filterset_class = ResultFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class FullResultViewSet(ModelFilterView):
    pagination_class = StandardResultsSetPagination
    queryset = Result.objects.all()
    filterset_class = FullResultFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # override the default renderers to use a custom csv renderer when requested
    # note that these custom renderers have hard-coded field name headers that match the their respective serialzers
    # from when this code was originally written, so if the serializer fields change, these renderer field name headers
    # won't match the serializer data, until the renderer code is manually updated to match the serializer fields
    def get_renderers(self):
        frmt = self.request.query_params.get('format', None)
        if frmt is not None and frmt == 'csv':
            table = self.request.query_params.get('table', None)
            # if table is not specified or not equal to samples, assume results
            if table is not None and table == 'sample':
                renderer_classes = (PaginatedResultSampleCSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
            else:
                renderer_classes = (PaginatedResultCSVRenderer, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
        else:
            renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
        return [renderer_class() for renderer_class in renderer_classes]

    # override the default serializer_class if CSV format is specified
    def get_serializer_class(self):
        if self.request.accepted_renderer.format == 'csv':
            table = self.request.query_params.get('table', None)
            # if table is not specified or not equal to samples, assume results
            if table is not None and table == 'sample':
                return FlatResultSampleSerializer
            else:
                return FlatResultSerializer
        else:
            return FullResultSerializer

    # override the default finalize_response to assign a filename to CSV files
    # see https://github.com/mjumbewu/django-rest-framework-csv/issues/15
    def finalize_response(self, request, *args, **kwargs):
        # override the default page_size to use unlimited pagination for filtered CSV requests, and 100 for all others
        other_params = self.request.query_params.copy()
        if 'format' in other_params.keys():
            del other_params['format']
        if self.request.accepted_renderer.format == 'csv' and len(other_params) > 0:
            self.pagination_class = UnlimitedResultsSetPagination
        response = super(viewsets.ModelViewSet, self).finalize_response(request, *args, **kwargs)
        if self.request.accepted_renderer.format == 'csv':
            table = self.request.query_params.get('table', None)
            # if table is not specified or not equal to samples, assume results
            if table is not None and table == 'sample':
                table_name = 'samples'
            else:
                table_name = 'results'
            filename = table_name + '_'
            filename += dt.now().strftime("%Y") + '-' + dt.now().strftime("%m") + '-' + dt.now().strftime("%d") + '.csv'
            response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response


######
#
# Constituent
#
######


class AnalysisTypeViewSet(ModelFilterView):
    serializer_class = AnalysisTypeSerializer
    pagination_class = None
    queryset = AnalysisType.objects.all()
    filterset_class = AnalysisTypeFilter


class ConstituentTypeViewSet(ModelFilterView):
    serializer_class = ConstituentTypeSerializer
    pagination_class = None
    queryset = ConstituentType.objects.all()
    filterset_class = ConstituentTypeFilter


class AnalysisConstituentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = AnalysisConstituent.objects.all()
    serializer_class = AnalysisConstituentSerializer


class AnalysisMediumViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = AnalysisMedium.objects.all()
    serializer_class = AnalysisMediumSerializer


class AnalysisMethodViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = AnalysisMethod.objects.all()
    serializer_class = AnalysisMethodSerializer


######
#
# Quality Assurance
#
######


class QualityAssuranceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = QualityAssurance.objects.all()
    serializer_class = QualityAssuranceSerializer


class QualityAssuranceTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = QualityAssuranceType.objects.all()
    serializer_class = QualityAssuranceTypeSerializer


class DetectionFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = DetectionFlag.objects.all()
    serializer_class = DetectionFlagSerializer


class IsotopeFlagViewSet(ModelFilterView):
    serializer_class = IsotopeFlagSerializer
    pagination_class = None
    queryset = IsotopeFlag.objects.all()
    filterset_class = IsotopeFlagFilter


class ResultDataFileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ResultDataFile.objects.all()
    serializer_class = ResultDataFileSerializer


class BalanceVerificationBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = BalanceVerification.objects.all()
    serializer_class = BalanceVerificationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BalanceVerificationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = BalanceVerification.objects.all()
    serializer_class = BalanceVerificationSerializer
    pagination_class = StandardResultsSetPagination


class EquipmentViewSet(ModelFilterView):
    serializer_class = EquipmentSerializer
    pagination_class = None
    queryset = Equipment.objects.all()
    filterset_class = EquipmentFilter


class EquipmentTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = EquipmentType.objects.all()
    serializer_class = EquipmentTypeSerializer


######
#
# Solution
#
######


class AcidBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Acid.objects.all()
    serializer_class = AcidSerializer
    permission_classes = (permissions.IsAuthenticated,)


class AcidViewSet(ModelFilterView):
    serializer_class = AcidSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Acid.objects.all()
    filterset_class = AcidFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class BlankWaterBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = BlankWater.objects.all()
    serializer_class = BlankWaterSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BlankWaterViewSet(ModelFilterView):
    serializer_class = BlankWaterSerializer
    pagination_class = StandardResultsSetPagination
    queryset = BlankWater.objects.all()
    filterset_class = BlankWaterFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class BrominationBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Bromination.objects.all()
    serializer_class = BrominationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BrominationViewSet(ModelFilterView):
    serializer_class = BrominationSerializer
    pagination_class = StandardResultsSetPagination
    queryset = Bromination.objects.all()
    filterset_class = BrominationFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


#######
#
# Personnel
#
######


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, ]
    filterset_class = UserFilter


class AuthView(views.APIView):
    authentication_classes = (authentication.BasicAuthentication,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user = request.user if request is not None else None
        if user and user.is_authenticated:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
        return Response(self.serializer_class(request.user).data)


# class UserLoginView(views.APIView):
#     def post(self, request):
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 logger.info("Logged In")
#                 data = UserSerializer(user).data
#                 return Response(data, status=status.HTTP_200_OK)
#             else:
#                 logger.info("Account is disabled: {0}".format(username))
#                 data = json.dumps({"status": "Unauthorized", "message": "Your account is disabled."})
#                 return Response(data, status=status.HTTP_401_UNAUTHORIZED)
#
#         else:
#             logger.info("Invalid login details: {0}, {1}".format(username, password))
#             data = json.dumps({"status": "Unauthorized", "message": "Invalid login details supplied."})
#             return Response(data, status=status.HTTP_401_UNAUTHORIZED)
#
#
# class UserLogoutView(views.APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def post(self, request):
#         logout(request)
#         logger.info("Logged Out")
#
#         return Response({}, status=status.HTTP_204_NO_CONTENT)


######
#
# Reports
#
######


class ReportResultsCountNawqa(ListFilterView):
    serializer_class = ReportResultsCountNawqaSerializer
    queryset = ResultCountNawqa.objects.all()
    filterset_class = ReportResultsCountNawqaFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class ReportResultsCountProjects(ListFilterView):
    serializer_class = ReportResultsCountProjectsSerializer
    queryset = ResultCountProjects.objects.all()
    filterset_class = ReportResultsCountProjectsFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class ReportSamplesNwis(ListFilterView):
    serializer_class = ReportSamplesNwisSerializer
    queryset = SampleNwis.objects.all()
    filterset_class = ReportSamplesNwisFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class ReportResultsNwis(ListFilterView):
    serializer_class = ReportResultsNwisSerializer
    queryset = ResultNwis.objects.all()
    filterset_class = ReportResultsNwisFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)


class ReportResultsCooperator(ListFilterView):
    serializer_class = ReportResultsCooperatorSerializer
    queryset = ResultCooperator.objects.all()
    filterset_class = ReportResultsCooperatorFilter

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)
