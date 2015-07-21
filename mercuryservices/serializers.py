from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer
from mercuryservices.models import *


######
##
## Project and Site
##
######


class ProjectSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    cooperator_string = serializers.StringRelatedField(source='cooperator')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Project
        fields = ('id', 'name', 'description', 'accounting_code', 'cooperator', 'cooperator_string', 'sites',)


class SimpleProjectSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    # the only difference from the ProjectSerializer is that this one doesn't include related sites

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Project
        fields = ('id', 'name', 'description', 'accounting_code', 'cooperator', 'cooperator_string',)


class CooperatorSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Cooperator
        fields = ('id', 'name', 'agency', 'email', 'phone', 'sec_phone', 'address', 'city', 'state', 'zipcode',
                  'country',)


class SiteSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Site
        fields = ('id', 'name', 'usgs_sid', 'usgs_scode', 'description', 'latitude', 'longitude', 'datum',
                  'method', 'site_status', 'nwis_customer_code', 'projects',)


class SimpleSiteSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    # the only difference from the SiteSerializer is that this one doesn't include related projects

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Site
        fields = ('id', 'name', 'usgs_sid', 'usgs_scode', 'description', 'latitude', 'longitude', 'datum',
                  'method', 'site_status', 'nwis_customer_code',)


class ProjectSiteSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    project_string = serializers.StringRelatedField(source='project')
    site_string = serializers.StringRelatedField(source='site')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ProjectSite
        fields = ('id', 'project', 'project_string', 'site', 'site_string')


######
##
## Field Sample
##
######


class BottleTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = BottleType
        fields = ('id', 'bottle_type', 'description',)


class BottlePrefixSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])
    bottle_type_string = serializers.StringRelatedField(source='bottle_type')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = BottlePrefix
        fields = ('id', 'bottle_prefix', 'tare_weight', 'bottle_type', 'bottle_type_string',
                  'created_date', 'description',)


class BottleSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])
    bottle_prefix_string = serializers.StringRelatedField(source='bottle_prefix')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'bottle_prefix', 'bottle_prefix_string', 'created_date', 'description',)


class FullBottleSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    # the only difference from the BottleSerializer is that this one includes the entire related bottle prefixes,
    # not just the related bottle prefix id and name
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])
    bottle_prefix = BottlePrefixSerializer()

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'bottle_prefix', 'created_date', 'description',)


class SampleSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    sample_date_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    sample_date = serializers.DateTimeField(format='%m/%d/%y', source='sample_date_time', read_only=True)
    sample_time = serializers.DateTimeField(format='%H%M', source='sample_date_time', read_only=True)
    received_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])
    project_string = serializers.StringRelatedField(source='project')
    site_string = serializers.StringRelatedField(source='site')
    site_usgs_scode = serializers.StringRelatedField(source='site.usgs_scode')
    medium_type_string = serializers.StringRelatedField(source='medium_type')
    lab_processing_string = serializers.StringRelatedField(source='lab_processing')
    sample_bottles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Sample
        fields = ('id', 'sample_date_time', 'sample_date', 'sample_time', 'depth', 'length', 'comment', 'received_date',
                  'replicate', 'medium_type', 'medium_type_string', 'lab_processing', 'lab_processing_string',
                  'sample_bottles', 'project', 'project_string', 'site', 'site_string', 'site_usgs_scode')


class SampleBottleSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    bottle_string = serializers.StringRelatedField(source='bottle')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = SampleBottle
        fields = ('id', 'sample', 'bottle', 'bottle_string', 'filter_type', 'volume_filtered',
                  'preservation_type', 'preservation_volume', 'preservation_acid', 'preservation_comment',)


class SampleBottleBrominationSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    sample_bottle_unique_name = serializers.StringRelatedField(source='sample_bottle.bottle.bottle_unique_name')
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])

    class Meta:
        list_serializer_class = BulkListSerializer
        model = SampleBottleBromination
        fields = ('id', 'sample_bottle', 'sample_bottle_unique_name',
                  'bromination', 'bromination_event', 'bromination_volume', 'created_date',)


class FilterTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = FilterType
        fields = ('id', 'filter', 'description',)


class PreservationTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = PreservationType
        fields = ('id', 'preservation', 'description',)


class ProcessingTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ProcessingType
        fields = ('id', 'processing', 'description',)


class MediumTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = MediumType
        fields = ('id', 'nwis_code', 'medium', 'description', 'comment',)


######
##
## Constituent (Analyte)
##
######


class ConstituentTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ConstituentType
        fields = ('id', 'constituent', 'description',)


class ConstituentMediumSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ConstituentMedium
        fields = ('id', 'constituent_type', 'medium_type',)


class ConstituentMethodSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ConstituentMethod
        fields = ('id', 'constituent_type', 'method_type',)


######
##
## Quality Assurance
##
######


class QualityAssuranceSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    quality_assurance_string = serializers.StringRelatedField(source='quality_assurance')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = QualityAssurance
        fields = ('id', 'quality_assurance', 'quality_assurance_string', 'result',)


class QualityAssuranceTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = QualityAssuranceType
        fields = ('id', 'quality_assurance', 'description',)


class DetectionFlagSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = DetectionFlag
        fields = ('id', 'detection_flag', 'description',)


class IsotopeFlagSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = IsotopeFlag
        fields = ('id', 'isotope_flag', 'description',)

######
##
## Solution
##
######


class AcidSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Acid
        fields = ('id', 'code', 'concentration', 'created_date', 'comment',)


class BlankWaterSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])

    class Meta:
        list_serializer_class = BulkListSerializer
        model = BlankWater
        fields = ('id', 'lot_number', 'concentration', 'created_date', 'comment',)


class BrominationSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    created_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Bromination
        fields = ('id', 'concentration', 'created_date', 'comment',)


#######
##
## Personnel
##
######


class UserSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'groups', 'user_permissions', 'is_superuser', 'is_staff', 'is_active')


######
##
## Status
##
######


class StatusSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    date_time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Status
        fields = ('id', 'status_id', 'status_type', 'procedure_type', 'user', 'date_time_stamp', 'note',)


class ProcedureStatusTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ProcedureStatusType
        fields = ('id', 'procedure_type', 'status_type',)


class StatusTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = StatusType
        fields = ('id', 'status_type',)


class ProcedureTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = ProcedureType
        fields = ('id', 'procedure',)


######
##
## Special
##
######


class FullSampleBottleSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    # the only difference from the SampleSerializer is that this one includes the entire related samples and bottles,
    # not just the related ids and names

    sample = SampleSerializer()
    bottle = FullBottleSerializer()
    filter_type_string = serializers.StringRelatedField(source='filter_type')
    preservation_type_string = serializers.StringRelatedField(source='preservation_type')
    preservation_acid_string = serializers.StringRelatedField(source='preservation_acid')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = SampleBottle
        fields = ('id', 'bottle', 'filter_type', 'filter_type_string', 'volume_filtered', 'preservation_type',
                  'preservation_type_string', 'preservation_volume', 'preservation_acid', 'preservation_acid_string',
                  'preservation_comment', 'sample',)


######
##
## Method and Result
##
######


class UnitTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):

    class Meta:
        list_serializer_class = BulkListSerializer
        model = UnitType
        fields = ('id', 'unit', 'description',)


class MethodTypeSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    raw_value_unit_string = serializers.StringRelatedField(source='raw_value_unit')
    final_value_unit_string = serializers.StringRelatedField(source='final_value_unit')
    method_detection_limit_unit_string = serializers.StringRelatedField(source='method_detection_limit_unit')

    class Meta:
        list_serializer_class = BulkListSerializer
        model = MethodType
        fields = ('id', 'method_code', 'method', 'preparation', 'description',
                  'method_detection_limit', 'method_detection_limit_unit', 'method_detection_limit_unit_string',
                  'raw_value_unit', 'raw_value_unit_string', 'final_value_unit', 'final_value_unit_string',
                  'decimal_places', 'significant_figures', 'standard_operating_procedure',
                  'nwis_parameter_code', 'nwis_parameter_name', 'nwis_method_code',)


class FlatResultSerializer(serializers.ModelSerializer):
    # a flattened (not nested) version of the essential fields of the FullResultSerializer, to populate CSV files
    # requested from the Result Search
    result_id = serializers.IntegerField(source='id', read_only=True)
    bottle = serializers.StringRelatedField(source='sample_bottle.bottle.bottle_unique_name')
    tare_weight = serializers.FloatField(source='sample_bottle.bottle.bottle_prefix.tare_weight', read_only=True)
    project_name = serializers.StringRelatedField(source='sample_bottle.sample.project.name')
    site_name = serializers.StringRelatedField(source='sample_bottle.sample.site.name')
    sample_date = serializers.DateTimeField(format='%m/%d/%y',
                                            source='sample_bottle.sample.sample_date_time', read_only=True)
    sample_time = serializers.DateTimeField(format='%H%M',
                                            source='sample_bottle.sample.sample_date_time', read_only=True)
    depth = serializers.FloatField(source='sample_bottle.sample.depth', read_only=True)
    constituent = serializers.StringRelatedField()
    isotope_flag = serializers.StringRelatedField()
    received_date = serializers.StringRelatedField(source='sample_bottle.sample.received_date')
    comments = serializers.StringRelatedField(source='sample_bottle.sample.comment')
    unit = serializers.StringRelatedField(source='method.final_value_unit')
    detection_flag = serializers.StringRelatedField()
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', read_only=True)

    class Meta:
        model = Result
        fields = ('result_id', 'bottle', 'tare_weight', 'project_name', 'site_name', 'sample_date', 'sample_time',
                  'depth', 'constituent', 'isotope_flag', 'received_date', 'comments', 'final_value', 'report_value',
                  'unit', 'detection_flag', 'analyzed_date',)


