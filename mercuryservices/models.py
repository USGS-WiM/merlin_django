from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib import admin


######
##
## Project and Site
##
######


class Cooperator(models.Model):
    name = models.CharField(max_length=128)
    agency = models.CharField(max_length=128)
    email = models.EmailField(blank=True)
    phone = models.BigIntegerField(null=True, blank=True)
    sec_phone = models.BigIntegerField(null=True, blank=True)
    address = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zipcode = models.BigIntegerField(null=True, blank=True)
    country = models.CharField(max_length=128, blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True)
    accounting_code = models.CharField(max_length=128, blank=True)
    cooperator = models.ForeignKey('Cooperator', related_name='projects')
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.name


class Site(models.Model):
    """A sampling location, usually an official USGS site."""

    name = models.CharField(max_length=128)
    usgs_sid = models.CharField(max_length=128, blank=True)
    usgs_scode = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    latitudedd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    longitudedd = models.DecimalField(max_digits=11, decimal_places=3, null=True, blank=True)
    datum = models.CharField(max_length=128, blank=True)
    method = models.CharField(max_length=128, blank=True)
    site_status = models.CharField(max_length=128, blank=True)
    nwis_customer_code = models.CharField(max_length=128, blank=True)
    projects = models.ManyToManyField('Project', through='ProjectSite', related_name='sites')
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.name


class ProjectSite(models.Model):
    project = models.ForeignKey('Project')
    site = models.ForeignKey('Site')

    def __str__(self):
        return str(self.id)


######
##
## Field Sample
##
######


class Bottle(models.Model):
    """Reusable bottles with permanently etched IDs."""

    bottle_unique_name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.bottle_unique_name


class FilterType(models.Model):
    filter = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.filter


class PreservationType(models.Model):
    """How sample is preserved; usually an acid, but occasionally freezing or freeze drying."""

    preservation = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.preservation


class MediumType(models.Model):
    """Medium in which sample was taken (various types of water, soil, or air)."""

    nwis_code = models.CharField(max_length=128, blank=True)
    medium = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.medium


class FieldSample(models.Model):
    """A sample of a medium at a site, taken at a unique depth and time. Can be stored in one or more bottles."""

    site = models.ForeignKey('Site')
    time_stamp = models.DateTimeField()
    depth = models.FloatField()
    length = models.FloatField(null=True, blank=True)
    comment = models.TextField(blank=True)
    received_time_stamp = models.DateTimeField()
    login_comment = models.TextField(blank=True)
    replicate = models.IntegerField(null=True, blank=True)
    medium_type = models.ForeignKey('MediumType')
    #status = models.ForeignKey('Status')

    def __str__(self):
        return str(self.id)


