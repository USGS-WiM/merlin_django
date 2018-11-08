from django import forms
from datetime import datetime
from merlinservices.models import UserProfile, Cooperator
from django.contrib.auth.models import User
from datetimewidget.widgets import DateTimeWidget
from django.forms.widgets import DateTimeInput
import requests
import json


def get_bottle_type_choices():
    r = requests.request(method='GET', url='http://localhost:8000/mercuryservices/bottletypes/')
    bottle_types = r.json()
    bottle_type_choices = []
    for bottle_type in bottle_types:
        bottle_type_choices.append((bottle_type["id"], bottle_type["bottle_type"]))
    #print(bottle_type_choices)
    return bottle_type_choices


def get_datetime_today():
    string_today = datetime.today().date().strftime('%Y-%m-%d') + " 00:00:00"
    datetime_today = datetime.strptime(string_today, '%Y-%m-%d %H:%M:%S')
    return datetime_today


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="username")
    email = forms.CharField(help_text="email")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="password")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    initials = forms.CharField(help_text="initials", required=False)
    phone = forms.IntegerField(help_text="phone number", required=False)

    class Meta:
        model = UserProfile
        fields = ('initials', 'phone')


class CooperatorForm(forms.Form):
    #id = forms.IntegerField()
    name = forms.CharField(help_text="Name")
    agency = forms.CharField(help_text="Agency")
    email = forms.CharField(help_text="Email", required=False)
    phone = forms.IntegerField(help_text="Phone Number", required=False)
    sec_phone = forms.IntegerField(help_text="Secondary Phone Number", required=False)
    address = forms.CharField(help_text="Address", required=False)
    city = forms.CharField(help_text="City", required=False)
    state = forms.CharField(help_text="State", required=False)
    zipcode = forms.IntegerField(help_text="Zipcode", required=False)
    country = forms.CharField(help_text="Country", required=False)

    # class Meta:
    #     model = Cooperator
    #     fields = ('name', 'agency', 'email', 'phone', 'sec_phone', 'address', 'city', 'state', 'zipcode', 'country')


class ProjectForm(forms.Form):
    name = forms.CharField(help_text="Name")


class SiteForm(forms.Form):
    name = forms.CharField(help_text="Name")


class SampleSearchForm(forms.Form):
    project = forms.CharField(help_text="Project Name")
    site = forms.CharField(help_text="Site Name")
    date_after = forms.DateTimeField(help_text="After Date")
    date_before = forms.DateTimeField(help_text="Before Date")


class SampleBottleForm(forms.Form):
    bottle_unique_name = forms.CharField(help_text="Bottle Unique Name")


class AcidForm(forms.Form):
    code = forms.CharField(help_text="Code")
    concentration = forms.DecimalField(help_text="Concentration")
    time_stamp = forms.DateTimeField(help_text="Date", initial=get_datetime_today(), widget=DateTimeInput())
    comment = forms.CharField(help_text="Comment", required=False)


class BlankWaterForm(forms.Form):
    lot_number = forms.CharField(help_text="Lot Number")
    concentration = forms.DecimalField(help_text="Concentration")
    time_stamp = forms.DateTimeField(help_text="Date", initial=get_datetime_today(), widget=DateTimeInput())
    comment = forms.CharField(help_text="Comment", required=False)


class BottleForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BottleForm, self).__init__(*args, **kwargs)
        self.fields['bottle_type'] = forms.ChoiceField(
            help_text="Bottle Type",
            choices=get_bottle_type_choices()
        )

    bottle_unique_name = forms.CharField(help_text="Bottle Unique Name")
    time_stamp = forms.CharField(help_text="Date", initial=datetime.today().date().strftime('%Y-%m-%d') + " 00:00:00")
    tare_weight = forms.DecimalField(help_text="Tare Weight", required=False)
    bottle_type = forms.ChoiceField(help_text="Bottle Type")
    description = forms.CharField(help_text="Description", required=False)


class BottleRangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BottleRangeForm, self).__init__(*args, **kwargs)
        self.fields['bottle_type'] = forms.ChoiceField(
            help_text="Bottle Type",
            choices=get_bottle_type_choices()
        )

    prefix = forms.CharField(help_text="Bottle Prefix")
    suffix = forms.CharField(help_text="Bottle Suffix")
    range_start = forms.CharField(help_text="Bottle Range Start")
    range_end = forms.CharField(help_text="Bottle Range End")
    time_stamp = forms.DateTimeField(help_text="Date", initial=get_datetime_today(), widget=DateTimeInput())
    tare_weight = forms.DecimalField(help_text="Tare Weight", required=False)
    bottle_type = forms.ChoiceField(help_text="Bottle Type")
    description = forms.CharField(help_text="Description", required=False)


class BrominationForm(forms.Form):
    #dateTimeOptions = {'format': 'yyyy-mm-dd HH:ii:ss', 'autoclose': True, 'showMeridian': True}
    concentration = forms.DecimalField(help_text="Concentration")
    time_stamp = forms.DateTimeField(help_text="Date", initial=get_datetime_today(), widget=DateTimeInput())
    #time_stamp = forms.DateTimeField(
    # help_text="Date")#, widget=DateTimeWidget(usel10n=True, bootstrap_version=3, options=dateTimeOptions))
    comment = forms.CharField(help_text="Comment", required=False)
