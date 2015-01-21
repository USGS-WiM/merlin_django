from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib import admin


######
##
## Project and Site
##
######


class Cooperator(models.Model):
    """A person or organization submitting data to the Mercury Lab."""

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
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    """A structure to organize a cooperator's sampling events for a particular purpose or goal."""

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True)
    accounting_code = models.CharField(max_length=128, blank=True)
    cooperator = models.ForeignKey('Cooperator', related_name='projects')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.name


class Site(models.Model):
    """A sampling location, usually an official USGS site. Can be used by more than one project."""

    name = models.CharField(max_length=128)
    usgs_sid = models.CharField(max_length=128, blank=True)
    usgs_scode = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=3, null=True, blank=True)
    datum = models.CharField(max_length=128, blank=True)
    method = models.CharField(max_length=128, blank=True)
    site_status = models.CharField(max_length=128, blank=True)
    nwis_customer_code = models.CharField(max_length=128, blank=True)
    projects = models.ManyToManyField('Project', through='ProjectSite', related_name='sites')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.name


class ProjectSite(models.Model):
    """Table to allow many-to-many relationship between Projects and Sites."""

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
    """Reusable bottles with permanently etched IDs (MLO751AA, WIP010BSH, etc.)."""

    bottle_unique_name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    tare_weight = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    bottle_type = models.ForeignKey('BottleType')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.bottle_unique_name


class BottleType(models.Model):
    """Type of bottle (1L Teflon, 250mL Teflon, Glass Jar, etc.)."""

    bottle_type = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.bottle_type


class FilterType(models.Model):
    """Type of filtration used to filter bottle (Calyx, Centrifugal, Quartz Fiber, etc.)."""

    filter = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.filter


class PreservationType(models.Model):
    """Type of preservation of bottle (Freezing, Acidification, None)."""

    preservation = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.preservation


class ProcessingType(models.Model):
    """Description of lab processing (None, In-Lab Filtration, Homogenization and Freeze Dry).
    Indicating what type of processing of the sample may have occurred at the lab.
    This information may be used to document procession charges that should be assessed to the cooperator.
    """

    processing = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.processing


class MediumType(models.Model):
    """Medium in which sample was taken (various types of water, soil, or air)."""

    nwis_code = models.CharField(max_length=128, blank=True)
    medium = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.medium


class Sample(models.Model):
    """A sample of a medium at a site, taken at a unique depth and time. Can be stored in one or more bottles."""

    project = models.ForeignKey('Project')
    site = models.ForeignKey('Site')
    time_stamp = models.DateTimeField()
    depth = models.FloatField()
    length = models.FloatField(null=True, blank=True)
    comment = models.TextField(blank=True)
    received_time_stamp = models.DateField()
    replicate = models.IntegerField(null=True, blank=True)
    lab_processing = models.ForeignKey('ProcessingType', null=True, blank=True)
    medium_type = models.ForeignKey('MediumType')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.id)


class SampleBottle(models.Model):
    """A bottle (reusable or disposable) containing a (portion of a) sample. Used for analysis methods."""

    sample = models.ForeignKey('Sample', related_name='sample_bottles')
    bottle = models.ForeignKey('Bottle')
    filter_type = models.ForeignKey('FilterType')
    volume_filtered = models.FloatField(null=True, blank=True)
    preservation_type = models.ForeignKey('PreservationType')
    preservation_volume = models.FloatField(null=True, blank=True)
    preservation_acid = models.ForeignKey('Acid', null=True, blank=True)
    preservation_comment = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.id)


# class FullSampleBottle(models.Model):
#     """A denormalized database view (a 'stored query', not a table) that adds all the fields from the related
#     Sample record to each SampleBottle record. The normalized relation is one Sample to many SampleBottles.
#     This view must be manually created and managed outside of Django, but creating this class here in the Models.py
#     file will allow the view to be used by Django like any normal table. This is accomplished by the 'managed'
#     meta option, set here to False."""
#
#     class Meta:
#         managed=False


class SampleBottleBromination(models.Model):
    """An event where Bromine Monochloride (BrCl) is added to a bottle containing a water sample.
    Used by the Total Mercury (THg) analysis method."""

    sample_bottle = models.ForeignKey('SampleBottle')
    bromination = models.ForeignKey('Bromination')
    bromination_event = models.IntegerField(null=True, blank=True)
    bromination_volume = models.FloatField(null=True, blank=True)
    time_stamp = models.DateTimeField()
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.id)


######
##
## Methods and Results
##
######


class UnitType(models.Model):
    """Defined units of measurement for data values."""

    unit = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.unit


