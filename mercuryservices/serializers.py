from rest_framework import serializers
from mercuryservices.models import *


######
##
## Project and Site
##
######


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'accounting_code', 'cooperator', 'sites',)


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


######
##
## Field Sample
##
######


class BottleSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%m/%d/%y', source='created_date')
    bottle_type = serializers.RelatedField(source='bottle_type')

    class Meta:
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'created_date', 'tare_weight', 'bottle_type', 'description',)


class BottleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BottleType
        fields = ('id', 'bottle_type', 'description',)


class SampleSerializer(serializers.ModelSerializer):
    sample_date = serializers.DateTimeField(format='%m/%d/%y', source='sample_date_time')
    sample_time = serializers.DateTimeField(format='%H%M', source='sample_date_time')
    received_date = serializers.DateTimeField(format='%m/%d/%y', source='received_date')
    project = ProjectSerializer(source='project')
    site = SiteSerializer(source='site')
    medium_type = serializers.RelatedField(source='medium_type')
    lab_processing = serializers.RelatedField(source='lab_processing')

    class Meta:
        model = Sample
        fields = ('id', 'project', 'site', 'sample_date', 'sample_time', 'depth', 'length', 'comment', 'received_date',
                  'replicate', 'medium_type', 'lab_processing', 'sample_bottles')


class SampleBottleSerializer(serializers.ModelSerializer):
    sample = serializers.RelatedField(source='sample')
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
    bottle = BottleSerializer(source='bottle')
    filter_type = serializers.RelatedField(source='filter_type')
    preservation_type = serializers.RelatedField(source='preservation_type')
    preservation_acid = serializers.RelatedField(source='preservation_acid')

    class Meta:
        model = SampleBottle
        fields = ('id', 'sample', 'bottle', 'filter_type', 'volume_filtered',
                  'preservation_type', 'preservation_volume', 'preservation_acid', 'preservation_comment',)


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

    class Meta:
        model = MethodType
        fields = ('id', 'method', 'preparation', 'description', 'method_detection_limit',
                  'method_detection_limit_unit', 'raw_value_unit', 'final_value_unit',
                  'decimal_places', 'significant_figures', 'standard_operating_procedure',
                  'nwis_parameter_code', 'nwis_parameter_name', 'nwis_method_code')


class FullResultSerializer(serializers.ModelSerializer):
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', source='analyzed_date')
    sample_bottle = FullSampleBottleSerializer(source='sample_bottle')
    constituent = serializers.RelatedField(source='constituent')
    isotope_flag = serializers.RelatedField(source='isotope_flag')

    class Meta:
        model = Result
        fields = ('id', 'sample_bottle', 'method', 'constituent', 'isotope_flag', 'detection_flag', 'raw_value',
                  'final_value', 'daily_detection_limit', 'analyzed_date', 'analysis_comment', 'quality_assurances')


class ResultSerializer(serializers.ModelSerializer):
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', source='analyzed_date')
    sample_bottle = serializers.RelatedField(source='sample_bottle')
    constituent = serializers.RelatedField(source='constituent')
    isotope_flag = serializers.RelatedField(source='isotope_flag')

    class Meta:
        model = Result
        fields = ('id', 'sample_bottle', 'method', 'constituent', 'isotope_flag', 'detection_flag', 'raw_value',
                  'final_value', 'daily_detection_limit', 'analyzed_date', 'analysis_comment', 'quality_assurances')


######
##
## Reports
##
######


class TestReportResultSerializer(serializers.ModelSerializer):
    analyzed_date = serializers.DateTimeField(format='%m/%d/%y', source='analyzed_date')
    sample_bottle = serializers.RelatedField(source='sample_bottle')
    constituent = serializers.RelatedField(source='constituent')
    isotope_flag = serializers.RelatedField(source='isotope_flag')

    class Meta:
        model = Result
        fields = ('id', 'sample_bottle', 'method', 'constituent', 'isotope_flag', 'detection_flag', 'raw_value',
                  'final_value', 'daily_detection_limit', 'analyzed_date', 'analysis_comment', 'quality_assurances')