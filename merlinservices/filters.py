import datetime as dtmod
from datetime import datetime as dt
from django_filters.rest_framework import FilterSet, BaseInFilter, NumberFilter, CharFilter, BooleanFilter, MultipleChoiceFilter, DateFilter, DateTimeFilter
from merlinservices.models import *
from django.core.exceptions import MultipleObjectsReturned
from django.db.models.base import ObjectDoesNotExist


LIST_DELIMITER = ','


class CooperatorFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains', label='Filter by string contained in name, not case-sensitive')

    class Meta:
        model = Cooperator
        fields = ['name', ]


class ProjectFilter(FilterSet):
    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer project ID, exact')
    name = CharFilter(field_name='name', lookup_expr='icontains', label='Filter by string contained in name, not case-sensitive')

    class Meta:
        model = Project
        fields = ['id', 'name', ]


class SiteFilter(FilterSet):

    # filter by project name or ID
    def filter_project(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a project ID
            if value.isdigit():
                # get the sites related to this project ID, exact
                queryset = queryset.filter(projects__exact=value)
            # else query value is a project name
            else:
                # lookup the project ID that matches this project name, exact
                project_id = Project.objects.get(name__exact=value)
                # get the sites related to this project ID, exact
                queryset = queryset.filter(projects__exact=project_id)
        return queryset

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer site ID, exact')
    name_exact = CharFilter(field_name='name', lookup_expr='exact', label='Filter by string of name, exact')
    name = CharFilter(field_name='name', lookup_expr='icontains', label='Filter by string contained in name, not case-sensitive')
    usgs_scode = CharFilter(field_name='usgs_scode', lookup_expr='exact', label='Filter by string of usgs_scode, exact')
    project = CharFilter(method='filter_project', label='Filter by project ID or name (or list of IDs or names), exact')

    class Meta:
        model = Site
        fields = ['id', 'name_exact', 'name', 'usgs_scode', 'project', ]


class ProjectSiteFilter(FilterSet):

    # filter by project name or ID
    def filter_project(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a project ID
            if value.isdigit():
                # get the sites related to this project ID, exact
                queryset = queryset.filter(projects__exact=value)
            # else query value is a project name
            else:
                # lookup the project ID that matches this project name, exact
                project_id = Project.objects.get(name__exact=value)
                # get the sites related to this project ID, exact
                queryset = queryset.filter(projects__exact=project_id)
        return queryset

    # filter by site name or ID
    def filter_site(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a site ID
            if value.isdigit():
                # get the sites related to this site ID, exact
                queryset = queryset.filter(sites__exact=value)
            # else query value is a project name
            else:
                # lookup the project ID that matches this site name, exact
                site_id = Site.objects.get(name__exact=value)
                # get the sites related to this site ID, exact
                queryset = queryset.filter(sites__exact=site_id)
        return queryset

    project = CharFilter(method='filter_project', label='Filter by project ID or name (or list of IDs or names), exact')
    site = CharFilter(method='filter_site', label='Filter by site ID or name (or list of IDs or names), exact')

    class Meta:
        model = ProjectSite
        fields = ['project', 'site', ]


class SampleFilter(FilterSet):
    # Note that a unique field sample is determined by project+site+time_stamp+depth+replicate
    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer sample ID, exact')
    project = NumberFilter(field_name='project', lookup_expr='exact', label='Filter by integer project ID, exact')
    site = NumberFilter(field_name='site', lookup_expr='exact', label='Filter by integer site ID, exact')
    sample_date_time = DateTimeFilter(field_name='sample_date_time', lookup_expr='exact', label='Filter by sample datetime, exact', help_text='YYYY-MM-DD HH:MM:ss format (ss is optional, space may be a T)')
    depth = NumberFilter(field_name='depth', lookup_expr='exact', label='Filter by float depth, exact')
    replicate = NumberFilter(field_name='replicate', lookup_expr='exact', label='Filter by integer replicate, exact')
    medium_type = NumberFilter(field_name='medium_type', lookup_expr='exact', label='Filter by integer medium type ID, exact')

    class Meta:
        model = Sample
        fields = ['id', 'project', 'site', 'sample_date_time', 'depth', 'replicate', 'medium_type', ]


class SampleBottleFilter(FilterSet):

    # override base queryset to use select_related
    @property
    def qs(self):
        parent = super().qs
        return parent.select_related('sample')

    # filter by bottle unique name, exact list
    def filter_bottle_string(self, queryset, name, value):
        if value is not None and value != '':
            if isinstance(value, list):
                value = ','.join([str(x) for x in value if x is not None])
            if LIST_DELIMITER not in value:
                try:
                    # look up this bottle
                    this_sample_bottle = SampleBottle.objects.get(bottle__bottle_unique_name=value[0])
                    # if there is one match, the user just wants the details of this bottle, so add it to the query set
                    if this_sample_bottle:
                        queryset = queryset.filter(bottle__bottle_unique_name__in=value)
                except (ObjectDoesNotExist, MultipleObjectsReturned):
                    # if there are multiple matches, or if it doesn't exist, then the submitted bottle value
                    # is not a full/valid bottle name, but just a partial name, so the user wants
                    # a list of bottles whose name contains the value
                    queryset = queryset.filter(bottle__bottle_unique_name__icontains=value[0])
            else:
                queryset = queryset.filter(bottle__bottle_unique_name__in=value)
        return queryset

    # filter by sample datetime (after only, before only, or between both, depending on which URL params appear)
    def filter_start_end_date(self, queryset, name, value):
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

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer sample bottle ID, exact')
    sample_id = NumberFilter(field_name='sample_id', lookup_expr='exact', label='Filter by integer sample ID, exact')
    project = NumberFilter(field_name='project', lookup_expr='exact', label='Filter by integer project ID, exact')
    site = NumberFilter(field_name='site', lookup_expr='exact', label='Filter by integer site ID, exact')
    bottle = NumberFilter(field_name='bottle', lookup_expr='exact', label='Filter by integer bottle ID, exact')
    bottle_string = CharFilter(method='filter_bottle_string', label='Filter by string bottle unique name (or list of names), exact')
    constituent = NumberFilter(field_name='constituent', lookup_expr='exact', label='Filter by integer constituent ID, exact')
    date_after = DateFilter(method='filter_start_end_date', label='Filter by sample datetime (after this date)', help_text='YYYY-MM-DD format')
    date_before = DateFilter(method='filter_start_end_date', label='Filter by sample datetime before this date)', help_text='YYYY-MM-DD format')

    class Meta:
        model = SampleBottle
        fields = ['id', 'sample_id', 'project', 'site', 'bottle', 'bottle_string', 'constituent', 'date_after', 'date_before', ]


class SampleBottleBrominationFilter(FilterSet):

    # filter by bottle name or ID
    def filter_bottle(self, queryset, name, value):
        bottle_list = value.split(LIST_DELIMITER)
        # if query values are IDs
        if bottle_list[0].isdigit():
            # queryset = queryset.filter(sample_bottle__bottle__id__in=bottle_list)
            clauses = ' '.join(['WHEN bottle_id=%s THEN %s' % (pk, i) for i, pk in enumerate(bottle_list)])
            ordering = 'CASE %s END' % clauses
            queryset = queryset.filter(sample_bottle__bottle__id__in=bottle_list).extra(
                select={'ordering': ordering}, order_by=('ordering',))
        # else query values are names
        else:
            queryset = queryset.filter(sample_bottle__bottle__bottle_unique_name__in=bottle_list)
        return queryset

    # filter by created date (after only, before only, or between both, depending on which URL params appear)
    def filter_start_end_date(self, queryset, name, value):
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

    bottle = NumberFilter(method='filter_bottle', label='Filter by integer bottle ID or string name (or list of IDs or names), exact')
    date_after = DateFilter(method='filter_start_end_date', label='Filter by bromination datetime (after this date)', help_text='YYYY-MM-DD format')
    date_before = DateFilter(method='filter_start_end_date', label='Filter by bromination datetime before this date)', help_text='YYYY-MM-DD format')

    class Meta:
        model = SampleBottle
        fields = ['bottle', 'date_after', 'date_before', ]


class BottleFilter(FilterSet):

    # filter by bottle unique name, exact list
    def filter_bottle_string(self, queryset, name, value):
        if value is not None and value != '':
            if isinstance(value, list):
                value = ','.join([str(x) for x in value if x is not None])
            if value is not None:
                if LIST_DELIMITER in value:
                    bottle_list = value.split(',')
                    # maintain the order of the bottles that were queried
                    clauses = ' '.join(
                        ['WHEN bottle_unique_name=\'%s\' THEN %s' % (pk, i) for i, pk in enumerate(bottle_list)])
                    ordering = 'CASE %s END' % clauses
                    queryset = queryset.filter(bottle_unique_name__in=bottle_list).extra(
                        select={'ordering': ordering}, order_by=('ordering',))
                else:
                    queryset = queryset.filter(bottle_unique_name__icontains=value)
        return queryset

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer bottle ID, exact')
    bottle_unique_name = CharFilter(method='filter_bottle_string', label='Filter by string bottle unique name (or list of names), exact')
    unused = BooleanFilter(label='Filter by whether bottle has been used yet as a sample bottle')

    class Meta:
        model = SampleBottle
        fields = ['id', 'bottle_unique_name', 'unused', ]


class BottlePrefixFilter(FilterSet):

    # filter by bottle prefix name or ID
    def filter_bottle_prefix(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a bottle prefix ID
            if value.isdigit():
                # get the bottle prefix by ID, exact
                queryset = queryset.filter(id__exact=value)
            # if query value is a bottle prefix name
            else:
                # get the bottle prefix by name, case-insensitive contain
                queryset = queryset.filter(bottle_prefix__icontains=value)
        return queryset

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer bottle ID, exact')
    bottle_prefix_exact = CharFilter(field='bottle_prefix', lookup_expr='exact', label='Filter by string bottle prefix name (or list of names), exact')
    bottle_prefix = CharFilter(method='filter_bottle_prefix', label='Filter by bottle prefix ID or name (or list of IDs or names), exact for IDs and not case-sensitive for names')

    class Meta:
        model = SampleBottle
        fields = ['id', 'bottle_prefix_exact', 'bottle_prefix', ]
