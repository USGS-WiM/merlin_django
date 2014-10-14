from rest_framework import serializers
from mercuryservices.models import *


######
##
## Project and Site
##
######


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'cooperator', 'sites',)


class CooperatorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Cooperator
        fields = ('id', 'name', 'agency', 'email', 'phone', 'sec_phone', 'address', 'city', 'state', 'zipcode',
                  'country', 'projects',)


class SiteSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Site
        fields = ('id', 'name', 'usgs_sid', 'usgs_scode', 'description', 'latitudedd', 'longitudedd', 'projects',)


######
##
## Field Sample
##
######


class FieldSampleSerializer(serializers.HyperlinkedModelSerializer):
    medium_type = serializers.Field(source='medium_type')

    class Meta:
        model = FieldSample
        fields = ('id', 'site', 'time_stamp', 'depth', 'length', 'comment', 'received_time_stamp', 'login_comment',
                  'replicate', 'medium_type',)


class FieldSampleBottleSerializer(serializers.HyperlinkedModelSerializer):
    field_sample = serializers.Field(source='field_sample')
    bottle = serializers.Field(source='bottle')
    filter_type = serializers.Field(source='filter_type')
    preservation_type = serializers.Field(source='preservation_type')
    preservation_acid = serializers.Field(source='preservation_acid')

    class Meta:
        model = FieldSampleBottle
        fields = ('id', 'field_sample', 'bottle', 'filter_type', 'tare_weight', 'volume_filtered', 'filter_weight',
                  'preservation_type', 'preservation_volume', 'preservation_acid', 'preservation_comment',)


class BottleSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bottle
        fields = ('id', 'bottle_unique_name', 'description',)


class FilterTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = FilterType
        fields = ('id', 'filter', 'description',)


class PreservationTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PreservationType
        fields = ('id', 'preservation', 'description',)


class MediumTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MediumType
        fields = ('url', 'id', 'nwis_code', 'medium', 'description', 'comment',)


######
##
## Method and Result
##
######


class UnitTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UnitType
        fields = ('id', 'unit', 'description',)


class MethodTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MethodType
        fields = ('id', 'method', 'preparation', 'description', 'raw_value_unit', 'final_value_unit',
                  'method_detection_limit', 'decimal_places', 'significant_figures', 'standard_operating_procedure',
                  'nwis_parameter_code', 'nwis_parameter_name', 'nwis_method_code')


class ResultSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Result
        fields = ('id', 'field_sample_bottle', 'method', 'isotope_flag', 'detection_flag', 'raw_value', 'final_value',
                  'daily_detection_limit', 'analyzed_date', 'analysis_comment', 'quality_assurances')


######
##
## Constituent (Analyte)
##
######


class ConstituentTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ConstituentType
        fields = ('id', 'constituent', 'description',)


class ConstituentMediumSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ConstituentMedium
        fields = ('id', 'constituent_type', 'medium_type',)


class ConstituentMethodSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ConstituentMethod
        fields = ('id', 'constituent_type', 'method_type',)


######
##
## Quality Assurance
##
######


class QualityAssuranceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = QualityAssurance
        fields = ('id', 'quality_assurance', 'description',)


class DetectionLimitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DetectionLimit
        fields = ('id', 'limit', 'limit_unit', 'description',)


######
##
## Solution
##
######


class AcidSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Acid
        fields = ('id', 'code', 'concentration', 'comment',)


class BlankWaterSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = BlankWater
        fields = ('id', 'lot_number', 'concentration', 'comment',)


class BrominationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bromination
        fields = ('id', 'concentration', 'bromination_date', 'comment',)


#######
##
## Personnel
##
######


# class RoleSerializer(serializers.HyperlinkedModelSerializer):
#
#     class Meta:
#         model = Role
#         fields = ('id', 'role', 'description', 'users',)
#
#
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'fname', 'lname', 'initials', 'email', 'phone', 'role',)


######
##
## Status
##
######


class StatusSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Status
        fields = ('id', 'status_id', 'status_type', 'procedure_type', 'user', 'time_stamp', 'note',)


class ProcedureStatusTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProcedureStatusType
        fields = ('id','procedure_type', 'status_type',)


class StatusTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StatusType
        fields = ('id', 'status_type',)


class ProcedureTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProcedureType
        fields = ('id', 'procedure',)

