import datetime as dtmod
from datetime import datetime as dt
from django_filters.rest_framework import FilterSet, BaseInFilter, NumberFilter, CharFilter, BooleanFilter, DateFilter, DateTimeFilter
from merlinservices.models import *
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count
from django.db.models.base import ObjectDoesNotExist


LIST_DELIMITER = ','


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CharInFilter(BaseInFilter, CharFilter):
    pass


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
    project = CharFilter(method='filter_project', label='Filter by project ID or name, exact')

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
                # lookup the projects-sites whose related projects contain this project name, case-insensitive
                queryset = queryset.filter(project__name__icontains=value)
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
                # lookup the projects-sites whose related sites contain this site name, case-insensitive
                queryset = queryset.filter(site__name__icontains=value)
        return queryset

    project = CharFilter(method='filter_project', label='Filter by integer project ID, exact, or string name, not case-sensitive')
    site = CharFilter(method='filter_site', label='Filter by integer site ID, exact, or string name, not case-sensitive')

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
    sample_id = NumberFilter(field_name='sample__id', lookup_expr='exact', label='Filter by integer sample ID, exact')
    project = NumberInFilter(field_name='sample__project', lookup_expr='in', label='Filter by integer project ID (or list of IDs), exact')
    site = NumberInFilter(field_name='sample__site', lookup_expr='in', label='Filter by integer site ID (or list of IDs), exact')
    bottle = NumberFilter(field_name='bottle', lookup_expr='exact', label='Filter by integer bottle ID, exact')
    bottle_string = CharFilter(method='filter_bottle_string', label='Filter by string bottle unique name (or list of names), exact')
    constituent = NumberInFilter(field_name='results__constituent_id', lookup_expr='in', label='Filter by integer constituent ID (or list of IDs), exact')
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

    bottle = CharFilter(method='filter_bottle', label='Filter by EITHER integer bottle ID (or list of IDs) OR string name (or list of names), but not a mix of IDs and names, exact')
    date_after = DateFilter(method='filter_start_end_date', label='Filter by bromination date (after this date)', help_text='YYYY-MM-DD format')
    date_before = DateFilter(method='filter_start_end_date', label='Filter by bromination date (before this date)', help_text='YYYY-MM-DD format')

    class Meta:
        model = SampleBottleBromination
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
    bottle_unique_name = CharFilter(method='filter_bottle_string', label='Filter by string bottle unique name, not case-sensitive, or list of names, exact')
    unused = BooleanFilter(field='sample_bottles', label='Filter by whether bottle has been used yet as a sample bottle')

    class Meta:
        model = Bottle
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
    bottle_prefix_exact = CharFilter(field='bottle_prefix', lookup_expr='exact', label='Filter by string bottle prefix name, exact')
    bottle_prefix = CharFilter(method='filter_bottle_prefix', label='Filter by bottle prefix ID or name, exact for ID and not case-sensitive for name')

    class Meta:
        model = BottlePrefix
        fields = ['id', 'bottle_prefix_exact', 'bottle_prefix', ]


class BottleTypeFilter(FilterSet):

    bottle_type_string = CharFilter(field='bottle_type_string', lookup_expr='exact', label='Filter by string bottle type, exact')

    class Meta:
        model = BottleType
        fields = ['bottle_type_string', ]


class MethodTypeFilter(FilterSet):

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer bottle ID, exact')
    analysis = NumberFilter(field_name='analyses', lookup_expr='exact', label='Filter by integer analysis ID, exact')
    constituent = CharFilter(field_name='analyses__constituents', label='Filter by integer constituent ID, exact')

    class Meta:
        model = MethodType
        fields = ['id', 'analysis', 'constituent', ]


class ResultFilter(FilterSet):

    sample_bottle = NumberFilter(field_name='sample_bottle', lookup_expr='exact', label='Filter by integer sample_bottle ID, exact')
    constituent = NumberFilter(field_name='constituent', lookup_expr='exact', label='Filter by integer constituent ID, exact')
    isotope_flag = NumberFilter(field_name='isotope_flag', label='Filter by integer isotope_flag ID, exact')

    class Meta:
        model = Result
        fields = ['sample_bottle', 'constituent', 'isotope_flag', ]


