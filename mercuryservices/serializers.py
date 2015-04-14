from rest_framework import serializers
from mercuryservices.models import *


######
##
## Project and Site
##
######


class ProjectSerializer(serializers.ModelSerializer):
    cooperator = serializers.RelatedField(source='cooperator')

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'accounting_code', 'cooperator', 'sites',)


class SimpleProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'accounting_code', 'cooperator',)


class CooperatorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cooperator
        fields = ('id', 'name', 'agency', 'email', 'phone', 'sec_phone', 'address', 'city', 'state', 'zipcode',
                  'country', 'projects',)


class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = ('id', 'name', 'usgs_sid', 'usgs_scode', 'description', 'latitude', 'longitude', 'datum',
                  'method', 'site_status', 'nwis_customer_code', 'projects',)


class SimpleSiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = ('id', 'name', 'usgs_sid', 'usgs_scode', 'description', 'latitude', 'longitude', 'datum',
                  'method', 'site_status', 'nwis_customer_code',)


######
##
## Field Sample
##
######


class BottleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BottleType
        fields = ('id', 'bottle_type', 'description',)


class BottlePrefixSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')
    bottle_type = serializers.RelatedField(source='bottle_type')

    class Meta:
        model = BottlePrefix
        fields = ('id', 'bottle_prefix', 'tare_weight', 'bottle_type', 'created_date', 'description',)


class BottleSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')
    bottle_prefix = serializers.RelatedField(source='bottle_prefix')

    class Meta:
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'bottle_prefix', 'created_date', 'description',)


class FullBottleSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')
    bottle_prefix = BottlePrefixSerializer(source='bottle_prefix')

    class Meta:
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'bottle_prefix', 'created_date', 'description',)


class SampleSerializer(serializers.ModelSerializer):
    #sample_date_time = serializers.DateTimeField(format='%Y-%m-%d %H%:M:%S', source='sample_date_time')
    sample_date = serializers.DateTimeField(format='%m/%d/%y', source='sample_date_time', read_only=True)
    sample_time = serializers.DateTimeField(format='%H%M', source='sample_date_time', read_only=True)
    received_date = serializers.DateTimeField(format='%m/%d/%y', source='received_date')
    project = SimpleProjectSerializer(source='project', read_only=True)
    site = SimpleSiteSerializer(source='site', read_only=True)
    medium_type = serializers.RelatedField(source='medium_type')
    lab_processing = serializers.RelatedField(source='lab_processing')
    sample_bottles = serializers.RelatedField(many=True, read_only=True)

    class Meta:
        model = Sample
        fields = ('id', 'sample_date_time', 'sample_date', 'sample_time', 'depth', 'length', 'comment', 'received_date',
                  'replicate', 'medium_type', 'lab_processing', 'sample_bottles', 'site', 'project',)


class SampleBottleSerializer(serializers.ModelSerializer):
    #sample = serializers.RelatedField(source='sample')
    bottle = serializers.RelatedField(source='bottle')

    class Meta:
        model = SampleBottle
        fields = ('id', 'sample', 'bottle', 'filter_type', 'volume_filtered',
                  'preservation_type', 'preservation_volume', 'preservation_acid', 'preservation_comment',)


class SampleBottleBrominationSerializer(serializers.ModelSerializer):
    sample_bottle = SampleBottleSerializer(source='sample_bottle')
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')

    class Meta:
        model = SampleBottleBromination
        fields = ('id', 'sample_bottle', 'bromination', 'bromination_event', 'bromination_volume', 'created_date',)


class FilterTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilterType
        fields = ('id', 'filter', 'description',)


class PreservationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreservationType
        fields = ('id', 'preservation', 'description',)


class ProcessingTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessingType
        fields = ('id', 'processing', 'description',)


class MediumTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediumType
        fields = ('id', 'nwis_code', 'medium', 'description', 'comment',)


######
##
## Constituent (Analyte)
##
######


class ConstituentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConstituentType
        fields = ('id', 'constituent', 'description',)


class ConstituentMediumSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConstituentMedium
        fields = ('id', 'constituent_type', 'medium_type',)


class ConstituentMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConstituentMethod
        fields = ('id', 'constituent_type', 'method_type',)


######
##
## Quality Assurance
##
######


class QualityAssuranceSerializer(serializers.ModelSerializer):
    quality_assurance = serializers.RelatedField(source='quality_assurance')

    class Meta:
        model = QualityAssurance
        fields = ('id', 'quality_assurance', 'result',)


class QualityAssuranceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = QualityAssuranceType
        fields = ('id', 'quality_assurance', 'description',)


class DetectionFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = DetectionFlag
        fields = ('id', 'detection_flag', 'description',)


class IsotopeFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = IsotopeFlag
        fields = ('id', 'isotope_flag', 'description',)

######
##
## Solution
##
######


class AcidSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')

    class Meta:
        model = Acid
        fields = ('id', 'code', 'concentration', 'created_date', 'comment',)


class BlankWaterSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')

    class Meta:
        model = BlankWater
        fields = ('id', 'lot_number', 'concentration', 'created_date', 'comment',)


class BrominationSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')

    class Meta:
        model = Bromination
        fields = ('id', 'concentration', 'created_date', 'comment',)


#######
##
## Personnel
##
######


# class RoleSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Role
#         fields = ('id', 'role', 'description', 'users',)


class UserSerializer(serializers.ModelSerializer):
    #initials = serializers.PrimaryKeyRelatedField(source='UserProfile')
    #phone = serializers.PrimaryKeyRelatedField(source='UserProfile')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_superuser', 'is_staff', 'is_active')#, 'initials', 'phone')


######
##
## Status
##
######


class StatusSerializer(serializers.ModelSerializer):
    date_time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='date_time_stamp')

    class Meta:
        model = Status
        fields = ('id', 'status_id', 'status_type', 'procedure_type', 'user', 'date_time_stamp', 'note',)


class ProcedureStatusTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcedureStatusType
        fields = ('id', 'procedure_type', 'status_type',)


class StatusTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusType
        fields = ('id', 'status_type',)


class ProcedureTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcedureType
        fields = ('id', 'procedure',)


######
##
## Special
##
######


class FullSampleBottleSerializer(serializers.ModelSerializer):
    sample = SampleSerializer(source='sample')
    bottle = FullBottleSerializer(source='bottle')
    filter_type = serializers.RelatedField(source='filter_type')
    preservation_type = serializers.RelatedField(source='preservation_type')
    preservation_acid = serializers.RelatedField(source='preservation_acid')

    class Meta:
        model = SampleBottle
        fields = ('id', 'bottle', 'filter_type', 'volume_filtered',
                  'preservation_type', 'preservation_volume', 'preservation_acid', 'preservation_comment',
                  'sample',)


    # sample = serializers.IntegerField(source='sample')
    # project = serializers.IntegerField(source='project')
    # site = serializers.IntegerField(source='site')
    # time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')
    # depth = serializers.FloatField(source='depth')
    # length = serializers.FloatField(source='length')
    # comment = serializers.CharField(source='comment')
    # received_time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='received_time_stamp')
    # replicate = serializers.IntegerField(source='replicate')
    # medium_type = serializers.IntegerField(source='medium_type')
    # lab_processing = serializers.IntegerField(source='lab_processing')
    # samplebottle = serializers.IntegerField(source='samplebottle')
    # bottle = serializers.IntegerField(source='bottle')
    # filter_type = serializers.IntegerField(source='filter_type')
    # volume_filtered = serializers.FloatField(source='volume_filtered')
    # preservation_type = serializers.IntegerField(source='preservation_type')
    # preservation_volume = serializers.FloatField(source='preservation_volume')
    # preservation_acid = serializers.IntegerField(source='preservation_acid')
    # preservation_comment = serializers.CharField(source='preservation_comment')


######
##
## Method and Result
##
######


class UnitTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnitType
        fields = ('id', 'unit', 'description',)


class MethodTypeSerializer(serializers.ModelSerializer):
    raw_value_unit = serializers.RelatedField(source='raw_value_unit')
    final_value_unit = serializers.RelatedField(source='final_value_unit')
    method_detection_limit_unit = serializers.RelatedField(source='method_detection_limit_unit')

    class Meta:
        model = MethodType
        fields = ('id', 'method_code', 'method', 'preparation', 'description', 'raw_method_detection_limit',
                  'final_method_detection_limit', 'raw_method_detection_limit_unit', 'final_method_detection_limit_unit',
                  'raw_value_unit', 'final_value_unit', 'decimal_places', 'significant_figures',
                  'standard_operating_procedure', 'nwis_parameter_code', 'nwis_parameter_name', 'nwis_method_code',)


class FlatResultSerializer(serializers.ModelSerializer):
    result_id = serializers.IntegerField(source='id', read_only=True)
    bottle = serializers.RelatedField(source='sample_bottle.bottle.bottle_unique_name')
    tare_weight = serializers.RelatedField(source='sample_bottle.bottle.bottle_prefix.tare_weight')
    project_name = serializers.RelatedField(source='sample_bottle.sample.project.name')
    site_name = serializers.RelatedField(source='sample_bottle.sample.site.name')
    sample_date = serializers.DateTimeField(format='%m/%d/%y', source='sample_bottle.sample.sample_date_time', read_only=True)
    sample_time = serializers.DateTimeField(format='%H%M', source='sample_bottle.sample.sample_date_time', read_only=True)
    depth = serializers.RelatedField(source='sample_bottle.sample.depth')
    constituent = serializers.RelatedField(source='constituent')
    isotope_flag = serializers.RelatedField(source='isotope_flag')
    received_date = serializers.RelatedField(source='sample_bottle.sample.received_date')
    comments = serializers.RelatedField(source='sample_bottle.sample.comment')
    unit = serializers.RelatedField(source='method.final_value_unit')
    detection_flag = serializers.RelatedField(source='detection_flag')
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', source='analyzed_date', read_only=True)

    class Meta:
        model = Result
        fields = ('result_id', 'bottle', 'tare_weight', 'project_name', 'site_name', 'sample_date', 'sample_time',
                  'depth', 'constituent', 'isotope_flag', 'received_date', 'comments', 'final_value', 'report_value',
                  'unit', 'detection_flag', 'analyzed_date',)


