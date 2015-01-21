import json
import itertools
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from rest_framework import views, viewsets, permissions, authentication, exceptions, status
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer, TemplateHTMLRenderer
from mercuryservices.serializers import *
from mercuryservices.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView, BulkCreateModelMixin, BulkUpdateModelMixin


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
    permission_classes = (permissions.IsAuthenticated,)


class CooperatorViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Cooperator.objects.all()
    serializer_class = CooperatorSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Cooperator.objects.all()
        name = self.request.QUERY_PARAMS.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ProjectBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Project
    permission_classes = (permissions.IsAuthenticated,)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    #paginate_by = 100

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
    permission_classes = (permissions.IsAuthenticated,)


class SiteViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Site.objects.all()
    serializer_class = SiteSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Site.objects.all()
        #queryset = Site.objects.exclude(usgs_scode__exact="''")
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


class SampleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Sample
    permission_classes = (permissions.IsAuthenticated,)


class SampleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    paginate_by = 100

    def get_queryset(self):
        queryset = Sample.objects.all()
        id = self.request.QUERY_PARAMS.get('id', None)
        if id is not None:
            queryset = queryset.filter(id__exact=id)
        # a unique field sample is determined by project+site+time_stamp+depth+replicate
        project = self.request.QUERY_PARAMS.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__exact=project)
        site = self.request.QUERY_PARAMS.get('site', None)
        if site is not None:
            queryset = queryset.filter(site__exact=site)
        time_stamp = self.request.QUERY_PARAMS.get('time_stamp', None)
        if time_stamp is not None:
            queryset = queryset.filter(time_stamp__exact=time_stamp)
        depth = self.request.QUERY_PARAMS.get('depth', None)
        if depth is not None:
            queryset = queryset.filter(depth__exact=depth)
        replicate = self.request.QUERY_PARAMS.get('replicate', None)
        if replicate is not None:
            queryset = queryset.filter(replicate__exact=replicate)
        return queryset


class SampleBottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = SampleBottle
    permission_classes = (permissions.IsAuthenticated,)


class SampleBottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = SampleBottle.objects.all()
    serializer_class = SampleBottleSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    # def get_queryset(self):
    #     queryset = SampleBottle.objects.all()
    #     id = self.request.QUERY_PARAMS.get('id', None)
    #     if id is not None:
    #         id_list = id.split(',')
    #         queryset = queryset.filter(id__in=id_list)
    #     bottle = self.request.QUERY_PARAMS.get('bottle', None)
    #     if bottle is not None:
    #         queryset = queryset.filter(bottle__exact=bottle)
    #     sample = self.request.QUERY_PARAMS.get('sample', None)
    #     if sample is not None:
    #         queryset = queryset.filter(field_sample__exact=sample)
    #     return queryset
    def get_queryset(self):
        queryset = SampleBottle.objects.all().select_related('sample')
        project = self.request.QUERY_PARAMS.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(sample__project__in=project_list)
        site = self.request.QUERY_PARAMS.get('site', None)
        if site is not None:
            site_list = site.split(',')
            queryset = queryset.filter(sample__site__in=site_list)
        bottle = self.request.QUERY_PARAMS.get('bottle', None)
        if bottle is not None:
            bottle_list = bottle.split(',')
            queryset = queryset.filter(bottle__bottle_unique_name__in=bottle_list)
        date_after = self.request.QUERY_PARAMS.get('date_after', None)
        date_before = self.request.QUERY_PARAMS.get('date_before', None)
        if date_after is not None and date_before is not None:
            queryset = queryset.filter(sample__time_stamp__range=(date_after, date_before))
        elif date_after is not None:
                queryset = queryset.filter(sample__time_stamp__gt=date_after)
        elif date_before is not None:
            queryset = queryset.filter(sample__time_stamp__lt=date_before)
        return queryset


class FullSampleBottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FullSampleBottleSerializer
    paginate_by = 100

    def get_queryset(self):
        queryset = SampleBottle.objects.all().select_related()
        project = self.request.QUERY_PARAMS.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(sample__project__in=project_list)
        site = self.request.QUERY_PARAMS.get('site', None)
        if site is not None:
            site_list = site.split(',')
            queryset = queryset.filter(sample__site__in=site_list)
        bottle = self.request.QUERY_PARAMS.get('bottle', None)
        if bottle is not None:
            bottle_list = bottle.split(',')
            queryset = queryset.filter(bottle__bottle_unique_name__in=bottle_list)
        date_after = self.request.QUERY_PARAMS.get('date_after', None)
        date_before = self.request.QUERY_PARAMS.get('date_before', None)
        if date_after is not None and date_before is not None:
            queryset = queryset.filter(sample__time_stamp__range=(date_after, date_before))
        elif date_after is not None:
                queryset = queryset.filter(sample__time_stamp__gt=date_after)
        elif date_before is not None:
            queryset = queryset.filter(sample__time_stamp__lt=date_before)
        return queryset


class SampleBottleBrominationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = SampleBottleBromination.objects.all()
    serializer_class = SampleBottleBrominationSerializer
    paginate_by = 100


class BottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Bottle
    permission_classes = (permissions.IsAuthenticated,)


class BottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Bottle.objects.all()
    serializer_class = BottleSerializer
    paginate_by = 100

    def get_queryset(self):
        queryset = Bottle.objects.all()
        bottle_unique_name = self.request.QUERY_PARAMS.get('bottle_unique_name', None)
        if bottle_unique_name is not None:
            queryset = queryset.filter(bottle_unique_name__icontains=bottle_unique_name)
        return queryset


class BottleTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = BottleType.objects.all()
    serializer_class = BottleTypeSerializer


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


class ResultBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    model = Result
    permission_classes = (permissions.IsAuthenticated,)


class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Result.objects.all()
    serializer_class = ResultSerializer
    paginate_by = 100


class FullResultViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    #queryset = Result.objects.all()
    serializer_class = FullResultSerializer
    paginate_by = 100

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Result.objects.all()
        # if bottle is in query, only search by bottle and ignore other params
        bottle = self.request.QUERY_PARAMS.get('bottle', None)
        if bottle is not None:
            bottle_list = bottle.split(',')
            # if query values are IDs
            if bottle_list[0].isdigit():
                queryset = queryset.filter(sample_bottle__bottle_id__in=bottle_list)
            # if query values are names
            else:
                queryset = queryset.filter(sample_bottle__bottle__bottle_unique_name__in=bottle_list)
            return queryset
        # else, search by other params
        else:
            barcode = self.request.QUERY_PARAMS.get('barcode', None)
            if barcode is not None:
                queryset = queryset.filter(sample_bottle__exact=barcode)
            constituent = self.request.QUERY_PARAMS.get('constituent', None)
            if constituent is not None:
                queryset = queryset.filter(constituent__exact=constituent)
            isotope = self.request.QUERY_PARAMS.get('isotope', None)
            if isotope is not None:
                queryset = queryset.filter(isotope_flag__exact=isotope)
            project = self.request.QUERY_PARAMS.get('project', None)
            if project is not None:
                project_list = project.split(',')
                queryset = queryset.filter(sample_bottle__sample__project__in=project_list)
            site = self.request.QUERY_PARAMS.get('site', None)
            if site is not None:
                site_list = site.split(',')
                queryset = queryset.filter(sample_bottle__sample__site__in=site_list)
            depth = self.request.QUERY_PARAMS.get('depth', None)
            if depth is not None:
                queryset = queryset.filter(sample_bottle__sample__depth__exact=depth)
            replicate = self.request.QUERY_PARAMS.get('replicate', None)
            if replicate is not None:
                queryset = queryset.filter(sample_bottle__sample__replicate__exact=replicate)
            date_after = self.request.QUERY_PARAMS.get('date_after', None)
            date_before = self.request.QUERY_PARAMS.get('date_before', None)
            if date_after is not None and date_before is not None:
                queryset = queryset.filter(sample_bottle__sample__time_stamp__range=(date_after, date_before))
            elif date_after is not None:
                    queryset = queryset.filter(sample_bottle__sample__time_stamp__gt=date_after)
            elif date_before is not None:
                queryset = queryset.filter(sample_bottle__sample__time_stamp__lt=date_before)
            return queryset


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
        constituent = self.request.QUERY_PARAMS.get('constituent', None)
        if constituent is not None:
            queryset = queryset.filter(constituent__icontains=constituent)
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
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AcidSerializer
    paginate_by = 100


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
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BlankWaterSerializer
    paginate_by = 100


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
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BrominationSerializer
    paginate_by = 100


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


# class UserLoginView(views.APIView):
#     def post(self, request):
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 print("Logged In")
#                 data = UserSerializer(user).data
#                 return Response(data, status=status.HTTP_200_OK)
#             else:
#                 print("Account is disabled: {0}".format(username))
#                 data = json.dumps({"status": "Unauthorized", "message": "Your account is disabled."})
#                 return Response(data, status=status.HTTP_401_UNAUTHORIZED)
#
#         else:
#             print("Invalid login details: {0}, {1}".format(username, password))
#             data = json.dumps({"status": "Unauthorized", "message": "Invalid login details supplied."})
#             return Response(data, status=status.HTTP_401_UNAUTHORIZED)
#
#
# class UserLogoutView(views.APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def post(self, request):
#         logout(request)
#         print("Logged Out")
#
#         return Response({}, status=status.HTTP_204_NO_CONTENT)


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

