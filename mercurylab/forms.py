from django import forms
from mercuryservices.models import UserProfile, Cooperator
from django.contrib.auth.models import User


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