class FlatResultSampleSerializer(serializers.ModelSerializer):
    # a flattened (not nested) version of the essential fields of the FullResultSerializer, to populate CSV files
    # requested from the Sample Search
    sample_id = serializers.IntegerField(source='sample_bottle.sample.id', read_only=True)
    project_name = serializers.StringRelatedField(source='sample_bottle.sample.project.name')
    project_id = serializers.StringRelatedField(source='sample_bottle.sample.project.id')
    site_name = serializers.StringRelatedField(source='sample_bottle.sample.site.name')
    site_id = serializers.StringRelatedField(source='sample_bottle.sample.site.usgs_scode')
    date = serializers.DateTimeField(format='%m/%d/%y', source='sample_bottle.sample.sample_date_time', read_only=True)
    time = serializers.DateTimeField(format='%H%M', source='sample_bottle.sample.sample_date_time', read_only=True)
    depth = serializers.FloatField(source='sample_bottle.sample.depth', read_only=True)
    length = serializers.FloatField(source='sample_bottle.sample.length', read_only=True)
    replicate = serializers.StringRelatedField(source='sample_bottle.sample.replicate')
    received = serializers.StringRelatedField(source='sample_bottle.sample.received_date')
    sample_comments = serializers.StringRelatedField(source='sample_bottle.sample.comment')
    container_id = serializers.StringRelatedField(source='sample_bottle.bottle.bottle_unique_name')
    lab_processing = serializers.StringRelatedField(source='sample_bottle.sample.lab_processing')
    medium = serializers.StringRelatedField(source='sample_bottle.sample.medium_type')
    analysis = serializers.StringRelatedField(source='constituent')
    isotope = serializers.StringRelatedField(source='isotope_flag')
    filter = serializers.StringRelatedField(source='sample_bottle.filter_type')
    filter_vol = serializers.FloatField(source='sample_bottle.volume_filtered', read_only=True)
    preservation = serializers.StringRelatedField(source='sample_bottle.preservation_type')
    acid = serializers.StringRelatedField(source='sample_bottle.preservation_acid')
    acid_vol = serializers.FloatField(source='sample_bottle.preservation_volume', read_only=True)
    pres_comments = serializers.StringRelatedField(source='sample_bottle.preservation_comment')
    sample_bottle_id = serializers.IntegerField(source='sample_bottle.id', read_only=True)
    result_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Result
        fields = ('sample_id', 'project_name', 'project_id', 'site_name', 'site_id', 'date', 'time', 'depth', 'length',
                  'replicate', 'sample_comments', 'received', 'lab_processing', 'container_id', 'medium', 'analysis',
                  'isotope', 'filter', 'filter_vol', 'preservation', 'acid', 'acid_vol', 'pres_comments',
                  'sample_bottle_id', 'result_id')


class FullResultSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    entry_date = serializers.DateField(format='%m/%d/%y', read_only=True)
    analyzed_date = serializers.DateField(format='%m/%d/%y', read_only=True)
    created_date = serializers.DateField(format='%m/%d/%y', read_only=True)
    sample_bottle = FullSampleBottleSerializer()
    method = MethodTypeSerializer()
    constituent_string = serializers.StringRelatedField(source='constituent')
    isotope_flag_string = serializers.StringRelatedField(source='isotope_flag')
    detection_flag_string = serializers.StringRelatedField(source='detection_flag')
    quality_assurances = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Result
        fields = ('id', 'constituent', 'constituent_string', 'isotope_flag', 'isotope_flag_string',
                  'raw_value', 'final_value', 'report_value', 'detection_flag', 'detection_flag_string',
                  'raw_daily_detection_limit', 'final_daily_detection_limit', 'final_method_detection_limit',
                  'sediment_dry_weight', 'sample_mass_processed', 'entry_date', 'analyzed_date', 'created_date',
                  'analysis_comment', 'quality_assurances', 'method', 'sample_bottle',)


class ResultSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    entry_date = serializers.DateTimeField(format='%m/%d/%y', read_only=True)
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', read_only=True)
    created_date = serializers.DateTimeField(format='%m/%d/%y', read_only=True)
    sample_bottle_unique_name = serializers.StringRelatedField(source='sample_bottle.bottle.bottle_unique_name')
    constituent_string = serializers.StringRelatedField(source='constituent')
    isotope_flag_string = serializers.StringRelatedField(source='isotope_flag')
    detection_flag_string = serializers.StringRelatedField(source='detection_flag')
    quality_assurances = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        list_serializer_class = BulkListSerializer
        model = Result
        fields = ('id', 'method', 'constituent', 'constituent_string', 'isotope_flag', 'isotope_flag_string',
                  'raw_value', 'final_value', 'report_value', 'detection_flag', 'detection_flag_string',
                  'raw_daily_detection_limit', 'final_daily_detection_limit', 'final_method_detection_limit',
                  'sediment_dry_weight', 'sample_mass_processed', 'entry_date', 'analyzed_date', 'created_date',
                  'analysis_comment', 'quality_assurances', 'sample_bottle', 'sample_bottle_unique_name',)


######
##
## Reports
##
######


class ReportResultsCountNawqaSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    site_name = serializers.CharField()
    count = serializers.IntegerField()


class ReportResultsCountProjectsSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    count = serializers.IntegerField()
    nwis_customer_code = serializers.CharField()
    #null = serializers.CharField()
    cooperator_email = serializers.EmailField()


class ReportSamplesNwisSerializer(serializers.Serializer):
    sample_integer = serializers.IntegerField()
    user_code = serializers.CharField()
    agency_cd = serializers.CharField()
    site_no = serializers.CharField()
    sample_start_date = serializers.CharField()
    sample_end_date = serializers.CharField()
    medium_cd = serializers.CharField()
    lab_id = serializers.CharField()
    project_cd = serializers.CharField()
    aqfr_cd = serializers.CharField()
    sample_type = serializers.CharField()
    anl_start_cd = serializers.CharField()
    anl_src_cd = serializers.CharField()
    hyd_cond_cd = serializers.CharField()
    hyd_event_cd = serializers.CharField()
    tissue_id = serializers.CharField()
    body_part_cd = serializers.CharField()
    lab_smp_comment = serializers.CharField()
    field_smp_comment = serializers.CharField()
    sample_tz_cd = serializers.CharField()
    tm_datum_rlblty_cd = serializers.CharField()
    coll_agency_cd = serializers.CharField()


class ReportResultsNwisSerializer(serializers.Serializer):
    sample_integer = serializers.IntegerField()
    parameter_cd = serializers.CharField()
    result_value = serializers.CharField()
    remark_cd = serializers.CharField()
    qa_cd = serializers.CharField()
    qw_method_cd = serializers.CharField()
    results_rd = serializers.CharField()
    val_qual_cd = serializers.CharField()
    rpt_lev_value = serializers.FloatField()
    rpt_lev_cd = serializers.CharField()
    dqi_cd = serializers.CharField()
    null_val_qual = serializers.CharField()
    prep_set_no = serializers.CharField()
    anl_set_no = serializers.CharField()
    anl_dt = serializers.CharField()
    prep_dt = serializers.CharField()
    lab_result_comment = serializers.CharField()
    field_result_comment = serializers.CharField()
    lab_std_dev = serializers.CharField()
    anl_ent = serializers.CharField()


class ReportResultsCooperatorSerializer(serializers.Serializer):
    site_name = serializers.CharField()
    usgs_scode = serializers.CharField()
    sample_date_time = serializers.DateTimeField(format='%m/%d/%y %H:%M:%S')
    medium = serializers.CharField()
    length = serializers.CharField()
    depth = serializers.CharField()
    analysis_date = serializers.DateField(format='%m/%d/%y', input_formats=['%Y-%m-%d'])
    result_id = serializers.IntegerField()
    bottle = serializers.CharField()
    constituent = serializers.CharField()
    final_ddl = serializers.CharField()
    detection_flag = serializers.CharField()
    final_value = serializers.CharField()
    unit = serializers.CharField()
    sample_id = serializers.IntegerField()
    analysis_comment = serializers.CharField()
    sample_comment = serializers.CharField()
    qaflags = serializers.CharField()