class FieldSampleBottle(models.Model):
    """A bottle (reusable or disposable) containing a (portion of a) sample. Used for analysis methods."""

    field_sample = models.ForeignKey('FieldSample')
    bottle = models.ForeignKey('Bottle')
    filter_type = models.ForeignKey('FilterType')
    tare_weight = models.FloatField(null=True, blank=True)
    volume_filtered = models.FloatField(null=True, blank=True)
    filter_weight = models.FloatField(null=True, blank=True)
    preservation_type = models.ForeignKey('PreservationType')
    preservation_volume = models.FloatField(null=True, blank=True)
    preservation_acid = models.ForeignKey('Acid')
    preservation_comment = models.TextField(blank=True)
    description = models.TextField(blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return str(self.id)


######
##
## Methods and Results
##
######


class UnitType(models.Model):
    unit = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.unit


class MethodType(models.Model):
    method = models.CharField(max_length=128)
    preparation = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    #raw_unit = models.ForeignKey('UnitType')
    #final_unit = models.ForeignKey('UnitType')
    unit = models.ForeignKey('UnitType')
    method_detection_limit = models.ForeignKey('DetectionLimit')
    decimal_places = models.IntegerField(null=True, blank=True)
    significant_figures = models.IntegerField(null=True, blank=True)
    standard_operating_procedure = models.TextField(blank=True)
    nwis_parameter_code = models.CharField(max_length=128, blank=True)
    nwis_parameter_name = models.CharField(max_length=128, blank=True)
    nwis_method_code = models.CharField(max_length=128, blank=True)

    #status = models.ForeignKey('Status')

    def __str__(self):
        return self.method


class Result(models.Model):
    """Results of a method analysis on a sample bottle."""

    field_sample_bottle = models.ForeignKey('FieldSampleBottle')
    method = models.ForeignKey('MethodType')
    isotope_flag = models.ForeignKey('IsotopeFlag')
    detection_flag = models.ForeignKey('DetectionFlag')
    raw_value = models.FloatField()
    final_value = models.FloatField()
    daily_detection_limit = models.FloatField()
    analyzed_date = models.DateTimeField()
    analysis_comment = models.TextField(blank=True)
    # also, there will usually be three QAs for each result
    ##
    # ****placeholder for legacy data fields****
    ##
    #status = models.ForeignKey('Status')

    def __str__(self):
        return str(self.id)
    

######
##
## Constituent (Analyte)
##
######


class ConstituentType(models.Model):
    """Determines which methods can be used to analyze samples from which mediums."""

    constituent = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    #status = models.ForeignKey(Status)

    def __str__(self):
        return self.constituent


class ConstituentMedium(models.Model):
    constituent_type = models.ForeignKey('ConstituentType')
    medium_type = models.ForeignKey('MediumType')
    #status = models.ForeignKey(Status)

    def __str__(self):
        return str(self.id)


class ConstituentMethod(models.Model):
    constituent_type = models.ForeignKey('ConstituentType')
    method_type = models.ForeignKey('MethodType')
    #status = models.ForeignKey(Status)

    def __str__(self):
        return str(self.id)


######
##
## Quality Assurance
##
######


class QualityAssurance(models.Model):
    quality_assurance = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    result = models.ForeignKey('Result', related_name='quality_assurances')  # usually three QAs per result
    #status = models.ForeignKey(Status)

    def __str__(self):
        return self.quality_assurance


class DetectionLimit(models.Model):
    """The detection limit for a method (distinct from daily or batch detection limits, which are result attributes)."""

    limit = models.CharField(max_length=128)
    limit_unit = models.ForeignKey('UnitType')
    description = models.TextField(blank=True)
    #status = models.ForeignKey(Status)

    def __str__(self):
        return self.limit


class DetectionFlag(models.Model):
    detection_flag = models.CharField(max_length=128)  # <, E, L
    description = models.TextField(blank=True)  # less than, estimated, lost
    #status = models.ForeignKey(Status)

    def __str__(self):
        return str(self.detection_flag)


class IsotopeFlag(models.Model):
    isotope_flag = models.CharField(max_length=128)  # A, X-198, X-199, X-200, X-201, X-202, X-204
    description = models.TextField(blank=True)
    #status = models.ForeignKey(Status)

    def __str__(self):
        return str(self.isotope_flag)


######
##
## Solution
##
######


class Acid(models.Model):
    code = models.CharField(max_length=128)
    concentration = models.FloatField(default=-999)
    comment = models.TextField(blank=True)
    #status = models.ForeignKey(Status)

    def __str__(self):
        return self.code


class BlankWater(models.Model):
    lot_number = models.CharField(max_length=128)
    concentration = models.FloatField(default=-999)
    comment = models.TextField(blank=True)
    #status = models.ForeignKey(Status)

    def __str__(self):
        return self.lot_number


class Bromination(models.Model):
    concentration = models.FloatField()
    bromination_date = models.DateTimeField()
    comment = models.TextField(blank=True)
    #status = models.ForeignKey(Status)

    def __str__(self):
        return str(self.id)


######
##
## Personnel
##
######


# class Role(models.Model):
#     role = models.CharField(max_length=128)
#     description = models.TextField()
#
#     def __str__(self):
#         return self.role
#
#
# class User(models.Model):
#     username = models.CharField(max_length=128)
#     fname = models.CharField(max_length=128, blank=True)
#     lname = models.CharField(max_length=128, blank=True)
#     initials = models.CharField(max_length=6, blank=True)
#     email = models.EmailField()
#     phone = models.BigIntegerField(null=True, blank=True)
#     role = models.ForeignKey('Role', related_name='users')
#
#     def __str__(self):
#         return self.username

class UserProfile(models.Model):
    """Extends the default User model.
       Default fields: username, first_name, last_name, email, password, groups, user_permissions,
       is_staff, is_active, is_superuser, last_login, date_joined"""
    user = models.OneToOneField(User)

    initials = models.CharField(max_length=6, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username


######
##
## Status
##
######


class Status(models.Model):
    status_id = models.BigIntegerField()
    status_type = models.ForeignKey('StatusType')
    procedure_type = models.ForeignKey('ProcedureType')
    user = models.ForeignKey('UserProfile')
    time_stamp = models.DateTimeField()
    note = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.status_id


class ProcedureStatusType(models.Model):
    procedure_type = models.ForeignKey('ProcedureType')
    status_type = models.ForeignKey('StatusType')

    def __str__(self):
        return str(self.id)


class StatusType(models.Model):
    status_type = models.CharField(max_length=128)

    def __str__(self):
        return self.status_type


class ProcedureType(models.Model):
    procedure = models.CharField(max_length=128)

    def __str__(self):
        return self.procedure


######
##
## Admin
##
######


admin.site.register(Cooperator)
admin.site.register(Project)
admin.site.register(ProjectSite)
admin.site.register(Site)
admin.site.register(FieldSample)
admin.site.register(FieldSampleBottle)
admin.site.register(Bottle)
admin.site.register(FilterType)
admin.site.register(PreservationType)
admin.site.register(MediumType)
admin.site.register(UnitType)
admin.site.register(MethodType)
admin.site.register(Result)
admin.site.register(ConstituentType)
admin.site.register(ConstituentMedium)
admin.site.register(ConstituentMethod)
admin.site.register(QualityAssurance)
admin.site.register(DetectionLimit)
admin.site.register(DetectionFlag)
admin.site.register(IsotopeFlag)
admin.site.register(Acid)
admin.site.register(BlankWater)
admin.site.register(Bromination)
admin.site.register(Status)
admin.site.register(StatusType)
admin.site.register(ProcedureType)
admin.site.register(ProcedureStatusType)