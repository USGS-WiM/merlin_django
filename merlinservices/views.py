import logging
import json
import time
import math
import decimal
import datetime as dtmod
from numbers import Number
from datetime import datetime as dt
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from django.db.models import Count
from django.db.models.base import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import views, viewsets, generics, permissions, authentication
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_bulk import BulkCreateModelMixin, BulkUpdateModelMixin
from merlinservices.serializers import *
from merlinservices.models import *
from merlinservices.renderers import *
from merlinservices.paginations import *


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
# Project and Site
#
######


# TODO: create an abstract class for ModelViewSets
class CooperatorBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Cooperator.objects.all()
    serializer_class = CooperatorSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CooperatorViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CooperatorSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Cooperator.objects.all()
        # filter by cooperator name, case-insensitive contain
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class ProjectBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ProjectSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Project.objects.all()
        # filter by project name, case-insensitive contain
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        # filter by project ID, exact
        project_id = self.request.query_params.get('id', None)
        if project_id is not None:
            queryset = queryset.filter(id__exact=project_id)
        return queryset


class SiteBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SiteViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = SiteSerializer
    pagination_class = StandardResultsSetPagination

    # TODO: put this method in an abstract class
    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Site.objects.all()
        # queryset = Site.objects.exclude(usgs_scode__exact="''")
        # filter by site name, exact
        name_exact = self.request.query_params.get('name_exact', None)
        if name_exact is not None:
            queryset = queryset.filter(name__exact=name_exact)
        # filter by site name, case-insensitive contain
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        # filter by site ID, exact
        site_id = self.request.query_params.get('id', None)
        if site_id is not None:
            queryset = queryset.filter(id__exact=site_id)
        # filter by site usgs scode, exact
        usgs_scode = self.request.query_params.get('usgs_scode', None)
        if usgs_scode is not None:
            queryset = queryset.filter(usgs_scode__exact=usgs_scode)
        # filter by project name or ID
        project = self.request.query_params.get('project', None)
        if project is not None:
            # if query value is a project ID
            if project.isdigit():
                # get the sites related to this project ID, exact
                queryset = queryset.filter(projects__exact=project)
            # else query value is a site name
            else:
                # lookup the project ID that matches this project name, exact
                project_id = Project.objects.get(name__exact=project)
                # get the sites related to this project ID, exact
                queryset = queryset.filter(projects__exact=project_id)
        return queryset


class ProjectSiteBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSiteSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProjectSiteViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ProjectSiteSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = ProjectSite.objects.all()
        project = self.request.query_params.get('project', None)
        if project is not None:
            # if query value is a project ID
            if project.isdigit():
                # get the projects-sites with this project ID, exact
                queryset = queryset.filter(project__exact=project)
            # else query value is a project name
            else:
                # lookup the projects-sites whose related projects contain this project name, case-insensitive
                queryset = queryset.filter(project__name__icontains=project)
        site = self.request.query_params.get('site', None)
        if site is not None:
            # if query value is a site ID
            if site.isdigit():
                # get the projects-sites with this site ID, eact
                queryset = queryset.filter(site__exact=site)
            # else query value is a project name
            else:
                # lookup the projects-sites whose related sites contain this site name, case-insensitive
                queryset = queryset.filter(site__name__icontains=site)
        return queryset


######
#
# Field Sample
#
######


class SampleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SampleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = SampleSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # Note that a unique field sample is determined by project+site+time_stamp+depth+replicate

    def get_queryset(self):
        queryset = Sample.objects.all()
        # filter by sample ID, exact
        sample_id = self.request.query_params.get('id', None)
        if sample_id is not None:
            queryset = queryset.filter(id__exact=sample_id)
        # filter by project ID, exact
        project = self.request.query_params.get('project', None)
        if project is not None:
            queryset = queryset.filter(project__exact=project)
        # filter by site ID, exact
        site = self.request.query_params.get('site', None)
        if site is not None:
            queryset = queryset.filter(site__exact=site)
        # filter by sample datetime, exact
        sample_date_time = self.request.query_params.get('sample_date_time', None)
        if sample_date_time is not None:
            queryset = queryset.filter(sample_date_time__exact=sample_date_time)
        # filter by depth, exact
        depth = self.request.query_params.get('depth', None)
        if depth is not None:
            queryset = queryset.filter(depth__exact=depth)
        # filter by replicate, exact
        replicate = self.request.query_params.get('replicate', None)
        if replicate is not None:
            queryset = queryset.filter(replicate__exact=replicate)
        # filter by medium type, exact
        medium_type = self.request.query_params.get('medium_type', None)
        if medium_type is not None:
            queryset = queryset.filter(medium_type__exact=medium_type)
        return queryset


class SampleBottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = SampleBottle.objects.all()
    serializer_class = SampleBottleSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SampleBottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = SampleBottleSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = SampleBottle.objects.all().select_related('sample')
        # filter by samplebottle ID, exact
        samplebottle_id = self.request.query_params.get('id', None)
        if samplebottle_id is not None:
            queryset = queryset.filter(id__exact=samplebottle_id)
        # filter by sample ID, exact
        sample_id = self.request.query_params.get('sample_id', None)
        if sample_id is not None:
            queryset = queryset.filter(sample__id__exact=sample_id)
        # filter by project IDs, exact list
        project = self.request.query_params.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(sample__project__in=project_list)
        # filter by site IDs, exact list
        site = self.request.query_params.get('site', None)
        if site is not None:
            site_list = site.split(',')
            queryset = queryset.filter(sample__site__in=site_list)
        # filter by bottle ID, exact
        bottle = self.request.query_params.get('bottle', None)
        if bottle is not None:
            queryset = queryset.filter(bottle__exact=bottle)
        # filter by bottle_string (bottle unique name)
        bottle_string = self.request.query_params.get('bottle_string', None)
        if bottle_string is not None:
            bottle_string_list = bottle_string.split(',')
            # if there is only one, chances are the user is trying to look up a specific bottle
            if len(bottle_string_list) == 1:
                try:
                    # look up this bottle
                    this_sample_bottle = SampleBottle.objects.get(bottle__bottle_unique_name=bottle_string_list[0])
                    # if there is one match, the user just wants the details of this bottle, so add it to the query set
                    if this_sample_bottle:
                        queryset = queryset.filter(bottle__bottle_unique_name__in=bottle_string_list)
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    # if there are multiple matches, or if it doesn't exist, then the submitted bottle value
                    # is not a full/valid bottle name, but just a partial name, so the user wants
                    # a list of bottles whose name contains the value
                    queryset = queryset.filter(bottle__bottle_unique_name__icontains=bottle_string_list[0])
            else:
                queryset = queryset.filter(bottle__bottle_unique_name__in=bottle_string_list)
        # filter by constituent IDs, exact list
        constituent = self.request.query_params.get('constituent', None)
        if constituent is not None:
            constituent_list = constituent.split(',')
            queryset = queryset.filter(results__constituent_id__in=constituent_list).distinct('id')
        # filter by sample datetime (after only, before only, or between both, depending on which URL params appear)
        date_after = self.request.query_params.get('date_after', None)
        date_before = self.request.query_params.get('date_before', None)
        # filtering datetime fields using only date is problematic
        # (see warning at https://docs.djangoproject.com/en/dev/ref/models/querysets/#range)
        # to properly do the date math on datetime fields,
        # set date_after to 23:59 of that date and date_before to 00:00 of that date
        if date_after is not None:
            date_after_plus = dt.combine(dt.strptime(date_after, '%Y-%m-%d').date(), dtmod.time.max)
        if date_before is not None:
            date_before_minus = dt.combine(dt.strptime(date_before, '%Y-%m-%d').date(), dtmod.time.min)
        if date_after is not None and date_before is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(sample__sample_date_time__range=(date_after_plus, date_before_minus))
            # the filter below is date-exclusive
            queryset = queryset.filter(sample__sample_date_time__gt=date_after_plus,
                                       sample__sample_date_time__lt=date_before_minus)
        elif date_after is not None:
            queryset = queryset.filter(sample__sample_date_time__gt=date_after_plus)
        elif date_before is not None:
            queryset = queryset.filter(sample__sample_date_time__lt=date_before_minus)
        return queryset


class FullSampleBottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FullSampleBottleSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = SampleBottle.objects.all().select_related()
        # filter by samplebottle ID, exact
        samplebottle_id = self.request.query_params.get('id', None)
        if samplebottle_id is not None:
            queryset = queryset.filter(id__exact=samplebottle_id)
        # filter by sample ID, exact
        sample_id = self.request.query_params.get('sample_id', None)
        if sample_id is not None:
            queryset = queryset.filter(sample__id__exact=sample_id)
        # filter by project IDs, exact list
        project = self.request.query_params.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(sample__project__in=project_list)
        # filter by site IDs, exact list
        site = self.request.query_params.get('site', None)
        if site is not None:
            site_list = site.split(',')
            queryset = queryset.filter(sample__site__in=site_list)
        # filter by bottle ID, exact
        bottle = self.request.query_params.get('bottle', None)
        if bottle is not None:
            bottle_list = bottle.split(',')
            queryset = queryset.filter(bottle__bottle_unique_name__in=bottle_list)
        # filter by constituent IDs, exact list
        constituent = self.request.query_params.get('constituent', None)
        if constituent is not None:
            constituent_list = constituent.split(',')
            queryset = queryset.filter(results__constituent_id__in=constituent_list)
        # filter by sample datetime (after only, before only, or between both, depending on which URL params appear)
        date_after = self.request.query_params.get('date_after', None)
        date_before = self.request.query_params.get('date_before', None)
        # filtering datetime fields using only date is problematic
        # (see warning at https://docs.djangoproject.com/en/dev/ref/models/querysets/#range)
        # to properly do the date math on datetime fields,
        # set date_after to 23:59 of that date and date_before to 00:00 of that date
        if date_after is not None:
            date_after_plus = dt.combine(dt.strptime(date_after, '%Y-%m-%d').date(), dtmod.time.max)
        if date_before is not None:
            date_before_minus = dt.combine(dt.strptime(date_before, '%Y-%m-%d').date(), dtmod.time.min)
        if date_after is not None and date_before is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(sample__sample_date_time__range=(date_after_plus, date_before_minus))
            # the filter below is date-exclusive
            queryset = queryset.filter(sample__sample_date_time__gt=date_after_plus,
                                       sample__sample_date_time__lt=date_before_minus)
        elif date_after is not None:
            queryset = queryset.filter(sample__sample_date_time__gt=date_after_plus)
        elif date_before is not None:
            queryset = queryset.filter(sample__sample_date_time__lt=date_before_minus)
        return queryset


class SampleBottleBrominationBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = SampleBottleBromination.objects.all()
    serializer_class = SampleBottleBrominationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SampleBottleBrominationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = SampleBottleBrominationSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        # logger.info(self.request.query_params)
        queryset = SampleBottleBromination.objects.all()
        # filter by bottle name or ID
        bottle = self.request.query_params.get('bottle', None)
        if bottle is not None:
            bottle_list = bottle.split(',')
            # if query values are IDs
            if bottle_list[0].isdigit():
                # logger.info(bottle_list[0])
                # queryset = queryset.filter(sample_bottle__bottle__id__in=bottle_list)
                clauses = ' '.join(['WHEN bottle_id=%s THEN %s' % (pk, i) for i, pk in enumerate(bottle_list)])
                ordering = 'CASE %s END' % clauses
                queryset = queryset.filter(sample_bottle__bottle__id__in=bottle_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                # logger.info(queryset)
            # else query values are names
            else:
                queryset = queryset.filter(sample_bottle__bottle__bottle_unique_name__in=bottle_list)
            return queryset
        # filter by created date (after only, before only, or between both, depending on which URL params appear)
        date_after = self.request.query_params.get('date_after', None)
        date_before = self.request.query_params.get('date_before', None)
        if date_after is not None and date_before is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(created_date__range=(date_after, date_before))
            # the filter below is date-exclusive
            queryset = queryset.filter(created_date__gt=date_after,
                                       created_date__lt=date_before)
        elif date_after is not None:
                queryset = queryset.filter(created_date__gt=date_after)
        elif date_before is not None:
            queryset = queryset.filter(created_date__lt=date_before)
        return queryset


class BottleBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Bottle.objects.all()
    serializer_class = BottleSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BottleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = BottleSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = Bottle.objects.all()
        # filter by bottle ID, exact
        bottle_id = self.request.query_params.get('id', None)
        if bottle_id is not None:
            queryset = queryset.filter(id__exact=bottle_id)
        # filter by bottle name, case-insensitive contain
        bottle_unique_name = self.request.query_params.get('bottle_unique_name', None)
        if bottle_unique_name is not None:
            if ',' in bottle_unique_name:
                bottle_list = bottle_unique_name.split(',')
                # maintain the order of the bottles that were queried
                clauses = ' '.join(['WHEN bottle_unique_name=\'%s\' THEN %s' % (pk, i) for i, pk in enumerate(bottle_list)])
                ordering = 'CASE %s END' % clauses
                queryset = queryset.filter(bottle_unique_name__in=bottle_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
            else:
                queryset = queryset.filter(bottle_unique_name__icontains=bottle_unique_name)
        # filter by unused bottles (i.e., bottles not yet used as sample bottles)
        unused = self.request.query_params.get('unused', None)
        if unused is not None:
            if unused == 'True' or unused == 'true':
                queryset = queryset.filter(sample_bottles=None)
        return queryset


class BottlePrefixBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = BottlePrefix.objects.all()
    serializer_class = BottlePrefixSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BottlePrefixViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = BottlePrefixSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = BottlePrefix.objects.all()
        # filter by bottle prefix ID, exact
        bottleprefix_id = self.request.query_params.get('id', None)
        if bottleprefix_id is not None:
            queryset = queryset.filter(id__exact=bottleprefix_id)
        # filter by bottle prefix name, exact
        bottle_prefix_exact = self.request.query_params.get('bottle_prefix_exact', None)
        if bottle_prefix_exact is not None:
            queryset = queryset.filter(bottle_prefix__exact=bottle_prefix_exact)
        # filter by bottle prefix ID or name
        bottle_prefix = self.request.query_params.get('bottle_prefix', None)
        if bottle_prefix is not None:
            # if query value is a bottle prefix ID
            if bottle_prefix.isdigit():
                # get the bottle prefix by ID, exact
                queryset = queryset.filter(id__exact=bottle_prefix)
            # if query value is a bottle prefix name
            else:
                # get the bottle prefix by name, case-insensitive contain
                queryset = queryset.filter(bottle_prefix__icontains=bottle_prefix)
        return queryset


class BottleTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = BottleTypeSerializer

    def get_queryset(self):
        queryset = BottleType.objects.all()
        # filter by bottle_type_string (bottle type name), exact
        bottle_type_string = self.request.query_params.get('bottle_type_string', None)
        if bottle_type_string is not None:
            queryset = queryset.filter(bottle_type__exact=bottle_type_string)
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


######
#
# Method Analysis
#
######


class UnitTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = UnitType.objects.all()
    serializer_class = UnitTypeSerializer


class MethodTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MethodTypeSerializer

    def get_queryset(self):
        queryset = MethodType.objects.all()
        # filter by analysis ID, exact
        analysis = self.request.query_params.get('analysis', None)
        if analysis is not None:
            queryset = queryset.filter(analyses__exact=analysis)
        # filter by constituent ID, exact
        constituent = self.request.query_params.get('constituent', None)
        if constituent is not None:
            queryset = queryset.filter(analyses__constituents__exact=constituent)
        # filter by method name, exact
        method_name = self.request.query_params.get('method', None)
        if method_name is not None:
            queryset = queryset.filter(method__exact=method_name)
        # filter by method ID, exact
        method_id = self.request.query_params.get('id', None)
        if method_id is not None:
            queryset = queryset.filter(id__exact=method_id)
        return queryset


class ResultBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ResultViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ResultSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = Result.objects.all()
        # filter by sample bottle ID, exact
        sample_bottle = self.request.query_params.get('sample_bottle', None)
        if sample_bottle is not None:
            queryset = queryset.filter(sample_bottle__exact=sample_bottle)
        # filter by constituent ID, exact
        constituent = self.request.query_params.get('constituent', None)
        if constituent is not None:
            if constituent.isdigit():
                queryset = queryset.filter(constituent__exact=constituent)
            else:
                queryset = queryset.filter(constituent__constituent__exact=constituent)
        # filter by analysis ID, exact
        analysis = self.request.query_params.get('analysis', None)
        if analysis is not None:
            if analysis.isdigit():
                queryset = queryset.filter(analysis__exact=analysis)
            else:
                queryset = queryset.filter(analysis__analysis__exact=analysis)
        # filter by isotope ID, exact
        isotope_flag = self.request.query_params.get('isotope_flag', None)
        if isotope_flag is not None:
            queryset = queryset.filter(isotope_flag__exact=isotope_flag)
        return queryset


class FullResultViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = StandardResultsSetPagination

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

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        # queryset = Result.objects.all()
        # prefetch_related only the exact, necessary fields to greatly improve the response time of the query
        queryset = Result.objects.all().prefetch_related(
            'sample_bottle', 'sample_bottle__bottle',
            'sample_bottle__bottle__bottle_prefix', 'sample_bottle__sample',
            'sample_bottle__sample__site', 'sample_bottle__sample__project', 'constituent', 'isotope_flag',
            'detection_flag', 'method'
        )

        # if bottle is in query, only search by bottle and ignore other params
        bottle = self.request.query_params.get('bottle', None)
        if bottle is not None:
            bottle_list = bottle.split(',')
            # if query values are IDs, match exact list of bottle IDs
            if bottle_list[0].isdigit():
                # logger.info(bottle_list[0])
                # queryset = queryset.filter(sample_bottle__bottle__id__in=bottle_list)
                # maintain the order of the bottles that were queried
                clauses = ' '.join(['WHEN bottle_id=%s THEN %s' % (pk, i) for i, pk in enumerate(bottle_list)])
                ordering = 'CASE %s END' % clauses
                queryset = queryset.filter(sample_bottle__bottle__id__in=bottle_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
                #  logger.info(queryset)
            # if query values are names, match exact list of bottle unique names
            else:
                # queryset = queryset.filter(sample_bottle__bottle__bottle_unique_name__in=bottle_list)
                # maintain the order of the bottles that were queried
                clauses = ' '.join(
                    ["WHEN bottle_unique_name='%s' THEN %s" % (pk, i) for i, pk in enumerate(bottle_list)])
                ordering = 'CASE %s END' % clauses
                queryset = queryset.filter(sample_bottle__bottle__bottle_unique_name__in=bottle_list).extra(
                    select={'ordering': ordering}, order_by=('ordering',))
            # filter by analysis ID, exact list
            analysis = self.request.query_params.get('analysis', None)
            if analysis is not None:
                analysis_list = analysis.split(',')
                queryset = queryset.filter(analysis__in=analysis_list)
            # filter by constituent ID, exact list
            constituent = self.request.query_params.get('constituent', None)
            if constituent is not None:
                constituent_list = constituent.split(',')
                queryset = queryset.filter(constituent__in=constituent_list)
            # if exclude_null_results is a param, then exclude null results, otherwise return all results
            exclude_null_results = self.request.query_params.get('exclude_null_results')
            if exclude_null_results is not None:
                if exclude_null_results == 'True' or exclude_null_results == 'true':
                    queryset = queryset.filter(final_value__isnull=False)
                # elif exclude_null_results == 'False' or exclude_null_results == 'false':
                #    queryset = queryset.filter(final_value__isnull=True)
            return queryset
        # else, search by other params (that don't include bottle ID or name)
        else:
            # barcode = self.request.query_params.get('barcode', None)
            # if barcode is not None:
            #    queryset = queryset.filter(sample_bottle__exact=barcode)
            # if exclude_null_results is a param, then exclude null results, otherwise return all results
            exclude_null_results = self.request.query_params.get('exclude_null_results')
            if exclude_null_results is not None:
                if exclude_null_results == 'True' or exclude_null_results == 'true':
                    queryset = queryset.filter(final_value__isnull=False)
                # elif exclude_null_results == 'False' or exclude_null_results == 'false':
                #    queryset = queryset.filter(final_value__isnull=True)
            # filter by analysis ID, exact list
            analysis = self.request.query_params.get('analysis', None)
            if analysis is not None:
                analysis_list = analysis.split(',')
                queryset = queryset.filter(analysis__in=analysis_list)
            # filter by constituent ID, exact list
            constituent = self.request.query_params.get('constituent', None)
            if constituent is not None:
                constituent_list = constituent.split(',')
                queryset = queryset.filter(constituent__in=constituent_list)
            # filter by isotope ID, exact
            isotope_flag = self.request.query_params.get('isotope_flag', None)
            if isotope_flag is not None:
                queryset = queryset.filter(isotope_flag__exact=isotope_flag)
            # filter by project ID, exact list
            project = self.request.query_params.get('project', None)
            if project is not None:
                project_list = project.split(',')
                queryset = queryset.filter(sample_bottle__sample__project__in=project_list)
            # filter by site ID, exact list
            site = self.request.query_params.get('site', None)
            if site is not None:
                site_list = site.split(',')
                queryset = queryset.filter(sample_bottle__sample__site__in=site_list)
            # filter by depth, exact
            depth = self.request.query_params.get('depth', None)
            if depth is not None:
                queryset = queryset.filter(sample_bottle__sample__depth__exact=depth)
            # filter by replicate, exact
            replicate = self.request.query_params.get('replicate', None)
            if replicate is not None:
                queryset = queryset.filter(sample_bottle__sample__replicate__exact=replicate)
            # filter by sample date (after only, before only, or between both, depending on which URL params appear)
            # remember that sample date is actually a date time object, so convert it to date before doing date math
            date_search_type = self.request.query_params.get('date_search_type', None)
            date_after_sample = self.request.query_params.get('date_after_sample', None)
            date_before_sample = self.request.query_params.get('date_before_sample', None)
            # filtering datetime fields using only date is problematic
            # (see warning at https://docs.djangoproject.com/en/dev/ref/models/querysets/#range)
            # to properly do the date math on datetime fields,
            # set date_after to 23:59 of the current date and date_before to 00:00 of the same day
            if date_after_sample is not None:
                date_after_sample_plus = dt.combine(dt.strptime(date_after_sample, '%Y-%m-%d').date(), dtmod.time.max)
                date_after_sample_minus = dt.combine(dt.strptime(date_after_sample, '%Y-%m-%d').date(), dtmod.time.min)
            if date_before_sample is not None:
                date_before_sample_minus = dt.combine(
                        dt.strptime(date_before_sample, '%Y-%m-%d').date(), dtmod.time.min)
                date_before_sample_plus = dt.combine(
                    dt.strptime(date_before_sample, '%Y-%m-%d').date(), dtmod.time.max)
            if date_search_type == "exclusive":
                if date_after_sample is not None and date_before_sample is not None:
                    # the filter below is date-exclusive
                    queryset = queryset.filter(sample_bottle__sample__sample_date_time__gt=date_after_sample_plus,
                                               sample_bottle__sample__sample_date_time__lt=date_before_sample_minus)
                elif date_after_sample is not None:
                    queryset = queryset.filter(sample_bottle__sample__sample_date_time__gt=date_after_sample_plus)
                elif date_before_sample is not None:
                    queryset = queryset.filter(sample_bottle__sample__sample_date_time__lt=date_before_sample_minus)
                # filter by entry date (after only, before only, or between both, depending on which URL params appear)
                date_after_entry = self.request.query_params.get('date_after_entry', None)
                date_before_entry = self.request.query_params.get('date_before_entry', None)
                if date_after_entry is not None and date_before_entry is not None:
                    # the filter below is date-exclusive
                    queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
                elif date_after_entry is not None:
                    queryset = queryset.filter(entry_date__gt=date_after_entry)
                elif date_before_entry is not None:
                    queryset = queryset.filter(entry_date__lt=date_before_entry)
            else:
                if date_after_sample is not None and date_before_sample is not None:
                    # __range is date-inclusive
                    queryset = queryset.filter(sample_bottle__sample__sample_date_time__gte=date_after_sample_minus,
                                               sample_bottle__sample__sample_date_time__lte=date_before_sample_plus)
                elif date_after_sample is not None:
                    queryset = queryset.filter(sample_bottle__sample__sample_date_time__gte=date_after_sample_minus)
                elif date_before_sample is not None:
                    queryset = queryset.filter(sample_bottle__sample__sample_date_time__lte=date_before_sample_plus)
                # filter by entry date (after only, before only, or between both, depending on which URL params appear)
                date_after_entry = self.request.query_params.get('date_after_entry', None)
                date_before_entry = self.request.query_params.get('date_before_entry', None)
                if date_after_entry is not None and date_before_entry is not None:
                    # __range is date-inclusive
                    queryset = queryset.filter(entry_date__gte=date_after_entry, entry_date__lte=date_before_entry)
                elif date_after_entry is not None:
                    queryset = queryset.filter(entry_date__gte=date_after_entry)
                elif date_before_entry is not None:
                    queryset = queryset.filter(entry_date__lte=date_before_entry)
            return queryset


######
#
# Constituent
#
######


class AnalysisTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = AnalysisTypeSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = AnalysisType.objects.all()
        # filter by method ID or name
        method = self.request.query_params.get('method', None)
        if method is not None:
            # if query value is a method ID
            if method.isdigit():
                # get the constituents related to this method ID, exact
                queryset = queryset.filter(methods__exact=method)
            # else query value is a method name
            else:
                # lookup the method ID that matches this method name, exact
                method_id = MethodType.objects.get(methods__exact=method)
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(methods__exact=method_id)
        # filter by medium ID or name
        medium = self.request.query_params.get('medium', None)
        if medium is not None:
            # if query value is a medium ID
            if medium.isdigit():
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(mediums__exact=medium)
            # else query value is a medium name
            else:
                # lookup the medium ID that matches this medium name, exact
                medium_id = MediumType.objects.get(mediums__exact=medium)
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(mediums__exact=medium_id)
        # filter by nwis code, exact
        nwis_code = self.request.query_params.get('nwis_code', None)
        if nwis_code is not None:
            queryset = queryset.filter(mediums__nwis_code__exact=nwis_code)
        # filter by analysis name, case-insensitive contain
        analysis = self.request.query_params.get('analysis', None)
        if analysis is not None:
            queryset = queryset.filter(analysis__icontains=analysis)
        # filter by analysis ID, exact
        analysis_id = self.request.query_params.get('id', None)
        if analysis_id is not None:
            queryset = queryset.filter(id__exact=analysis_id)
        return queryset


class ConstituentTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ConstituentTypeSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = ConstituentType.objects.all()
        # filter by analysis ID or name
        analysis = self.request.query_params.get('analysis', None)
        if analysis is not None:
            # if query value is an analysis ID
            if analysis.isdigit():
                # get the constituents related to this analysis ID, exact
                queryset = queryset.filter(analyses__exact=analysis)
            # else query value is an analysis name
            else:
                # lookup the analysis ID that matches this analysis name, exact
                analysis_id = AnalysisType.objects.get(analysis__exact=analysis)
                # get the constituents related to this analysis ID, exact
                queryset = queryset.filter(analyses__exact=analysis_id)
        # filter by method ID or name
        method = self.request.query_params.get('method', None)
        if method is not None:
            # if query value is a method ID
            if method.isdigit():
                # get the constituents related to this method ID, exact
                queryset = queryset.filter(analyses__methods__exact=method)
            # else query value is a method name
            else:
                # lookup the method ID that matches this method name, exact
                method_id = MethodType.objects.get(analyses__methods__exact=method)
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(analyses__methods__exact=method_id)
        # filter by medium ID or name
        medium = self.request.query_params.get('medium', None)
        if medium is not None:
            # if query value is a medium ID
            if medium.isdigit():
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(analyses__mediums__exact=medium)
            # else query value is a medium name
            else:
                # lookup the medium ID that matches this medium name, exact
                medium_id = MediumType.objects.get(analyses__mediums__exact=medium)
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(analyses__mediums__exact=medium_id)
        # filter by nwis code, exact
        nwis_code = self.request.query_params.get('nwis_code', None)
        if nwis_code is not None:
            queryset = queryset.filter(analyses__mediums__nwis_code__exact=nwis_code)
        # filter by constituent name, case-insensitive contain
        constituent = self.request.query_params.get('constituent', None)
        if constituent is not None:
            queryset = queryset.filter(constituent__icontains=constituent)
        # filter by constituent ID, exact
        constituent_id = self.request.query_params.get('id', None)
        if constituent_id is not None:
            queryset = queryset.filter(id__exact=constituent_id)
        return queryset


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


class ResultQualityAssuranceFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ResultQualityAssuranceFlag.objects.all()
    serializer_class = ResultQualityAssuranceFlagSerializer


class QualityAssuranceFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = QualityAssuranceFlag.objects.all()
    serializer_class = QualityAssuranceFlagSerializer


class QualityAssuranceBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = QualityAssurance.objects.all()
    serializer_class = QualityAssuranceSerializer
    permission_classes = (permissions.IsAuthenticated,)


class QualityAssuranceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = QualityAssurance.objects.all()
    serializer_class = QualityAssuranceSerializer
    pagination_class = StandardResultsSetPagination


class QualityAssuranceTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = QualityAssuranceTypeSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = QualityAssuranceType.objects.all()
        # filter by quality assurance name, exact
        qa_name = self.request.query_params.get('name', None)
        if qa_name is not None:
            queryset = queryset.filter(name__exact=qa_name)
        return queryset


class StandardQualityAssuranceCode(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = StandardQualityAssuranceCode.objects.all()
    serializer_class = StandardQualityAssuranceCodeSerializer


class StandardBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes = (permissions.IsAuthenticated,)


class StandardViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = StandardSerializer
    pagination_class = StandardResultsSetPagination

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Standard.objects.all()
        # filter by bottle name, exact
        bottle_name = self.request.query_params.get('name', None)
        if bottle_name is not None:
            queryset = queryset.filter(bottle__botle_unique_name__exact=bottle_name)
        return queryset


class DetectionFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = DetectionFlag.objects.all()
    serializer_class = DetectionFlagSerializer


class IsotopeFlagViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = IsotopeFlagSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = IsotopeFlag.objects.all()
        # filter by isotope ID, case-insensitive contain
        isotope_id = self.request.query_params.get('id', None)
        if isotope_id is not None:
            queryset = queryset.filter(id__icontains=isotope_id)
        return queryset


class ResultDataFileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ResultDataFile.objects.all()
    serializer_class = ResultDataFileSerializer


class EquipmentVerificationBulkCreateUpdateViewSet(BulkCreateModelMixin, BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = EquipmentVerification.objects.all()
    serializer_class = EquipmentVerificationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class EquipmentVerificationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = EquipmentVerification.objects.all()
    serializer_class = EquipmentVerificationSerializer
    pagination_class = StandardResultsSetPagination


class EquipmentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = EquipmentSerializer

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Equipment.objects.all()
        # filter by type, exact
        type = self.request.query_params.get('type', None)
        if type is not None:
            queryset = queryset.filter(type__exact=type)
        # filter by serial_number, case-insensitive contain
        serial_number = self.request.query_params.get('serial_number', None)
        if serial_number is not None:
            queryset = queryset.filter(serial_number__icontains=serial_number)
        return queryset


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


class AcidViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = AcidSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Acid.objects.all()
        # filter by acid code, exact
        code_exact = self.request.query_params.get('code_exact', None)
        if code_exact is not None:
            queryset = queryset.filter(code__exact=code_exact)
        # filter by acid code, case-insensitive contain
        code = self.request.query_params.get('code', None)
        if code is not None:
            queryset = queryset.filter(code__icontains=code)
        return queryset


class BlankWaterBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = BlankWater.objects.all()
    serializer_class = BlankWaterSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BlankWaterViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = BlankWaterSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = BlankWater.objects.all()
        # filter by lot number, case-insensitive contain
        lot_number = self.request.query_params.get('lot_number', None)
        if lot_number is not None:
            queryset = queryset.filter(lot_number__icontains=lot_number)
        return queryset


class BrominationBulkUpdateViewSet(BulkUpdateModelMixin, viewsets.ModelViewSet):
    queryset = Bromination.objects.all()
    serializer_class = BrominationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class BrominationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = BrominationSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    # override the default queryset to allow filtering by URL arguments
    def get_queryset(self):
        queryset = Bromination.objects.all()
        # filter by bromination ID, case-insensitive contain
        bromination_id = self.request.query_params.get('id', None)
        if bromination_id is not None:
            queryset = queryset.filter(id__icontains=bromination_id)
        # filter by created date
        date = self.request.query_params.get('date', None)
        if date is not None:
            queryset = queryset.filter(created_date__icontains=date)
        return queryset


#######
#
# Personnel
#
######


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('-last_login')
        # filter by username, exact
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(username__exact=username)
        return queryset


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


class ReportResultsCountNawqa(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReportResultsCountNawqaSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = ResultCountNawqa.objects.all()
        # filter by entry date (after only, before only, or between both, depending on which URL params appear)
        date_search_type = self.request.query_params.get('date_search_type', None)
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_search_type == "exclusive":
            if date_after_entry is not None and date_before_entry is not None:
                # the filter below is date-exclusive
                queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gt=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lt=date_before_entry)
        else:
            if date_after_entry is not None and date_before_entry is not None:
                # __range is date-inclusive
                queryset = queryset.filter(entry_date__gte=date_after_entry, entry_date__lte=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gte=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lte=date_before_entry)
        # create a new column for counts that doesn't appear in the database view, using the Django annotate() method,
        # which will count the number of records after the date filter has been applied, rather than before,
        # (which is what would happen if we had a count column in the database view)
        queryset = queryset.values('project_name', 'site_name').annotate(count=Count('project_name'))
        return queryset


class ReportResultsCountProjects(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReportResultsCountProjectsSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = ResultCountProjects.objects.all()
        # filter by entry date (after only, before only, or between both, depending on which URL params appear)
        date_search_type = self.request.query_params.get('date_search_type', None)
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_search_type == "exclusive":
            if date_after_entry is not None and date_before_entry is not None:
                # the filter below is date-exclusive
                queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gt=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lt=date_before_entry)
        else:
            if date_after_entry is not None and date_before_entry is not None:
                # the filter below is date-exclusive
                queryset = queryset.filter(entry_date__gte=date_after_entry, entry_date__lte=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gte=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lte=date_before_entry)
        # create a new column for counts that doesn't appear in the database view, using the Django annotate() method,
        # which will count the number of records after the date filter has been applied, rather than before,
        # (which is what would happen if we had a count column in the database view)
        queryset = queryset.values(
            'project_name', 'nwis_customer_code', 'cooperator_email').annotate(count=Count('project_name'))
        return queryset


class ReportSamplesNwis(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReportSamplesNwisSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = SampleNwis.objects.all()
        project = self.request.query_params.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(project_name__in=project_list)
        project_not = self.request.query_params.get('project_not', None)
        if project_not is not None:
            project_not_list = project_not.split(',')
            queryset = queryset.exclude(project_name__in=project_not_list)
        date_search_type = self.request.query_params.get('date_search_type', None)
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_search_type == "exclusive":
            if date_after_entry is not None and date_before_entry is not None:
                # the filter below is date-exclusive
                queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gt=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lt=date_before_entry)
        else:
            if date_after_entry is not None and date_before_entry is not None:
                # __range is date-inclusive
                queryset = queryset.filter(entry_date__gte=date_after_entry, entry_date__lte=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gte=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lte=date_before_entry)
        # Because of the design of the underlying database view (originally written in Oracle for Starlims, and migrated
        # to PostgreSQL for Merlin), which uses entry_dates from the results table and not the sample table, there
        # can be many records from the database view whose values are identical except for the entry_date column.
        # This is a problem, because NWIS requires only one record per sample. The following distinct() method call
        # will return just one record per occurrence of a unique sample_integer. Since all the other values are the same
        # for each occurrence of a sample_integer (except for entry_date, which isn't sent to NWIS), there is no risk
        # in doing this, and it gets us exactly the data we need, in the format we need. Finally, the reason for calling
        # the .distinct() method at the end, rather than at the beginning, is because a user needs to be able to filter
        # by any possible entry_date associated with a sample_integer, not just one entry_date, so we need the full set
        # available for filtering, but just the distinct set to send back to the user after filtering.
        queryset = queryset.distinct('sample_integer')
        return queryset


class ReportResultsNwis(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReportResultsNwisSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = ResultNwis.objects.all()
        exclude_ld = self.request.query_params.get('exclude_ld', None)
        if exclude_ld is not None:
            if exclude_ld == 'True' or exclude_ld == 'true':
                # parameter_cd for length is '00024' and depth is '00098'
                queryset = queryset.exclude(parameter_cd__exact='00024').exclude(parameter_cd__exact='00098')
        project = self.request.query_params.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(project_name__in=project_list)
        project_not = self.request.query_params.get('project_not', None)
        if project_not is not None:
            project_not_list = project_not.split(',')
            queryset = queryset.exclude(project_name__in=project_not_list)
        date_search_type = self.request.query_params.get('date_search_type', None)
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_search_type == "exclusive":
            if date_after_entry is not None and date_before_entry is not None:
                # the filter below is date-exclusive
                queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gt=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lt=date_before_entry)
        else:
            if date_after_entry is not None and date_before_entry is not None:
                # __range is date-inclusive
                queryset = queryset.filter(entry_date__gte=date_after_entry, entry_date__lte=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gte=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lte=date_before_entry)
        return queryset


class ReportResultsCooperator(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ReportResultsCooperatorSerializer
    pagination_class = StandardResultsSetPagination

    # override the default pagination to allow disabling of pagination
    def paginate_queryset(self, *args, **kwargs):
        if not self.request:
            return super().paginate_queryset(*args, **kwargs)
        elif 'no_page' in self.request.query_params:
            return None
        return super().paginate_queryset(*args, **kwargs)

    def get_queryset(self):
        queryset = ResultCooperator.objects.all()
        cooperator = self.request.query_params.get('cooperator', None)
        if cooperator is not None:
            cooperator_list = cooperator.split(',')
            queryset = queryset.filter(cooperator_name__in=cooperator_list)
        project = self.request.query_params.get('project', None)
        if project is not None:
            project_list = project.split(',')
            queryset = queryset.filter(project_name__in=project_list)
        project_not = self.request.query_params.get('project_not', None)
        if project_not is not None:
            project_not_list = project_not.split(',')
            queryset = queryset.exclude(project_name__in=project_not_list)
        date_search_type = self.request.query_params.get('date_search_type', None)
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_search_type == "exclusive":
            if date_after_entry is not None and date_before_entry is not None:
                # the filter below is date-exclusive
                queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gt=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lt=date_before_entry)
        else:
            if date_after_entry is not None and date_before_entry is not None:
                # __range is date-inclusive
                queryset = queryset.filter(entry_date__gte=date_after_entry, entry_date__lte=date_before_entry)
            elif date_after_entry is not None:
                queryset = queryset.filter(entry_date__gte=date_after_entry)
            elif date_before_entry is not None:
                queryset = queryset.filter(entry_date__lte=date_before_entry)
        return queryset


######
#
# Batch Upload
#
######


# batch_upload_save: validation
class BatchUpload(views.APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        status = []
        data = []
        try:
            data = json.loads(request.body.decode('utf-8'))
            for row in data:
                # validate sample id/bottle bar code
                is_valid, message, bottle_id, sample, volume_filtered = validate_bottle_bar_code(row)
                if not is_valid:
                    status.append({"message": message, "success": "false"})
                    continue
                
                # get bottle_unique_name
                bottle_unique_name = row["bottle_unique_name"]
                
                # validate constituent type
                is_valid, message, constituent_id = validate_constituent_type(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # validate analysis type
                is_valid, message, analysis_id = validate_analysis_type(row)
                if not is_valid:
                    status.append(
                        {"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # validate analysis method type
                is_valid, message, analysis_method_id = validate_analysis_method(constituent_id, row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                is_valid, message, isotope_flag_id = validate_isotope_flag(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # validate quality assurance flags
                is_valid, message, quality_assurance_flag_id_array = validate_quality_assurance_flag(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                is_valid, message = validate_analyzed_date(row)
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue
                # get sample_mass_processed and sediment_dry_weight if given
                try:
                    sample_mass_processed = row["sample_mass_processed"]
                except KeyError:
                    sample_mass_processed = None
                try:
                    sediment_dry_weight = row["sediment_dry_weight"]
                except KeyError:
                    sediment_dry_weight = None
        
                # validate result
                # get method id
                method_id = row["method_id"]
                is_valid, message, result_id = validate_result(
                    sample, constituent_id, method_id, analysis_id, row
                )
                if not is_valid:
                    status.append({"message": message, "success": "false", "bottle_unique_name": bottle_unique_name})
                    continue

                # calculate the result
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_result(
                    row, result_id
                )
                raw_value = row["raw_value"]

                # SAVE THE RESULT #
                result_details = Result.objects.get(id=result_id)
                result_details.raw_value = float(raw_value)
                result_details.method_id = method_id

                # get and process the final_value
                result_details.final_value = float(raw_value)
                result_details.final_value = process_final_value(
                    result_details.final_value, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed,
                    result_id)

                # calculate the final_method_detection_limit and report value
                method_detection_limit, significant_figures, decimal_places = get_method_type(method_id)
                final_method_detection_limit = process_method_daily_detection_limit(
                    method_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed)
                result_details.final_method_detection_limit = final_method_detection_limit
#                if (
#                        method_detection_limit is not None
#                        and result_details.final_value is not None
#                        and result_details.final_value < method_detection_limit
#                ):
#                    result_details.report_value = final_method_detection_limit
#                else:
                result_details.report_value = process_report_value(reported_value, method_id, volume_filtered,
                                                                   sediment_dry_weight, sample_mass_processed, result_id)
                # round by sigfigs
                if significant_figures is not None and decimal_places is not None:
                    result_details.report_value = eval_sigfigs_decimals(result_details.report_value,
                                                                        significant_figures, decimal_places)
                
                result_details.detection_flag = DetectionFlag.objects.get(detection_flag=detection_flag)

                # daily detection limit
                result_details.raw_daily_detection_limit = daily_detection_limit
                result_details.final_daily_detection_limit = process_daily_detection_limit(
                    daily_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed)

                result_details.entry_date = time.strftime("%Y-%m-%d")
                if row["analysis_comment"]:
                    result_details.analysis_comment = row["analysis_comment"]
                else:
                    result_details.analysis_comment = ""
                if row["analyzed_date"]:
                    analyzed_date = row["analyzed_date"]
                    analyzed_date = dt.strptime(analyzed_date, "%m/%d/%Y")
                    result_details.analyzed_date = analyzed_date
                else:
                    result_details.analyzed_date = ""
                if row["percent_matching"]:
                    result_details.percent_matching = row["percent_matching"]
                else:
                    result_details.percent_matching = None
                result_details.save()
                # save result quality assurance flags
                quality_assurance_flag_id_array = quality_assurance_flag_id_array + qa_flags
                for quality_assurance_flag_id in quality_assurance_flag_id_array:
                    ResultQualityAssuranceFlag.objects.create(
                        result_id=result_id, quality_assurance_flag_id=quality_assurance_flag_id)
                status.append({"success": "true", "result_id": result_id, "bottle_unique_name": bottle_unique_name})
        except BaseException as e:
            if isinstance(data, list) is False:
                e = "Expecting an array of results"
            status.append({"success": "false", "message": str(e), "bottle_unique_name": bottle_unique_name})
            # traceback.print_exc()
        return HttpResponse(json.dumps(status), content_type='application/json')


######
#
# Batch Upload Validations
#
######


def validate_bottle_bar_code(row):
    is_valid = False
    bottle_id = -1
    volume_filtered = None
    message = ""
    sample = {}

    try:
        bottle_name = row["bottle_unique_name"]
    except KeyError:
        message = "'bottle_unique_name' is required"
        return is_valid, message, bottle_id, sample, volume_filtered

    try:
        bottle_details = Bottle.objects.get(bottle_unique_name=bottle_name)
    except ObjectDoesNotExist:
        message = "The bottle '"+bottle_name+"' does not exist"
        return is_valid, message, bottle_id, sample, volume_filtered

    # get bottle id
    bottle_id = bottle_details.id

    # find the sample bottle id
    try:
        sample_bottle_details = SampleBottle.objects.get(bottle=bottle_id)
    except ObjectDoesNotExist:
        message = "The bottle "+bottle_name+" exists but was not found in the results table"
        return is_valid, message, bottle_id, sample, volume_filtered

    is_valid = True
    sample_bottle_id = sample_bottle_details.id
    volume_filtered = sample_bottle_details.volume_filtered

    return is_valid, message, bottle_id, sample_bottle_id, volume_filtered


def validate_constituent_type(row):
    is_valid = False
    constituent_id = -1
    message = ""
    try:
        constituent_type = row["constituent"]
    except KeyError:
        message = "'constituent' is required"
        return is_valid, message, constituent_id

    # get constituent id
    try:
        constituent_type_details = ConstituentType.objects.get(constituent=constituent_type)
    except ObjectDoesNotExist:
        message = "The constituent type '"+constituent_type+"' does not exist"
        return is_valid, message, constituent_id

    constituent_id = constituent_type_details.id
    is_valid = True
    return is_valid, message, constituent_id


def validate_analysis_type(row):
    is_valid = False
    analysis_id = -1
    message = ""
    try:
        analysis_type = row["analysis"]
    except KeyError:
        message = "'analysis' is required"
        return is_valid, message, analysis_id

    # get analysis id
    try:
        analysis_type_details = AnalysisType.objects.get(analysis=analysis_type)
    except ObjectDoesNotExist:
        message = "The analysis type '"+analysis_type+"' does not exist"
        return is_valid, message, analysis_id

    analysis_id = analysis_type_details.id
    is_valid = True
    return is_valid, message, analysis_id


def validate_isotope_flag(row):
    is_valid = False
    message = ""
    isotope_flag_id = -1

    # get isotope flag
    try:
        isotope_flag_id = row["isotope_flag_id"]
        # make sure that it is numeric
        if isinstance(isotope_flag_id, Number) is False:
            message = "Expecting a numeric value for isotope_flag_id"
            return is_valid, message, isotope_flag_id
    except KeyError:
        message = "'isotope_flag_id' is required"
        return is_valid, message, isotope_flag_id

    # get isotope flag id
    try:
        isotope_flag_details = IsotopeFlag.objects.get(id=isotope_flag_id)
    except ObjectDoesNotExist:
        message = "The isotope flag '"+str(isotope_flag_id)+"' does not exist"
        return is_valid, message, isotope_flag_id

    isotope_flag_id = isotope_flag_details.id
    is_valid = True
    return is_valid, message, isotope_flag_id


def validate_analysis_method(constituent_id, row):
    is_valid = False
    analysis_method_id = -1
    message = ""
    constituent_type = row["constituent"]
    try:
        method = row["method_id"]
    except KeyError:
        message = "'method_id' is required"
        return is_valid, message, analysis_method_id

    if isinstance(method, int) is False:
        message = "Expecting an int for method_id"
        return is_valid, message, analysis_method_id

    analysis_types = AnalysisConstituent.objects.filter(constituent_id=constituent_id).values_list('analysis_id',
                                                                                                   flat=True)
    try:
        analysis_type_details = AnalysisMethod.objects.filter(analysis_type__in=analysis_types,
                                                              method_type__exact=method)
        # analysis_type_details = AnalysisMethod.objects.get(analysis_type=str(analysis_type),method_type=str(method))
    except ObjectDoesNotExist:
        message = "The method code '"+str(method)+"' is not allowed for the constituent '"+constituent_type+"'"
        return is_valid, message, analysis_method_id

    if len(analysis_type_details) != 1:
        message = "More than one analysis type was found for method code '"+str(method)+"'"
        message += ", please contact the database administrator."
        return is_valid, message, analysis_method_id
    else:
        is_valid = True
        analysis_method_id = analysis_type_details[0].id
        return is_valid, message, analysis_method_id


def validate_quality_assurance_flag(row):
    is_valid = False
    message = ""
    quality_assurance_flag_id_array = []
    quality_assurance_flag_array = []
    try:
        quality_assurance_flag_array = row["quality_assurance_flag"]
        #  check if it's an array
        if isinstance(quality_assurance_flag_array, list) is False:
            message = "'quality_assurance_flag' needs to be a list of values"
            return is_valid, message, quality_assurance_flag_id_array
    except KeyError:
        is_valid = True

    # check that the given quality assurance flag exists
    for quality_assurance_flag in quality_assurance_flag_array:
        try:
            quality_assurance_flag_details = QualityAssuranceFlag.objects.get(
                quality_assurance_flag=quality_assurance_flag)
        except ObjectDoesNotExist:
            message = "The quality assurance flag '"+quality_assurance_flag+"' does not exist"
            return is_valid, message, quality_assurance_flag_id_array

        quality_assurance_flag_id = quality_assurance_flag_details.id
        quality_assurance_flag_id_array.append(quality_assurance_flag_id)

    is_valid = True
    return is_valid, message, quality_assurance_flag_id_array


def validate_analyzed_date(row):
    # get the date
    if row["analyzed_date"]:
        analyzed_date = row["analyzed_date"]
    else:
        analyzed_date = None

    if analyzed_date is None:
        is_valid = True
        return is_valid, ""
    else:
        try:
            analyzed_date = dt.strptime(analyzed_date, "%m/%d/%Y")
            is_valid = True
            return is_valid, ""
        except ValueError:
            is_valid = False
            message = "The analyzed_date '"+str(analyzed_date)+"' does not match the format mm/dd/YYYY. eg. 2/02/2014."
            return is_valid, message


def validate_result(sample_bottle_id, constituent_id, method_id, analysis_id, row):
    is_valid = False
    result_id = -1
    message = ""
    bottle_name = row["bottle_unique_name"]
    constituent_type = row["constituent"]
    analysis_type = row["analysis"]
    isotope_flag_id = row["isotope_flag_id"]

    # make sure that a result is given
    try:
        raw_value = row["raw_value"]
        # make sure that it is numeric
        if isinstance(raw_value, Number) is False:
            message = "Expecting a numeric value for result"
            return is_valid, message, result_id
    except KeyError:
        message = "'raw_value' is required"
        return is_valid, message, result_id

    # Find the matching record in the Results table, using the unique combination of barcode + constituent + analysis { + isotope}
    try:
        result_details = Result.objects.get(
            constituent=constituent_id, sample_bottle=sample_bottle_id, analysis=analysis_id,
            isotope_flag=isotope_flag_id)
    except ObjectDoesNotExist:
        message = "There is no matching record in the result table for bottle '"
        message += str(bottle_name)+"', constituent type '"+str(constituent_type)
        message += "', analysis type '" + str(analysis_type) + "', and isotope flag '" + str(isotope_flag_id)
        return is_valid, message, result_id
    except MultipleObjectsReturned:
        message = "There are more than one matching records in the result table for bottle '"
        message += str(bottle_name) + "', constituent type '" + str(constituent_type)
        message += "', analysis type '" + str(analysis_type) + "', and isotope flag '" + str(isotope_flag_id)
        return is_valid, message, result_id
    # check if final value already exists
    final_value = result_details.final_value
    if final_value is not None:
        # print(result_details.id)
        message = "This result row cannot be updated as a final value already exists"
        return is_valid, message, result_id

    # check if the method requires a bottle tare weight (77 (SPM)) and that the tare weight exists
    if method_id == 77 and Bottle.objects.filter(id=result_details.sample_bottle.bottle_id)[0].tare_weight is None:
        message = "A bottle tare weight is required for SPM calculations but was not found"
        return is_valid, message, result_id

    is_valid = True
    result_id = result_details.id
    return is_valid, message, result_id


######
#
# Batch Upload Calculations
#
######


def eval_result(row, result_id):
    qa_flags = []
    # check if it is an archived sample
    raw_value = row["raw_value"]
    try:
        daily_detection_limit = row["daily_detection_limit"]
    except KeyError:
        daily_detection_limit = None
    if raw_value == -888:
        display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = get_archived_sample_result()
    # check if lost sample
    elif raw_value == -999:
        display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = get_lost_sample_result(
            raw_value, daily_detection_limit
        )
    else:
        # get isotope flag
        result_details = Result.objects.get(id=result_id)
        isotope_flag = str(result_details.isotope_flag)
        try:
            analysis_date = dt.strptime(row["analyzed_date"], "%m/%d/%Y")
        except ValueError:
            analysis_date = None
        constituent_type = row["constituent"]
        method_code = row["method_id"]
        if (isotope_flag == 'NA' or isotope_flag == 'A') and (
            (constituent_type in ['FMHG', 'FTHG', 'UMHG', 'UTHG']) or
            ((constituent_type in ['PTHG', 'PMHG']) and (analysis_date >= dt.strptime("01/01/2003", "%m/%d/%Y"))) or
            ((constituent_type in ['SMHG', 'STHG']) and (analysis_date >= dt.strptime("01/01/2004", "%m/%d/%Y"))) and
            method_code != 165 or (constituent_type in ['BMHG'] and method_code in [108, 184])
        ):
            # evaluate according to MDL
            method_detection_limit, significant_figures, decimal_places = get_method_type(method_code)
            if raw_value < method_detection_limit:
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_mdl(
                    daily_detection_limit, method_detection_limit
                )
            else:
                # evaluate according to significant_figures & decimal_places
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_detection(
                    raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places
                )
        elif (isotope_flag in ['X-198', 'X-199', 'X-200', 'X-201', 'X-202']) or (
                (isotope_flag == 'NA' or isotope_flag == 'A') and (
                    (constituent_type in ['BMHG'] and method_code != 108) or
                    (constituent_type in ['BTHG']) or
                    (constituent_type in ['DMHG', 'DTHG', 'STHG', 'PMHG', 'PTHG', 'SMHG', 'SRHG'])
                )
        ):
            # set DDL to -999 for DTHG because it does not have a DDL
            if constituent_type == 'DTHG':
                daily_detection_limit = -999
            # set MDL to DDL
            method_detection_limit, significant_figures, decimal_places = get_method_type(method_code)
            method_detection_limit = daily_detection_limit
            if raw_value < method_detection_limit:
                # evaluate according to MDL
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_mdl(
                    daily_detection_limit, method_detection_limit
                )
            else:
                # all isotopes should use a decplaces of 3 despite what is in the
                if isotope_flag in ['X-198', 'X-199', 'X-200', 'X-201', 'X-202']:
                    decimal_places = 3
                # evaluate according to significant_figures & decimal_places
                display_value, reported_value, detection_flag, daily_detection_limit, qa_flags = eval_detection(
                    raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places
                )
        else:
            # if raw_value < 1:
            # display_value = '0'+ str(raw_value)
            # else:
            display_value = str(raw_value)
            detection_flag = 'NONE'
            reported_value = raw_value
    return display_value, reported_value, detection_flag, daily_detection_limit, qa_flags


# Archived Sample
# A value of -888 indicates an archived sample
# an archived sample is one for which no near-term analysis is expected
# in order to not leave a "hole", a value of -888 is used
# VALUE should remain -888
# REPORTED_VALUE and DISPLAY_VALUE should be -888
# DETECTION_FLAG should be 'A'
# DAILY_DETECTION_LIMIT should be set to -888
# No QA flag for the result
def get_archived_sample_result():
    qa_flags = []
    reported_value = -888
    display_value = str(-888)
    detection_flag = 'A'
    daily_detection_limit = -888
    return display_value, reported_value, detection_flag, daily_detection_limit, qa_flags


# Lost Sample
# A value of -999 indicates a lost sample
# VALUE should remain -999
# REPORTED_VALUE and DISPLAY_VALUE should be -999
# DETECTION_FLAG should be 'L'
# DAILY_DETECTION_LIMIT should be set to -999 if not otherwise provided
# Separately, a QA flag of LS should be added for the result
# but that should be accomplished by the batch load process, not this trigger
def get_lost_sample_result(raw_value, daily_detection_limit):
    if daily_detection_limit is None:
        daily_detection_limit = -999
    elif daily_detection_limit == -888:
        daily_detection_limit = -999
    reported_value = raw_value
    detection_flag = 'L'
    display_value = str(raw_value)
    qa_flags = []
    # qa = QualityAssuranceFlag.objects.get(quality_assurance_flag='LS')
    # qa_flag_id = qa.id
    # qa_flags.append(qa_flag_id)
    return display_value, reported_value, detection_flag, daily_detection_limit, qa_flags


def eval_mdl(daily_detection_limit, method_detection_limit):
    # if method_detection_limit < 1:
        # add leading zero
    #    display_value = '0'+ str(method_detection_limit)
    # else:
    display_value = str(method_detection_limit)
    reported_value = method_detection_limit
    detection_flag = '<'
    return display_value, reported_value, detection_flag, daily_detection_limit, []


# def eval_sigfigs_decimals(
#         raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places):
#     num_infront, num_behind, is_decimal_exists = get_decimal_info(raw_value)

#     if num_infront >= significant_figures+1:
#         sigfig_value = truncate_float(raw_value, significant_figures+1-num_infront)
#     elif num_behind == 0:
#         sigfig_value = raw_value
#     elif num_infront == 0:
#         sigfig_value = truncate_float(raw_value, decimal_places+1)
#     elif (num_infront+num_behind) == significant_figures+1:
#         sigfig_value = truncate_float(raw_value, num_behind)
#     elif (num_infront+num_behind) != significant_figures+1:
#         sigfig_value = truncate_float(
#             raw_value, (num_behind - ((num_infront + num_behind) - (significant_figures + 1))))
#     else:
#         sigfig_value = raw_value

#     #pad sigfig_value with zeroes
#     sigfig_value_str = pad_value(sigfig_value, significant_figures+1, decimal_places+1)
#     rounded_val = round_by_rule_of_five(sigfig_value, sigfig_value_str, significant_figures, decimal_places)
#     #if the daily_detection_limit is null, assign the MDL
#     if daily_detection_limit is None:
#         daily_detection_limit = method_detection_limit
#     #set the reported value to the value
#     reported_value = rounded_val
#     #determine the reported value and detection flag according to the DDL
#     #if the value is greater than the MDL and less than the DDL (MDL < VALUE < DDL),
#     #set the reported value to the value and the flag to E
#     if method_detection_limit <= rounded_val < daily_detection_limit:
#         detection_flag = 'E'
#     #if the value is greater than the MDL and greater than the DDL (MDL < VALUE > DDL),
#     #set the reported value to the value and the flag to NONE
#     elif method_detection_limit <= rounded_val >= daily_detection_limit:
#         detection_flag = 'NONE'
#     else:
#         detection_flag = 'NONE'
#     #Determine the display value by padding with trailing zeros if necessary
#     #Pad the reported_value with trailing zeros if length < sigfigs + 1 (and decimal point)
#     display_value_str = pad_value(reported_value, significant_figures, decimal_places)
#     #pad a leading zero if the value is less than 1
#     #if reported_value < 1 and reported_value > 0:
#     #    display_value_str = '0'+display_value_str
#     return display_value_str, reported_value, detection_flag, daily_detection_limit, []

def eval_sigfigs_decimals(
        value, significant_figures, decimal_places):
    num_infront, num_behind, is_decimal_exists = get_decimal_info(value)

    if num_infront >= significant_figures+1:
        sigfig_value = truncate_float(value, significant_figures+1-num_infront)
    elif num_behind == 0:
        sigfig_value = value
    elif num_infront == 0:
        sigfig_value = truncate_float(value, decimal_places+1)
    elif (num_infront+num_behind) == significant_figures+1:
        sigfig_value = truncate_float(value, num_behind)
    elif (num_infront+num_behind) != significant_figures+1:
        sigfig_value = truncate_float(
            value, (num_behind - ((num_infront + num_behind) - (significant_figures + 1))))
    else:
        sigfig_value = value

    # pad sigfig_value with zeroes
    sigfig_value_str = pad_value(sigfig_value, significant_figures+1, decimal_places+1)
    rounded_val = round_by_rule_of_five(sigfig_value, sigfig_value_str, significant_figures, decimal_places)

    # set the reported value to the value
    reported_value = rounded_val

    return reported_value


def eval_detection(
        raw_value, daily_detection_limit, method_detection_limit, significant_figures, decimal_places):

    # if the daily_detection_limit is null, assign the MDL
    if daily_detection_limit is None:
        daily_detection_limit = method_detection_limit
    # set the reported value to the value
    reported_value = raw_value
    # determine the reported value and detection flag according to the DDL
    # if the value is greater than the MDL and less than the DDL (MDL < VALUE < DDL),
    # set the reported value to the value and the flag to E
    if method_detection_limit <= raw_value < daily_detection_limit:
        detection_flag = 'E'
    # if the value is greater than the MDL and greater than the DDL (MDL < VALUE > DDL),
    # set the reported value to the value and the flag to NONE
    elif method_detection_limit <= raw_value >= daily_detection_limit:
        detection_flag = 'NONE'
    else:
        detection_flag = 'NONE'
    # Determine the display value by padding with trailing zeros if necessary
    # Pad the reported_value with trailing zeros if length < sigfigs + 1 (and decimal point)
    display_value_str = pad_value(reported_value, significant_figures, decimal_places)
    # pad a leading zero if the value is less than 1
    if 0 < reported_value < 1:
        display_value_str = '0'+display_value_str
 
    return display_value_str, reported_value, detection_flag, daily_detection_limit, []


def pad_value(value, significant_figures, decimal_places):
    num_infront, num_behind, is_decimal_exists = get_decimal_info(value)
    value_str = str(value)
    counter = len(value_str)
    # if decimal exists
    if num_behind > 0:
        if value >= 1:
            num_padding = significant_figures+1-counter
            if len(value_str) != significant_figures+1:
                value_str = add_padding(num_padding, value_str)
        else:
            num_padding = decimal_places+1-counter
            if len(value_str) != decimal_places+1:
                value_str = add_padding(num_padding, value_str)
    return value_str


def add_padding(num_padding, value_str):
    if num_padding > 0:
        for x in range(1, num_padding):
            value_str += "0"
    return value_str


def round_by_rule_of_five(sigfig_value, sigfig_value_str, significant_figures, decimal_places):
    if sigfig_value >= 1:
        rounded_val = get_rounded_value(sigfig_value, sigfig_value_str, significant_figures)
    else:
        rounded_val = get_rounded_value(sigfig_value, sigfig_value_str, decimal_places)
    return rounded_val


def get_rounded_value(sigfig_value, sigfig_value_str, value):
    num_infront, num_behind, is_decimal_exists = get_decimal_info(sigfig_value)
    is_last_digit_five, is_last_digit_zero = get_sigfig_info(sigfig_value_str)
    ndigits = num_behind-(num_infront+num_behind-value)
    # confirm that this is ok
    # if last digit is a (trailing) zero, do not do anything if no decimal place
    if is_last_digit_zero and is_decimal_exists:
        rounded_val = sigfig_value
    # if last digit is a (trailing) zero, round if there is a decimal place
    # Or if last digit is not a 5 and there isn't a decimal place, round,-1
    # Or if last digit is not a 5 and there is a decimal place, round,-1
    elif (
            (is_last_digit_zero and not is_decimal_exists) or
            (not is_last_digit_five and not is_decimal_exists) or
            (not is_last_digit_five and is_decimal_exists)
    ):
        rounded_val = round(sigfig_value, ndigits)
    # if last digit is a 5 round off or up based on 2nd last digit
    elif is_last_digit_five:
        digit_before_last = get_digit_before_last(sigfig_value_str, num_behind)
        # if last digit is a 5 and second to last digit is even, trunc
        if digit_before_last % 2 == 0:
            rounded_val = truncate_float(sigfig_value, ndigits)
        # if last digit is a 5 and second to last digit is odd, round
        else:
            rounded_val = math.ceil(sigfig_value*pow(10, ndigits))/pow(10, ndigits)
    else:
        rounded_val = sigfig_value
    return rounded_val


def get_digit_before_last(value_str, num_behind):
    length = len(value_str)
    if(num_behind > 0) and num_behind == 1:
        # if decimal exists and the decimal point is in the second to last position,
        # take the number just before the decimal point
        digit_before_last = value_str[length-3:length-2]
    else:
        # else take the second to last digit
        digit_before_last = value_str[length-2:length-1]
    return int(digit_before_last)


def get_sigfig_info(val):
    is_last_digit_five = False
    is_last_digit_zero = False
    val_str = str(val)
    length = len(val_str)
    last_digit = val_str[length-1:length]
    if last_digit == '5':
        is_last_digit_five = True
    elif last_digit == '0':
        is_last_digit_zero = True
    return is_last_digit_five, is_last_digit_zero


def get_decimal_info(val):
    str_val = str(val)
    val_arr = str_val.split(".")
    num_infront = len(val_arr[0])
    if len(val_arr) > 1:
        num_behind = len(val_arr[1])
        is_decimal_exists = True
    else:
        num_behind = 0
        is_decimal_exists = False
    if num_infront == 1 and val_arr[0] == '0':
        num_infront = 0

    return num_infront, num_behind, is_decimal_exists


def truncate_float(float_value, decimal_places):
    return round(int(float_value*pow(10, decimal_places))*pow(10, -decimal_places), decimal_places)


def get_method_type(method_code):
    method_type_details = MethodType.objects.get(id=str(method_code))
    significant_figures = method_type_details.significant_figures
    decimal_places = method_type_details.decimal_places
    if method_type_details.method_detection_limit is None or method_type_details.method_detection_limit == '':
        method_detection_limit = 0
    else:
        method_detection_limit = float(method_type_details.method_detection_limit)
    return method_detection_limit, significant_figures, decimal_places


def process_final_value(final_value, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed, result_id):
    value = final_value
    if method_id is None or final_value is None:
        value = final_value
    elif final_value == -999 or final_value == -888:
        value = final_value
    elif method_id in (86, 92, 103, 104):
        value = final_value * 100
    elif method_id == 42:
        value = final_value / 1000
    elif method_id in (48, 49, 83, 84, 85, 233, 211):
        if volume_filtered is None:
            return -900
        else:
            value = final_value * 1000 / volume_filtered
    elif method_id == 52 or method_id == 71:
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            if sample_mass_processed is not None and sample_mass_processed != -999:
                value = final_value / sediment_dry_weight / sample_mass_processed
    elif method_id in (73, 127, 157):
        if sample_mass_processed is not None and sample_mass_processed != -999:
            value = final_value / sample_mass_processed
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            value = final_value / sediment_dry_weight
    elif method_id == 228:
        if sample_mass_processed is not None and sample_mass_processed != -999:
            value = final_value / sample_mass_processed
    elif method_id == 77:
        if volume_filtered is None:
            return -900
        result = Result.objects.get(pk=result_id)
        tare_weight = Bottle.objects.filter(id=result.sample_bottle.bottle_id)[0].tare_weight
        value = (float(decimal.Decimal(str(final_value)) - tare_weight) * 1000) / (volume_filtered / 1000)
    return value


def process_report_value(report_value, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed, result_id):
    value = report_value
    if method_id is None or report_value is None:
        value = report_value
    elif report_value == -999 or report_value == -888:
        value = report_value
    elif method_id in (86, 92, 103, 104):
        value = round(report_value * 100, 2)
    elif method_id == 42:
        value = round(report_value / 1000, 4)
    elif method_id in (48, 49, 83, 84, 85, 233, 211):
        if volume_filtered is None:
            return -900
        else:
            value = round(report_value * 1000 / volume_filtered, 3)
    elif method_id == 52 or method_id == 71:
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            if sample_mass_processed is not None and sample_mass_processed != -999:
                value = round(report_value / sediment_dry_weight / sample_mass_processed, 2)
    elif method_id in (73, 127, 157, 228):
        if sample_mass_processed is not None and sample_mass_processed != -999:
            value = round(report_value / sample_mass_processed, 2)
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is not None and sediment_dry_weight != -999:
            value = round(report_value / sediment_dry_weight, 2)
    elif method_id == 77:
        if volume_filtered is None:
            return -900
        result = Result.objects.get(pk=result_id)
        tare_weight = Bottle.objects.filter(id=result.sample_bottle.bottle_id)[0].tare_weight
        value = round((float(decimal.Decimal(str(report_value)) - tare_weight) * 1000) / (volume_filtered / 1000), 4)
    return value


def process_daily_detection_limit(
        daily_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed):
    value = daily_detection_limit
    if method_id is None or daily_detection_limit is None or daily_detection_limit == 0:
        value = daily_detection_limit
    elif daily_detection_limit == -999:
        value = daily_detection_limit
    elif method_id == 42:
        value = daily_detection_limit / 1000
    elif method_id in (48, 49, 83, 84, 85, 233):
        if volume_filtered is None:
            return -900
        else:
            value = daily_detection_limit * 1000 / volume_filtered
    elif method_id == 71 or method_id == 211:
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            if sample_mass_processed is None or sample_mass_processed == -999:
                value = -999
            else:
                value = daily_detection_limit / sediment_dry_weight / sample_mass_processed
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            value = daily_detection_limit / sediment_dry_weight
    elif method_id in (73, 127, 157, 228):
        if sample_mass_processed is None or sample_mass_processed == -999:
            value = -999
        else:
            value = daily_detection_limit / sample_mass_processed
    return value


def process_method_daily_detection_limit(
        method_daily_detection_limit, method_id, volume_filtered, sediment_dry_weight, sample_mass_processed):
    value = method_daily_detection_limit
    if method_id is None or method_daily_detection_limit is None or method_daily_detection_limit == 0:
        value = method_daily_detection_limit
    elif method_daily_detection_limit == -999:
        value = -999
    elif method_id == 42:
        value = method_daily_detection_limit / 1000
    elif method_id in (48, 49, 83, 84, 85, 233, 211):
        if volume_filtered is None:
            return -900
        else:
            value = method_daily_detection_limit * 1000 / volume_filtered
    elif method_id == 52 or method_id == 71:
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            if sample_mass_processed is None or sample_mass_processed == -999:
                value = -999
            else:
                value = method_daily_detection_limit / sediment_dry_weight / sample_mass_processed
    elif method_id in (50, 74, 82):
        if sediment_dry_weight is None or sediment_dry_weight == -999:
            value = -999
        else:
            value = method_daily_detection_limit / sediment_dry_weight
    elif method_id in (73, 127, 157, 228):
        if sample_mass_processed is None or sample_mass_processed == -999:
            value = -999
        else:
            value = method_daily_detection_limit / sample_mass_processed
    if value is not None:
        value = round(value, 4)
    return value
