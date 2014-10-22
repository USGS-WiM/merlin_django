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
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView, BulkUpdateModelMixin
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

    def get_queryset(self):
        queryset = Cooperator.objects.all()
        name = self.request.QUERY_PARAMS.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class SiteViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


######
##
## Field Sample
##
######


class FieldSampleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = FieldSample.objects.all()
    serializer_class = FieldSampleSerializer


class FieldSampleBottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = FieldSampleBottle.objects.all()
    serializer_class = FieldSampleBottleSerializer


class BottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Bottle.objects.all()
    serializer_class = BottleSerializer


class FilterTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = FilterType.objects.all()
    serializer_class = FilterTypeSerializer


class PreservationTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = PreservationType.objects.all()
    serializer_class = PreservationTypeSerializer


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
    queryset = ConstituentType.objects.all()
    serializer_class = ConstituentTypeSerializer


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


class DetectionLimitViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = DetectionLimit.objects.all()
    serializer_class = DetectionLimitSerializer


######
##
## Solution
##
######


class AcidViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Acid.objects.all()
    serializer_class = AcidSerializer


class BlankWaterViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = BlankWater.objects.all()
    serializer_class = BlankWaterSerializer


class BrominationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Bromination.objects.all()
    serializer_class = BrominationSerializer


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

