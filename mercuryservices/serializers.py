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
        fields = ('id', 'name', 'description', 'cooperator', 'sites',)


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


class SampleSerializer(serializers.ModelSerializer):
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')
    received_time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='received_time_stamp')
    medium_type = serializers.PrimaryKeyRelatedField(source='medium_type')

    class Meta:
        model = Sample
        fields = ('id', 'project', 'site', 'time_stamp', 'depth', 'length', 'comment', 'received_time_stamp',
                  'replicate', 'medium_type', 'lab_processing', 'sample_bottles')


class SampleBottleSerializer(serializers.ModelSerializer):
    field_sample = serializers.PrimaryKeyRelatedField(source='field_sample')
    bottle = serializers.PrimaryKeyRelatedField(source='bottle')
    filter_type = serializers.PrimaryKeyRelatedField(source='filter_type')
    preservation_type = serializers.PrimaryKeyRelatedField(source='preservation_type')
    preservation_acid = serializers.PrimaryKeyRelatedField(source='preservation_acid')

    class Meta:
        model = SampleBottle
        fields = ('id', 'field_sample', 'bottle', 'constituent_type', 'filter_type', 'volume_filtered',
                  'preservation_type', 'preservation_volume', 'preservation_acid', 'preservation_comment',)


class SampleBottleBrominationSerializer(serializers.ModelSerializer):
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')

    class Meta:
        model = SampleBottleBromination
        fields = ('id', 'field_sample_bottle', 'bromination', 'bromination_event', 'bromination_volume', 'time_stamp',)


class BottleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'description', 'tare_weight', 'bottle_type',)


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


class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = ('id', 'field_sample_bottle', 'method', 'isotope_flag', 'detection_flag', 'raw_value', 'final_value',
                  'daily_detection_limit', 'analyzed_date', 'analysis_comment', 'quality_assurances')


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
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')

    class Meta:
        model = Acid
        fields = ('id', 'code', 'concentration', 'time_stamp', 'comment',)


class BlankWaterSerializer(serializers.ModelSerializer):
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')

    class Meta:
        model = BlankWater
        fields = ('id', 'lot_number', 'concentration', 'time_stamp', 'comment',)


class BrominationSerializer(serializers.ModelSerializer):
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')

    class Meta:
        model = Bromination
        fields = ('id', 'concentration', 'time_stamp', 'comment',)


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
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'groups', 'user_permissions',)#, 'initials', 'phone')


######
##
## Status
##
######


class StatusSerializer(serializers.ModelSerializer):
    time_stamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', source='time_stamp')

    class Meta:
        model = Status
        fields = ('id', 'status_id', 'status_type', 'procedure_type', 'user', 'time_stamp', 'note',)


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