class FlatResultSampleSerializer(serializers.ModelSerializer):
    sample_id = serializers.IntegerField(source='sample_bottle.sample.id', read_only=True)
    project_name = serializers.RelatedField(source='sample_bottle.sample.project.name')
    site_name = serializers.RelatedField(source='sample_bottle.sample.site.name')
    site_id = serializers.RelatedField(source='sample_bottle.sample.site.usgs_scode')
    date = serializers.DateTimeField(format='%m/%d/%y', source='sample_bottle.sample.sample_date_time', read_only=True)
    time = serializers.DateTimeField(format='%H%M', source='sample_bottle.sample.sample_date_time', read_only=True)
    depth = serializers.RelatedField(source='sample_bottle.sample.depth')
    length = serializers.RelatedField(source='sample_bottle.sample.length')
    received = serializers.RelatedField(source='sample_bottle.sample.received_date')
    sample_comments = serializers.RelatedField(source='sample_bottle.sample.comment')
    container_id = serializers.RelatedField(source='sample_bottle.bottle.bottle_unique_name')
    lab_processing = serializers.RelatedField(source='sample_bottle.sample.lab_processing')
    medium = serializers.RelatedField(source='sample_bottle.sample.medium_type')
    analysis = serializers.RelatedField(source='constituent')
    isotope = serializers.RelatedField(source='isotope_flag')
    filter = serializers.RelatedField(source='sample_bottle.filter_type')
    filter_vol = serializers.RelatedField(source='sample_bottle.volume_filtered')
    preservation = serializers.RelatedField(source='sample_bottle.preservation_type')
    acid = serializers.RelatedField(source='sample_bottle.preservation_acid')
    acid_vol = serializers.RelatedField(source='sample_bottle.preservation_volume')
    pres_comments = serializers.RelatedField(source='sample_bottle.preservation_comment')

    class Meta:
        model = Result
        fields = ('sample_id', 'project_name', 'site_name', 'site_id', 'date', 'time', 'depth', 'length',
                  'received', 'sample_comments', 'container_id', 'lab_processing', 'medium', 'analysis', 'isotope',
                  'filter', 'filter_vol', 'preservation', 'acid', 'acid_vol', 'pres_comments')


class FullResultSerializer(serializers.ModelSerializer):
    entry_date = serializers.DateTimeField(format='%m/%d/%y', source='entry_date', read_only=True)
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', source='analyzed_date', read_only=True)
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date', read_only=True)
    sample_bottle = FullSampleBottleSerializer(source='sample_bottle')
    method = MethodTypeSerializer(source='method')
    constituent = serializers.RelatedField(source='constituent')
    isotope_flag = serializers.RelatedField(source='isotope_flag')
    detection_flag = serializers.RelatedField(source='detection_flag')

    class Meta:
        model = Result
        fields = ('id', 'constituent', 'isotope_flag', 'raw_value', 'final_value', 'report_value',
                  'detection_flag', 'raw_daily_detection_limit', 'final_daily_detection_limit',
                  'sediment_dry_weight', 'sample_mass_processed', 'entry_date', 'analyzed_date', 'created_date',
                  'analysis_comment', 'quality_assurances', 'method', 'sample_bottle',)


class ResultSerializer(serializers.ModelSerializer):
    entry_date = serializers.DateTimeField(format='%m/%d/%y', source='entry_date', read_only=True)
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', source='analyzed_date', read_only=True)
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date', read_only=True)
    sample_bottle = serializers.RelatedField(source='sample_bottle')
    constituent = serializers.RelatedField(source='constituent')
    isotope_flag = serializers.RelatedField(source='isotope_flag')

    class Meta:
        model = Result
        fields = ('id', 'method', 'constituent', 'isotope_flag', 'raw_value', 'final_value', 'report_value',
                  'detection_flag', 'raw_daily_detection_limit', 'final_daily_detection_limit',
                  'sediment_dry_weight', 'sample_mass_processed', 'entry_date', 'analyzed_date', 'created_date',
                  'analysis_comment', 'quality_assurances', 'sample_bottle',)


######
##
## Reports
##
######


class ReportResultsCountNawqaSerializer(serializers.Serializer):
    project_name = serializers.CharField()
    site_name = serializers.CharField()
    count = serializers.IntegerField()