class MethodType(models.Model):
    """Established protocols for analyzing samples."""

    method = models.CharField(max_length=128)
    preparation = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    method_detection_limit = models.CharField(max_length=128)
    method_detection_limit_unit = models.ForeignKey('UnitType', null=True, related_name='mdl_unit')
    raw_value_unit = models.ForeignKey('UnitType', null=True, related_name='raw_unit')
    final_value_unit = models.ForeignKey('UnitType', null=True, related_name='final_unit')
    #unit = models.ForeignKey('UnitType')
    decimal_places = models.IntegerField(null=True, blank=True)
    significant_figures = models.IntegerField(null=True, blank=True)
    standard_operating_procedure = models.TextField(blank=True)
    nwis_parameter_code = models.CharField(max_length=128, blank=True)
    nwis_parameter_name = models.CharField(max_length=128, blank=True)
    nwis_method_code = models.CharField(max_length=128, blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.method


class Result(models.Model):
    """Results of a method analysis on a sample bottle."""

    sample_bottle = models.ForeignKey('SampleBottle', related_name='results')
    method = models.ForeignKey('MethodType', null=True, blank=True)
    constituent = models.ForeignKey('ConstituentType')
    isotope_flag = models.ForeignKey('IsotopeFlag')
    detection_flag = models.ForeignKey('DetectionFlag', null=True, blank=True)
    raw_value = models.FloatField(null=True, blank=True)
    final_value = models.FloatField(null=True, blank=True)
    daily_detection_limit = models.FloatField(null=True, blank=True)
    analyzed_date = models.DateTimeField(null=True, blank=True)
    analysis_comment = models.TextField(blank=True)
    ##
    # ****placeholder for legacy data fields****
    ##
    status = models.ForeignKey('Status', null=True, blank=True)

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
    mediums = models.ManyToManyField('MediumType', through='ConstituentMedium', related_name='constituents')
    methods = models.ManyToManyField('MethodType', through='ConstituentMethod', related_name='constituents')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.constituent


class ConstituentMedium(models.Model):
    """Table to allow many-to-many relationship between Constituents and Mediums."""

    constituent_type = models.ForeignKey('ConstituentType')
    medium_type = models.ForeignKey('MediumType')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.id)


class ConstituentMethod(models.Model):
    """Table to allow many-to-many relationship between Constituents and Methods."""

    constituent_type = models.ForeignKey('ConstituentType')
    method_type = models.ForeignKey('MethodType')
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.id)


######
##
## Quality Assurance
##
######


class QualityAssurance(models.Model):
    """Table to allow one-to-many relationship between Results and QualityAssuranceType."""

    quality_assurance = models.ForeignKey('QualityAssuranceType')
    result = models.ForeignKey('Result', related_name='quality_assurances')  # usually three QAs per one result
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.id)


class QualityAssuranceType(models.Model):
    """Activities performed to prevent mistakes or contamination of samples."""

    quality_assurance = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.quality_assurance


class DetectionFlag(models.Model):
    """Flag indicating if value needs to be qualified because of proximity to a detection limit (method, daily).
    Also, may indicate if sample was "lost" (will never have a reportable value),
    or "archived" (no analysis has been done but may occur in the future, avoiding a "hole")."""

    detection_flag = models.CharField(max_length=128)  # A, <, E, L
    description = models.TextField(blank=True)  # less than, estimated, lost
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.detection_flag)


class IsotopeFlag(models.Model):
    """Flag indicating whether isotope parameters are Ambient (A) or Excess (X-198, X-199, X-200, X-201, X-202)."""

    isotope_flag = models.CharField(max_length=128)  # A, X-198, X-199, X-200, X-201, X-202, X-204
    description = models.TextField(blank=True)  # Ambient, Excess of 199, Excess of 200, etc
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return str(self.isotope_flag)


######
##
## Solution
##
######


class Acid(models.Model):
    """A particular concentration of an acid used for sample preservation."""

    code = models.CharField(max_length=128)
    concentration = models.FloatField(default=-999)
    time_stamp = models.DateTimeField()
    comment = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.code


class BlankWater(models.Model):
    """Water that has none of the chemicals being analyzed."""

    lot_number = models.CharField(max_length=128)
    concentration = models.FloatField(default=-999)
    time_stamp = models.DateTimeField()
    comment = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

    def __str__(self):
        return self.lot_number


class Bromination(models.Model):
    """A particular concentration of Bromine Monochloride (BrCl)."""

    concentration = models.FloatField()
    time_stamp = models.DateTimeField()
    comment = models.TextField(blank=True)
    status = models.ForeignKey('Status', null=True, blank=True)

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
    user = models.ForeignKey(User)
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
admin.site.register(Sample)
admin.site.register(SampleBottle)
admin.site.register(SampleBottleBromination)
admin.site.register(Bottle)
admin.site.register(BottleType)
admin.site.register(FilterType)
admin.site.register(PreservationType)
admin.site.register(ProcessingType)
admin.site.register(MediumType)
admin.site.register(UnitType)
admin.site.register(MethodType)
admin.site.register(Result)
admin.site.register(ConstituentType)
admin.site.register(ConstituentMedium)
admin.site.register(ConstituentMethod)
admin.site.register(QualityAssurance)
admin.site.register(QualityAssuranceType)
admin.site.register(DetectionFlag)
admin.site.register(IsotopeFlag)
admin.site.register(Acid)
admin.site.register(BlankWater)
admin.site.register(Bromination)
admin.site.register(Status)
admin.site.register(StatusType)
admin.site.register(ProcedureType)
admin.site.register(ProcedureStatusType)