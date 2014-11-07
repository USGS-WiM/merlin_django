from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer, TemplateHTMLRenderer
from mercuryservices.serializers import *
from mercuryservices.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView, BulkCreateModelMixin, BulkUpdateModelMixin
from rest_framework import filters


#The following lines were a test to see if Django Rest Framework could return responses to HTML instead of JSON.
# class ModelViewSetOverride(viewsets.ModelViewSet):
#     renderer_classes = (TemplateHTMLRenderer,)
#
#     def list(self, request, *args, **kwargs):
#         self.object = self.get_queryset()
#         cooperator_form = CooperatorForm()
#         return Response({'list': self.object, 'cooperator_form': cooperator_form}, template_name='mercurylab/list.html')
#
#     def retrieve(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         return Response({'item': self.object}, template_name='mercurylab/retrieve.html')
#
#     def create(self, request, *args, **kwargs):
#         form = CooperatorForm(request.POST)
#         if form.is_valid():
#             form.save(commit=True)
#         return Response({'list': self.get_queryset(), 'cooperator_form': CooperatorForm()}, template_name='mercurylab/list.html')



######
##
## Project and Site
##
######


class CooperatorBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Cooperator


class CooperatorViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Cooperator.objects.all()
    serializer_class = CooperatorSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Cooperator.objects.all()
        name = self.request.QUERY_PARAMS.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ProjectBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Project


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Project.objects.all()
        name = self.request.QUERY_PARAMS.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        id = self.request.QUERY_PARAMS.get('id', None)
        if id is not None:
            queryset = queryset.filter(id__icontains=id)
        return queryset


class SiteBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Site


class SiteViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Site.objects.all()
    serializer_class = SiteSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Site.objects.all()
        # filter by site name
        name = self.request.QUERY_PARAMS.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        # filter by site ID
        id = self.request.QUERY_PARAMS.get('id', None)
        if id is not None:
            queryset = queryset.filter(id__icontains=id)
        # filter by project name or ID
        project = self.request.QUERY_PARAMS.get('project', None)
        if project is not None:
            # if query value is a Project ID
            if project.isdigit():
                # get the Sites related to this Project ID
                queryset = queryset.filter(projects__exact=project)
            # if query value is a Site name
            else:
                # lookup the Project ID that matches this Project name
                id = Project.objects.get(name__exact=project)
                # get the Sites related to this Project ID
                queryset = queryset.filter(projects__exact=id)
        return queryset


######
##
## Field Sample
##
######


class FieldSampleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = FieldSample


class FieldSampleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = FieldSample.objects.all()
    serializer_class = FieldSampleSerializer


class FieldSampleBottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = FieldSampleBottle


class FieldSampleBottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = FieldSampleBottle.objects.all()
    serializer_class = FieldSampleBottleSerializer


class BottleBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Bottle


class BottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Bottle.objects.all()
    serializer_class = BottleSerializer
    paginate_by = 100

    def get_queryset(self):
        queryset = Bottle.objects.all()
        name = self.request.QUERY_PARAMS.get('name', None)
        if name is not None:
            queryset = queryset.filter(bottle_unique_name__icontains=name)
        return queryset


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

    #The following lines were a test to see if Django Rest Framework could return responses to HTML instead of JSON.
    # def list(self, request, *args, **kwargs):
    #     response = super(MediumTypeViewSet, self).list(request, *args, **kwargs)
    #     if request.accepted_renderer.format == 'html':
    #         return Response({'data': response.data}, template_name='mercury/mediums.html')
    #     return response
    #
    # def retrieve(self, request, *args, **kwargs):
    #     response = super(MediumTypeViewSet, self).retrieve(request, *args, **kwargs)
    #     if request.accepted_renderer.format == 'html':
    #         return Response({'data': response.data}, template_name='mercury/medium.html')
    #     return response


######
##
## Method Analysis
##
######


class UnitTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer


class MethodTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = MethodType.objects.all()
    serializer_class = MethodTypeSerializer


class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


######
##
## Constituent
##
######


class ConstituentTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = ConstituentType.objects.all()
    serializer_class = ConstituentTypeSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = ConstituentType.objects.all()
        medium = self.request.QUERY_PARAMS.get('medium', None)
        if medium is not None:
            # if query value is a Medium ID
            if medium.isdigit():
                # get the Constituents related to this Medium ID
                queryset = queryset.filter(mediums__exact=medium)
            # if query value is a Medium name
            else:
                # lookup the Medium ID that matches this Medium name
                id = MediumType.objects.get(medium__exact=medium)
                # get the Constituents related to this Medium ID
                queryset = queryset.filter(mediums__exact=id)
        return queryset


class ConstituentMediumViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ConstituentMedium.objects.all()
    serializer_class = ConstituentMediumSerializer


class ConstituentMethodViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ConstituentMethod.objects.all()
    serializer_class = ConstituentMethodSerializer


######
##
## Quality Assurance
##
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


class IsotopeFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = IsotopeFlag.objects.all()
    serializer_class = IsotopeFlagSerializer


######
##
## Solution
##
######


class AcidBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Acid


class AcidViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Acid.objects.all()
    serializer_class = AcidSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Acid.objects.all()
        code = self.request.QUERY_PARAMS.get('code', None)
        if code is not None:
            queryset = queryset.filter(code__icontains=code)
        return queryset


class BlankWaterBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = BlankWater


class BlankWaterViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = BlankWater.objects.all()
    serializer_class = BlankWaterSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = BlankWater.objects.all()
        lot_number = self.request.QUERY_PARAMS.get('lot_number', None)
        if lot_number is not None:
            queryset = queryset.filter(lot_number__icontains=lot_number)
        return queryset


class BrominationBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Bromination


class BrominationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Bromination.objects.all()
    serializer_class = BrominationSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Bromination.objects.all()
        id = self.request.QUERY_PARAMS.get('id', None)
        if id is not None:
            queryset = queryset.filter(id__icontains=id)
        date = self.request.QUERY_PARAMS.get('date', None)
        if date is not None:
            queryset = queryset.filter(bromination_date__icontains=date)
        return queryset


#######
##
## Personnel
##
######


# class RoleViewSet(viewsets.ModelViewSet):
#     queryset = Role.objects.all()
#     serializer_class = RoleSerializer
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


######
##
## Status
##
######


class StatusViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class ProcedureStatusTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ProcedureStatusType.objects.all()
    serializer_class = ProcedureStatusTypeSerializer


class StatusTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = StatusType.objects.all()
    serializer_class = StatusTypeSerializer


class ProcedureTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ProcedureType.objects.all()
    serializer_class = ProcedureTypeSerializer

