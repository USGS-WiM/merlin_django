from django import forms
from mercuryservices.models import UserProfile, Cooperator
from django.contrib.auth.models import User
from datetimewidget.widgets import DateTimeWidget


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


class SampleBottleForm(forms.Form):
    bottle_unique_name = forms.CharField(help_text="Bottle Unique Name")


class AcidForm(forms.Form):
    code = forms.CharField(help_text="Code")
    concentration = forms.DecimalField(help_text="Concentration")
    comment = forms.CharField(help_text="Comment", required=False)


class BlankWaterForm(forms.Form):
    lot_number = forms.CharField(help_text="Lot Number")
    concentration = forms.DecimalField(help_text="Concentration")
    comment = forms.CharField(help_text="Comment", required=False)


class BottleForm(forms.Form):
    bottle_unique_name = forms.CharField(help_text="Bottle Unique Name")
    tare_weight = forms.DecimalField(help_text="Tare Weight")
    bottle_type = forms.CharField(help_text="Bottle Type")
    description = forms.CharField(help_text="Description", required=False)


class BrominationForm(forms.Form):
    dateTimeOptions = {'format': 'yyyy-mm-dd HH:ii:ss', 'autoclose': True, 'showMeridian': True}
    bromination_date = forms.DateTimeField(help_text="Bromination Date")#, widget=DateTimeWidget(usel10n=True, bootstrap_version=3, options=dateTimeOptions))
    concentration = forms.DecimalField(help_text="Concentration")
    comment = forms.CharField(help_text="Comment", required=False)




