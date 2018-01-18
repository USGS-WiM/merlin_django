from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin


######
#
# Project and Site
#
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

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mercury_cooperator"
        ordering = ['-id']
        unique_together = ("name", "agency")


class Project(models.Model):
    """A structure to organize a cooperator's sampling events for a particular purpose or goal."""

    name = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=128, blank=True)
    accounting_code = models.CharField(max_length=128, blank=True)
    cooperator = models.ForeignKey('Cooperator', related_name='projects', null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mercury_project"
        ordering = ['-id']


class Site(models.Model):
    """A sampling location, usually an official USGS site. Can be used by more than one project."""

    name = models.CharField(max_length=128)
    usgs_sid = models.CharField(max_length=128, blank=True)
    usgs_scode = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=13, decimal_places=10, null=True, blank=True)
    datum = models.CharField(max_length=128, blank=True)
    method = models.CharField(max_length=128, blank=True)
    site_status = models.CharField(max_length=128, blank=True)
    nwis_customer_code = models.CharField(max_length=128, blank=True)
    projects = models.ManyToManyField('Project', through='ProjectSite', related_name='sites')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mercury_site"
        ordering = ['-id']


class ProjectSite(models.Model):
    """Table to allow many-to-many relationship between Projects and Sites."""

    project = models.ForeignKey('Project')
    site = models.ForeignKey('Site')

    def __str__(self):
        # return str(self.id)
        return str(self.project) + " - " + str(self.site)

    class Meta:
        db_table = "mercury_projectsite"
        ordering = ['-id']
        unique_together = ("project", "site")


######
#
# Bottle
#
######


class BottleType(models.Model):
    """Type of bottle (1L Teflon, 250mL Teflon, Glass Jar, etc.)."""

    bottle_type = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.bottle_type

    class Meta:
        db_table = "mercury_bottletype"
        ordering = ['-id']


class BottlePrefix(models.Model):
    """Reusable bottles with permanently etched IDs (MLO755, DSV330, etc.)."""

    bottle_prefix = models.CharField(max_length=128, unique=True)
    bottle_type = models.ForeignKey('BottleType')
    tare_weight = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True, db_index=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.bottle_prefix

    class Meta:
        db_table = "mercury_bottleprefix"
        ordering = ['-created_date', '-id']


class Bottle(models.Model):
    """Bottles with temporary IDs / "barcodes" consisting of a Bottle Prefix and Suffix,
     where the prefix is the permanent ID of the bottle being used and the suffix is the
     indicator of the current use of that bottle prefix (DIS26009, WIP507BWK, etc.)."""

    bottle_unique_name = models.CharField(max_length=128, unique=True)
    bottle_prefix = models.ForeignKey('BottlePrefix')
    # tare_weight = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    description = models.TextField(blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True, db_index=True)
    # created_by = CreatingUserField(related_name='created_bottles')
    modified_date = models.DateField(auto_now=True, null=True, blank=True)
    # modified_by = LastUserField()
    # modified_by = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.bottle_unique_name

    class Meta:
        db_table = "mercury_bottle"
        ordering = ['-created_date', '-id']


######
#
# Field Sample
#
######