class FullResultFilter(FilterSet):

    @property
    def qs(self):
        parent = super().qs
        # prefetch_related only the exact, necessary fields to greatly improve the response time of the query
        queryset = parent.prefetch_related(
            'sample_bottle', 'sample_bottle__bottle', 'sample_bottle__bottle__bottle_prefix', 'sample_bottle__sample',
            'sample_bottle__sample__site', 'sample_bottle__sample__project', 'constituent', 'isotope_flag',
            'detection_flag', 'method'
        )
        return queryset

    # filter by bottle prefix name or ID
    def filter_bottle(self, queryset, name, value):
        if value is not None and value != '':
            bottle_list = value.split(',')
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
            # if exclude_null_results is a param, then exclude null results, otherwise return all results
            exclude_null_results = self.request.query_params.get('exclude_null_results')
            if exclude_null_results is not None:
                if exclude_null_results == 'True' or exclude_null_results == 'true':
                    queryset = queryset.filter(final_value__isnull=False)
                # elif exclude_null_results == 'False' or exclude_null_results == 'false':
                #    queryset = queryset.filter(final_value__isnull=True)
        return queryset

    # filter by sample date (after only, before only, or between both, depending on which URL params appear)
    # remember that sample date is actually a date time object, so convert it to date before doing date math
    def filter_sample_start_end_date(self, queryset, name, value):
        date_after_sample = self.request.query_params.get('date_after_sample', None)
        date_before_sample = self.request.query_params.get('date_before_sample', None)
        # filtering datetime fields using only date is problematic
        # (see warning at https://docs.djangoproject.com/en/dev/ref/models/querysets/#range)
        # to properly do the date math on datetime fields,
        # set date_after to 23:59 of the current date and date_before to 00:00 of the same day
        if date_after_sample is not None:
            date_after_sample_plus = dt.combine(dt.strptime(date_after_sample, '%Y-%m-%d').date(), dtmod.time.max)
        if date_before_sample is not None:
            date_before_sample_minus = dt.combine(
                dt.strptime(date_before_sample, '%Y-%m-%d').date(), dtmod.time.min)
        if date_after_sample is not None and date_before_sample is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(sample_bottle__sample__sample_date_time__range=(
            #    date_after_sample_plus, date_before_sample_minus))
            # the filter below is date-exclusive
            queryset = queryset.filter(sample_bottle__sample__sample_date_time__gt=date_after_sample_plus,
                                       sample_bottle__sample__sample_date_time__lt=date_before_sample_minus)
        elif date_after_sample is not None:
            queryset = queryset.filter(sample_bottle__sample__sample_date_time__gt=date_after_sample_plus)
        elif date_before_sample is not None:
            queryset = queryset.filter(sample_bottle__sample__sample_date_time__lt=date_before_sample_minus)
        return queryset

    # filter by created date (after only, before only, or between both, depending on which URL params appear)
    def filter_entry_start_end_date(self, queryset, name, value):
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_after_entry is not None and date_before_entry is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(created_date__range=(date_after, date_before))
            # the filter below is date-exclusive
            queryset = queryset.filter(created_date__gt=date_after_entry, created_date__lt=date_before_entry)
        elif date_after_entry is not None:
            queryset = queryset.filter(created_date__gt=date_after_entry)
        elif date_before_entry is not None:
            queryset = queryset.filter(created_date__lt=date_before_entry)
        return queryset

    bottle = NumberFilter(method='filter_bottle', label='Filter by integer bottle ID (or list of IDs), exact')
    analysis = NumberInFilter(field_name='analysis', lookup_expr='in', label='Filter by integer analysis ID (or list of IDs), exact')
    constituent = NumberInFilter(field_name='constituent', lookup_expr='in', label='Filter by integer constituent ID (or list of IDs), exact')
    isotope_flag = NumberFilter(field_name='isotope_flag', label='Filter by integer isotope_flag ID, exact')
    project = NumberInFilter(field_name='sample_bottle__sample__project', lookup_expr='in', label='Filter by integer project ID (or list of IDs), exact')
    site = NumberInFilter(field_name='sample_bottle__sample__site', lookup_expr='in', label='Filter by integer site ID (or list of IDs), exact')
    depth = NumberFilter(field_name='sample_bottle__sample__depth', label='Filter by float depth, exact')
    replicate = NumberFilter(field_name='sample_bottle__sample__replicate', label='Filter by integer replicate, exact')
    date_after_sample = DateFilter(method='filter_sample_start_end_date', label='Filter by sample date after this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_sample = DateFilter(method='filter_sample_start_end_date', label='Filter by sample date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_after_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    exclude_null_results = BooleanFilter(field_name='final_value', label='Exclude null results (otherwise include all results)')

    class Meta:
        model = Result
        fields = ['bottle', 'analysis', 'constituent', 'isotope_flag', 'project', 'site', 'depth', 'replicate',
                  'date_after_sample', 'date_before_sample', 'date_after_entry', 'date_before_entry',
                  'exclude_null_results', ]


class AnalysisTypeFilter(FilterSet):

    # filter by method name or ID
    def filter_method(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a method ID
            if value.isdigit():
                # get the analyses related to this method ID, exact
                queryset = queryset.filter(methods__exact=value)
            # else query value is a method name
            else:
                # lookup the method ID that matches this method name, exact
                method_id = MethodType.objects.get(methods__exact=value)
                # get the analyses related to this method ID, exact
                queryset = queryset.filter(methods__exact=method_id)
        return queryset

    # filter by medium name or ID
    def filter_medium(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a medium ID
            if value.isdigit():
                # get the analyses related to this medium ID, exact
                queryset = queryset.filter(mediums__exact=value)
            # else query value is a medium name
            else:
                # lookup the medium ID that matches this medium name, exact
                medium_id = MediumType.objects.get(mediums__exact=value)
                # get the analyses related to this medium ID, exact
                queryset = queryset.filter(mediums__exact=medium_id)
        return queryset

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer analysis ID, exact')
    analysis = CharFilter(field_name='analyses', lookup_expr='icontains', label='Filter by string contained in analysis name, not case-sensitive')
    method = CharFilter(method='filter_method', label='Filter by integer method ID or string name, exact')
    medium = CharFilter(method='filter_medium', label='Filter by integer medium ID or string name, exact')
    nwis_code = CharFilter(field_name='mediums__nwis_code', label='Filter by integer NWIS Code ID, exact')

    class Meta:
        model = AnalysisType
        fields = ['id', 'analysis', 'method', 'medium', 'nwis_code', ]


class ConstituentTypeFilter(FilterSet):

    # filter by analysis name or ID
    def filter_analysis(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a analysis ID
            if value.isdigit():
                # get the constituents related to this analysis ID, exact
                queryset = queryset.filter(analyses__exact=value)
            # else query value is a analysis name
            else:
                # lookup the analysis ID that matches this analysis name, exact
                method_id = AnalysisType.objects.get(analysis__exact=value)
                # get the constituents related to this analysis ID, exact
                queryset = queryset.filter(analyses__exact=method_id)
        return queryset

    # filter by method name or ID
    def filter_method(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a method ID
            if value.isdigit():
                # get the constituents related to this method ID, exact
                queryset = queryset.filter(analyses__methods__exact=value)
            # else query value is a method name
            else:
                # lookup the method ID that matches this method name, exact
                method_id = MethodType.objects.get(analyses__methods__exact=value)
                # get the constituents related to this method ID, exact
                queryset = queryset.filter(analyses__methods__exact=method_id)
        return queryset

    # filter by medium name or ID
    def filter_medium(self, queryset, name, value):
        if value is not None and value != '':
            # if query value is a medium ID
            if value.isdigit():
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(analyses__mediums__exact=value)
            # else query value is a medium name
            else:
                # lookup the medium ID that matches this medium name, exact
                medium_id = MediumType.objects.get(analyses__mediums__exact=value)
                # get the constituents related to this medium ID, exact
                queryset = queryset.filter(analyses__mediums__exact=medium_id)
        return queryset

    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer constituent ID, exact')
    constituent = CharFilter(field_name='constituent', lookup_expr='icontains', label='Filter by string contained in constituent name, not case-sensitive')
    analysis = CharFilter(method='filter_analysis', label='Filter by integer analysis ID or string name exact')
    method = CharFilter(method='filter_method', label='Filter by integer method ID or string name, exact')
    medium = CharFilter(method='filter_medium', label='Filter by integer medium ID or string name, exact')
    nwis_code = CharFilter(field_name='mediums__nwis_code', label='Filter by integer NWIS Code ID, exact')

    class Meta:
        model = ConstituentType
        fields = ['id', 'constituent', 'analysis', 'method', 'medium', 'nwis_code', ]


class IsotopeFlagFilter(FilterSet):
    # TODO: this is changed from the old filtering, make sure to test this
    id = NumberFilter(field_name='id', lookup_expr='exact', label='Filter by integer isotope flag ID, exact')
    isotope_flag = CharFilter(field_name='isotope_flag', lookup_expr='icontains', label='Filter by string contained in isotope flag, not case-sensitive')

    class Meta:
        model = IsotopeFlag
        fields = ['id', 'isotope_flag', ]


class EquipmentFilter(FilterSet):
    type = NumberFilter(field_name='type', lookup_expr='exact', label='Filter by integer type ID, exact')
    serial_number = CharFilter(field_name='serial_number', lookup_expr='icontains', label='Filter by string contained in serial_number, not case-sensitive')

    class Meta:
        model = Equipment
        fields = ['type', 'serial_number', ]


class AcidFilter(FilterSet):
    code_exact = CharFilter(field_name='code', lookup_expr='exact', label='Filter by string acid code, exact')
    code = CharFilter(field_name='code', lookup_expr='icontains', label='Filter by string contained in acid code, not case-sensitive')

    class Meta:
        model = Acid
        fields = ['code', 'code_exact', ]


class BlankWaterFilter(FilterSet):
    lot_number = CharFilter(field_name='lot_number', lookup_expr='icontains', label='Filter by string contained in lot number, not case-sensitive')

    class Meta:
        model = BlankWater
        fields = ['lot_number', ]


class BrominationFilter(FilterSet):
    id = CharFilter(field_name='id', lookup_expr='icontains', label='Filter by string contained in bromination ID, not case-sensitive')
    date = DateTimeFilter(field_name='created_date', lookup_expr='icontains', label='Filter by string contained in created date, not case-sensitive', help_text='YYYY-MM-DD format')

    class Meta:
        model = Bromination
        fields = ['id', 'date', ]


class UserFilter(FilterSet):

    @property
    def qs(self):
        parent = super().qs
        queryset = parent.order_by('-last_login')
        return queryset

    username = CharFilter(field_name='username', lookup_expr='exact', label='Filter by string username, exact')

    class Meta:
        model = User
        fields = ['username', ]


class ReportResultsCountNawqaFilter(FilterSet):

    # @property
    # def qs(self):
    #     parent = super().qs
    #     # create a new column for counts that doesn't appear in the database view, using the Django annotate() method,
    #     # which will count the number of records after the date filter has been applied, rather than before,
    #     # (which is what would happen if we had a count column in the database view)
    #     queryset = parent.values('project_name', 'site_name').annotate(count=Count('project_name'))
    #     return queryset

    # filter by entry date (after only, before only, or between both, depending on which URL params appear)
    def filter_entry_start_end_date(self, queryset, name, value):
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_after_entry is not None and date_before_entry is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(entry_date__range=(date_after_entry, date_before_entry))
            # the filter below is date-exclusive
            queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
        elif date_after_entry is not None:
            queryset = queryset.filter(entry_date__gt=date_after_entry)
        elif date_before_entry is not None:
            queryset = queryset.filter(entry_date__lt=date_before_entry)
        # create a new column for counts that doesn't appear in the database view, using the Django annotate() method,
        # which will count the number of records after the date filter has been applied, rather than before,
        # (which is what would happen if we had a count column in the database view)
        queryset = queryset.values('project_name', 'site_name').annotate(count=Count('project_name'))
        return queryset

    date_after_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')

    class Meta:
        model = ResultCountNawqa
        fields = ['date_after_entry', 'date_before_entry', ]


class ReportResultsCountProjectsFilter(FilterSet):

    # filter by entry date (after only, before only, or between both, depending on which URL params appear)
    def filter_entry_start_end_date(self, queryset, name, value):
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_after_entry is not None and date_before_entry is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(entry_date__range=(date_after_entry, date_before_entry))
            # the filter below is date-exclusive
            queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
        elif date_after_entry is not None:
            queryset = queryset.filter(entry_date__gt=date_after_entry)
        elif date_before_entry is not None:
            queryset = queryset.filter(entry_date__lt=date_before_entry)
        # create a new column for counts that doesn't appear in the database view, using the Django annotate() method,
        # which will count the number of records after the date filter has been applied, rather than before,
        # (which is what would happen if we had a count column in the database view)
        queryset = queryset.values(
            'project_name', 'nwis_customer_code', 'cooperator_email').annotate(count=Count('project_name'))
        return queryset

    date_after_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')

    class Meta:
        model = ResultCountProjects
        fields = ['date_after_entry', 'date_before_entry', ]


class ReportSamplesNwisFilter(FilterSet):

    # filter by entry date (after only, before only, or between both, depending on which URL params appear)
    def filter_entry_start_end_date(self, queryset, name, value):
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_after_entry is not None and date_before_entry is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(entry_date__range=(date_after_entry, date_before_entry))
            # the filter below is date-exclusive
            queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
        elif date_after_entry is not None:
            queryset = queryset.filter(entry_date__gt=date_after_entry)
        elif date_before_entry is not None:
            queryset = queryset.filter(entry_date__lt=date_before_entry)
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

    project = CharInFilter(field_name='project_name', lookup_expr='in', label='Filter by string project name (or list of names), exact')
    project_not = CharInFilter(field_name='project_name', lookup_expr='in', exclude=True, label='Filter by string project name to exclude (or list of names to exclude), exact')
    date_after_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')

    class Meta:
        model = SampleNwis
        fields = ['project', 'project_not', 'date_after_entry', 'date_before_entry', ]


class ReportResultsNwisFilter(FilterSet):

    # filter by exclude of length and depth parameters
    def filter_exclude_ld(self, queryset, name, value):
        if value is not None and value != '':
            if value.lower() == 'true':
                # parameter_cd for length is '00024' and depth is '00098'
                queryset = queryset.exclude(parameter_cd__exact='00024').exclude(parameter_cd__exact='00098')
            return queryset

    # filter by entry date (after only, before only, or between both, depending on which URL params appear)
    def filter_entry_start_end_date(self, queryset, name, value):
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_after_entry is not None and date_before_entry is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(entry_date__range=(date_after_entry, date_before_entry))
            # the filter below is date-exclusive
            queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
        elif date_after_entry is not None:
            queryset = queryset.filter(entry_date__gt=date_after_entry)
        elif date_before_entry is not None:
            queryset = queryset.filter(entry_date__lt=date_before_entry)
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

    exclude_ld = CharFilter(method='filter_exclude_ld', label='Filter by excluding length and depth parameters (otherwise include all parameters)')
    project = CharInFilter(field_name='project_name', lookup_expr='in', label='Filter by string project name (or list of names), exact')
    project_not = CharInFilter(field_name='project_name', lookup_expr='in', exclude=True, label='Filter by string project name to exclude (or list of names to exclude), exact')
    date_after_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')

    class Meta:
        model = ResultNwis
        fields = ['project', 'project_not', 'date_after_entry', 'date_before_entry', ]


class ReportResultsCooperatorFilter(FilterSet):

    # filter by entry date (after only, before only, or between both, depending on which URL params appear)
    def filter_entry_start_end_date(self, queryset, name, value):
        date_after_entry = self.request.query_params.get('date_after_entry', None)
        date_before_entry = self.request.query_params.get('date_before_entry', None)
        if date_after_entry is not None and date_before_entry is not None:
            # the filter below using __range is date-inclusive
            # queryset = queryset.filter(entry_date__range=(date_after_entry, date_before_entry))
            # the filter below is date-exclusive
            queryset = queryset.filter(entry_date__gt=date_after_entry, entry_date__lt=date_before_entry)
        elif date_after_entry is not None:
            queryset = queryset.filter(entry_date__gt=date_after_entry)
        elif date_before_entry is not None:
            queryset = queryset.filter(entry_date__lt=date_before_entry)
        return queryset

    cooperator = NumberInFilter(field_name='cooperator_name__in', lookup_expr='in', label='Filter by string cooperator name (or list of names), exact')
    project = CharInFilter(field_name='project_name', lookup_expr='in', label='Filter by string project name (or list of names), exact')
    project_not = CharInFilter(field_name='project_name', lookup_expr='in', exclude=True, label='Filter by string project name to exclude (or list of names to exclude), exact')
    date_after_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')
    date_before_entry = DateFilter(method='filter_entry_start_end_date', label='Filter by entry date before this date, exclusive)', help_text='YYYY-MM-DD format')

    class Meta:
        model = ResultCooperator
        fields = ['cooperator', 'project', 'project_not', 'date_after_entry', 'date_before_entry', ]