class Sample(models.Model):
    """A sample of a medium at a site, taken at a unique depth and time. Can be stored in one or more bottles."""

    project = models.ForeignKey('Project')
    site = models.ForeignKey('Site')
    sample_date_time = models.DateTimeField()
    depth = models.FloatField()
    length = models.FloatField(null=True, blank=True)
    comment = models.TextField(blank=True)
    received_date = models.DateField(null=True, blank=True)
    replicate = models.IntegerField(null=True, blank=True)
    lab_processing = models.ForeignKey('ProcessingType', null=True, blank=True)
    medium_type = models.ForeignKey('MediumType')
    created_date = models.DateField(default=datetime.now, null=True, blank=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_sample"
        ordering = ['-id']
        unique_together = ("project", "site", "sample_date_time", "depth", "length", "replicate", "medium_type")


class SampleBottle(models.Model):
    """A bottle (reusable or disposable) containing a (portion of a) sample. Used for analysis."""

    sample = models.ForeignKey('Sample', related_name='sample_bottles', null=True)
    # bottle = models.ForeignKey('Bottle', related_name='sample_bottles', unique=True, null=True)
    bottle = models.OneToOneField('Bottle', related_name='sample_bottles', null=True)
    filter_type = models.ForeignKey('FilterType', null=True, blank=True)
    volume_filtered = models.FloatField(null=True, blank=True)
    preservation_type = models.ForeignKey('PreservationType', null=True, blank=True)
    preservation_volume = models.FloatField(null=True, blank=True)
    preservation_acid = models.ForeignKey('Acid', null=True, blank=True)
    preservation_comment = models.TextField(blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_samplebottle"
        unique_together = ("sample", "bottle")


class SampleBottleBromination(models.Model):
    """An event where Bromine Monochloride (BrCl) is added to a bottle containing a water sample.
    Used by the Total Mercury (THg) analysis method."""

    sample_bottle = models.ForeignKey('SampleBottle')
    bromination = models.ForeignKey('Bromination')
    bromination_event = models.IntegerField(null=True, blank=True)
    bromination_volume = models.FloatField(null=True, blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True, db_index=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_samplebottlebromination"
        ordering = ['-created_date', '-id']
        unique_together = ("sample_bottle", "bromination", "bromination_event")


class FilterType(models.Model):
    """Type of filtration used to filter bottle (Calyx, Centrifugal, Quartz Fiber, etc.)."""

    filter = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.filter

    class Meta:
        db_table = "mercury_filtertype"
        ordering = ['-id']


class PreservationType(models.Model):
    """Type of preservation of bottle (Freezing, Acidification, None)."""

    preservation = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.preservation

    class Meta:
        db_table = "mercury_preservationtype"
        ordering = ['-id']


class ProcessingType(models.Model):
    """Description of lab processing (None, In-Lab Filtration, Homogenization and Freeze Dry).
    Indicating what type of processing of the sample may have occurred at the lab.
    This information may be used to document procession charges that should be assessed to the cooperator.
    """

    processing = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.processing

    class Meta:
        db_table = "mercury_processingtype"
        ordering = ['-id']


class MediumType(models.Model):
    """Medium in which sample was taken (various types of water, soil, or air)."""

    nwis_code = models.CharField(max_length=128, blank=True, unique=True)
    nwis_code_qa = models.CharField(max_length=128, blank=True)
    medium = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.nwis_code

    class Meta:
        db_table = "mercury_mediumtype"
        ordering = ['-id']


######
#
# Results
#
######


class Result(models.Model):
    """Results of an analysis method on a sample bottle."""

    sample_bottle = models.ForeignKey('SampleBottle', related_name='results')
    method = models.ForeignKey('MethodType', null=True, blank=True)
    analysis = models.ForeignKey('AnalysisType')
    constituent = models.ForeignKey('ConstituentType')
    isotope_flag = models.ForeignKey('IsotopeFlag')
    detection_flag = models.ForeignKey('DetectionFlag', null=True, blank=True)
    raw_value = models.FloatField(null=True, blank=True)
    final_value = models.FloatField(null=True, blank=True)
    report_value = models.CharField(max_length=128, null=True, blank=True)
    raw_daily_detection_limit = models.FloatField(null=True, blank=True)
    final_daily_detection_limit = models.FloatField(null=True, blank=True)
    final_method_detection_limit = models.FloatField(null=True, blank=True)
    sediment_dry_weight = models.FloatField(max_length=128, null=True, blank=True)
    sample_mass_processed = models.FloatField(max_length=128, null=True, blank=True)
    entry_date = models.DateField(null=True, blank=True)
    analyzed_date = models.DateField(null=True, blank=True)
    analysis_comment = models.TextField(null=True, blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_result"
        ordering = ['-id']
        unique_together = ("sample_bottle", "analysis", "constituent", "isotope_flag")


class DetectionFlag(models.Model):
    """Flag indicating if value needs to be qualified because of proximity to a detection limit (method, daily).
    Also, may indicate if sample was "lost" (will never have a reportable value),
    or "archived" (no analysis has been done but may occur in the future, avoiding a "hole")."""

    detection_flag = models.CharField(max_length=128, unique=True)  # A, <, E, L
    description = models.TextField(blank=True)  # less than, estimated, lost

    def __str__(self):
        return str(self.detection_flag)

    class Meta:
        db_table = "mercury_detectionflag"
        ordering = ['-id']


class IsotopeFlag(models.Model):
    """Flag indicating whether isotope parameters are Ambient (A) or Excess (X-198, X-199, X-200, X-201, X-202)."""

    isotope_flag = models.CharField(max_length=128, unique=True)  # A, X-198, X-199, X-200, X-201, X-202, X-204
    description = models.TextField(blank=True)  # Ambient, Excess of 199, Excess of 200, etc

    def __str__(self):
        return str(self.isotope_flag)

    class Meta:
        db_table = "mercury_isotopeflag"
        ordering = ['-id']


class ResultDataFile(models.Model):
    """File containing the raw result data being uploaded."""

    name = models.CharField(max_length=128, unique=True)
    file = models.FileField()
    result = models.ForeignKey('Result', related_name='result_data_files')
    uploaded_date = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "mercury_resultdatafile"
        ordering = ['-id']


class QualityAssurance(models.Model):
    """Table to allow one-to-many relationship between Results and QualityAssuranceType."""

    quality_assurance = models.ForeignKey('QualityAssuranceType')
    result = models.ForeignKey('Result', related_name='quality_assurances')  # usually three QAs per one result

    def __str__(self):
        return str(self.quality_assurance)

    class Meta:
        db_table = "mercury_qualityassurance"
        ordering = ['-id']
        unique_together = ("quality_assurance", "result")


class QualityAssuranceType(models.Model):
    """Activities performed to prevent mistakes or contamination of samples."""

    quality_assurance = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    nwis_value_qualifier = models.CharField(max_length=128, blank=True)
    nwis_value_qualifier_comment = models.TextField(blank=True)

    def __str__(self):
        return self.quality_assurance

    class Meta:
        db_table = "mercury_qualityassurancetype"
        ordering = ['-id']


######
#
# Analysis, Constituent, & Method
#
######


class AnalysisType(models.Model):
    """Determines which methods can be used to analyze samples from which mediums."""

    analysis = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    mediums = models.ManyToManyField('MediumType', through='AnalysisMedium', related_name='analyses')
    methods = models.ManyToManyField('MethodType', through='AnalysisMethod', related_name='analyses')

    def __str__(self):
        return self.analysis

    class Meta:
        db_table = "mercury_analysistype"
        ordering = ['-id']


class ConstituentType(models.Model):
    """Constituents of samples being analyzed."""

    constituent = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    analyses = models.ManyToManyField('AnalysisType', through='AnalysisConstituent', related_name='constituents')

    def __str__(self):
        return self.constituent

    class Meta:
        db_table = "mercury_constituenttype"
        ordering = ['-id']


class AnalysisConstituent(models.Model):
    """Table to allow many-to-many relationship between Analyses and Constituents."""

    analysis = models.ForeignKey('AnalysisType')
    constituent = models.ForeignKey('ConstituentType')

    def __str__(self):
        # return str(self.id)
        return str(self.analysis) + " - " + str(self.constituent)

    class Meta:
        db_table = "mercury_analysisconstituent"
        ordering = ['-id']
        unique_together = ("analysis", "constituent")


class MethodType(models.Model):
    """Established protocols for analyzing samples."""

    method = models.CharField(max_length=128, unique=True)
    method_code = models.IntegerField(unique=True)
    preparation = models.CharField(max_length=128, blank=True)
    description = models.TextField(blank=True)
    method_detection_limit = models.FloatField(null=True, blank=True)
    method_detection_limit_unit = models.ForeignKey('UnitType', null=True, related_name='mdl_unit')
    raw_value_unit = models.ForeignKey('UnitType', null=True, related_name='raw_unit')
    final_value_unit = models.ForeignKey('UnitType', null=True, related_name='final_unit')
    decimal_places = models.IntegerField(null=True, blank=True)
    significant_figures = models.IntegerField(null=True, blank=True)
    standard_operating_procedure = models.TextField(blank=True)
    nwis_parameter_code = models.CharField(max_length=128, blank=True)
    nwis_parameter_name = models.CharField(max_length=128, blank=True)
    nwis_method_code = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.method

    class Meta:
        db_table = "mercury_methodtype"
        ordering = ['-id']


class UnitType(models.Model):
    """Defined units of measurement for data values."""

    unit = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.unit

    class Meta:
        db_table = "mercury_unittype"
        ordering = ['-id']


class AnalysisMedium(models.Model):
    """Table to allow many-to-many relationship between Analyses and Mediums."""

    analysis_type = models.ForeignKey('AnalysisType')
    medium_type = models.ForeignKey('MediumType')

    def __str__(self):
        # return str(self.id)
        return str(self.analysis_type) + " - " + str(self.medium_type)

    class Meta:
        db_table = "mercury_analysismedium"
        ordering = ['-id']
        unique_together = ("analysis_type", "medium_type")


class AnalysisMethod(models.Model):
    """Table to allow many-to-many relationship between Analyses and Methods."""

    analysis_type = models.ForeignKey('AnalysisType')
    method_type = models.ForeignKey('MethodType')

    def __str__(self):
        # return str(self.id)
        return str(self.analysis_type) + " - " + str(self.method_type)

    class Meta:
        db_table = "mercury_analysismethod"
        unique_together = ("analysis_type", "method_type")


######
#
# Solution
#
######


class Acid(models.Model):
    """A particular concentration of an acid used for sample preservation."""

    code = models.CharField(max_length=128, unique=True)
    concentration = models.FloatField(default=-999)
    comment = models.TextField(blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True, db_index=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = "mercury_acid"
        ordering = ['-created_date', '-id']


class BlankWater(models.Model):
    """Water that has none of the chemicals being analyzed."""

    lot_number = models.CharField(max_length=128, unique=True)
    concentration = models.FloatField(default=-999)
    comment = models.TextField(blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True, db_index=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.lot_number

    class Meta:
        db_table = "mercury_blankwater"
        ordering = ['-created_date', '-id']


class Bromination(models.Model):
    """A particular concentration of Bromine Monochloride (BrCl)."""

    concentration = models.FloatField()
    comment = models.TextField(blank=True)
    created_date = models.DateField(default=datetime.now, null=True, blank=True, db_index=True)
    modified_date = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_bromination"
        ordering = ['-created_date', '-id']


######
#
# Personnel
#
######


class UserProfile(models.Model):
    """Extends the default User model.
       Default fields of the User model: username, first_name, last_name, email, password, groups, user_permissions,
       is_staff, is_active, is_superuser, last_login, date_joined"""
    user = models.OneToOneField(User)

    initials = models.CharField(max_length=6, blank=True)
    phone = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        db_table = "mercury_userprofile"
        ordering = ['-id']


######
#
# Temporary Tables for Excel Macros
#
######


class TempBottle(models.Model):
    bottle_id = models.CharField(max_length=128)
    sort_id = models.IntegerField()

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_tempbottle"


class TempBottle2(models.Model):
    bottle_id = models.CharField(max_length=128)
    sort_id = models.IntegerField()

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "mercury_tempbottle2"


######
#
# Database Views for Reporting
#
######


class ResultCountNawqa(models.Model):
    project_name = models.CharField(max_length=128)
    site_name = models.CharField(max_length=128)
    entry_date = models.DateField()
    row_num = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.row_num)

    class Meta:
        db_table = "report_nawqa_results_count"
        managed = False


class ResultCountProjects(models.Model):
    project_name = models.CharField(max_length=128)
    nwis_customer_code = models.CharField(max_length=128)
    null = models.CharField(max_length=8)
    cooperator_email = models.EmailField()
    entry_date = models.DateField()
    row_num = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.row_num)

    class Meta:
        db_table = "report_projects_results_count"
        managed = False


class SampleNwis(models.Model):
    sample_integer = models.IntegerField()
    user_code = models.CharField(max_length=128)
    agency_cd = models.CharField(max_length=8)
    site_no = models.CharField(max_length=128)
    sample_start_date = models.CharField(max_length=128)
    sample_end_date = models.CharField(max_length=8)
    medium_cd = models.CharField(max_length=128)
    lab_id = models.CharField(max_length=8)
    project_cd = models.CharField(max_length=8)
    aqfr_cd = models.CharField(max_length=8)
    sample_type = models.CharField(max_length=8)
    anl_start_cd = models.CharField(max_length=8)
    anl_src_cd = models.CharField(max_length=8)
    hyd_cond_cd = models.CharField(max_length=8)
    hyd_event_cd = models.CharField(max_length=8)
    tissue_id = models.CharField(max_length=8)
    body_part_cd = models.CharField(max_length=8)
    lab_smp_comment = models.CharField(max_length=8)
    field_smp_comment = models.TextField()
    sample_tz_cd = models.CharField(max_length=8)
    tm_datum_rlblty_cd = models.CharField(max_length=8)
    coll_agency_cd = models.CharField(max_length=8)
    entry_date = models.DateField()
    project_name = models.CharField(max_length=128)
    row_num = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.row_num)

    class Meta:
        db_table = "report_nwis_samples"
        managed = False


class ResultNwis(models.Model):
    sample_integer = models.IntegerField()
    parameter_cd = models.CharField(max_length=128)
    result_value = models.CharField(max_length=128)
    remark_cd = models.CharField(max_length=128)
    qa_cd = models.CharField(max_length=8)
    qw_method_cd = models.CharField(max_length=8)
    results_rd = models.CharField(max_length=8)
    val_qual_cd = models.TextField()
    rpt_lev_value = models.FloatField()
    rpt_lev_cd = models.CharField(max_length=8)
    dqi_cd = models.CharField(max_length=8)
    null_val_qual = models.CharField(max_length=8)
    prep_set_no = models.CharField(max_length=8)
    anl_set_no = models.CharField(max_length=8)
    anl_dt = models.CharField(max_length=8)
    prep_dt = models.CharField(max_length=8)
    lab_result_comment = models.TextField()
    field_result_comment = models.CharField(max_length=8)
    lab_std_dev = models.CharField(max_length=8)
    anl_ent = models.CharField(max_length=8)
    entry_date = models.DateField()
    project_name = models.CharField(max_length=128)
    row_num = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.row_num)

    class Meta:
        db_table = "report_nwis_results_ld"
        managed = False


class ResultCooperator(models.Model):
    site_name = models.CharField("Site", max_length=128)
    usgs_scode = models.CharField("USGS Station ID", max_length=128)
    sample_date_time = models.DateTimeField("Sample Date Time")
    medium = models.CharField("Medium", max_length=128)
    length = models.CharField("Sample Length (m)", max_length=128)
    depth = models.CharField("Sample Depth (m)", max_length=128)
    analysis_date = models.DateField("Analysis Date", max_length=128)
    result_id = models.IntegerField("Results ID")
    bottle = models.CharField("Bottle ID", max_length=128)
    constituent = models.CharField("Parameter", max_length=128)
    final_ddl = models.CharField("DDL (output)", max_length=128)
    detection_flag = models.CharField("D-Flag (output)", max_length=128)
    final_value = models.CharField("Value", max_length=128)
    unit = models.CharField("Units", max_length=128)
    sample_id = models.IntegerField("Field ID")
    analysis_comment = models.TextField("Analysis Comment")
    sample_comment = models.TextField("Sample Comment")
    qaflags = models.CharField("ALL QA FLAGS", max_length=128)
    entry_date = models.DateField()
    project_name = models.CharField(max_length=128)
    cooperator_name = models.CharField(max_length=128)
    row_num = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.row_num)

    class Meta:
        db_table = "report_cooperator_results"
        managed = False


######
#
# Admin
#
######


admin.site.register(Cooperator)
admin.site.register(Project)
admin.site.register(ProjectSite)
admin.site.register(Site)
admin.site.register(Sample)
admin.site.register(SampleBottle)
admin.site.register(SampleBottleBromination)
admin.site.register(Bottle)
admin.site.register(BottlePrefix)
admin.site.register(BottleType)
admin.site.register(FilterType)
admin.site.register(PreservationType)
admin.site.register(ProcessingType)
admin.site.register(MediumType)
admin.site.register(UnitType)
admin.site.register(MethodType)
admin.site.register(Result)
admin.site.register(ResultDataFile)
admin.site.register(AnalysisType)
admin.site.register(ConstituentType)
admin.site.register(AnalysisMedium)
admin.site.register(AnalysisMethod)
admin.site.register(QualityAssurance)
admin.site.register(QualityAssuranceType)
admin.site.register(DetectionFlag)
admin.site.register(IsotopeFlag)
admin.site.register(Acid)
admin.site.register(BlankWater)
admin.site.register(Bromination)