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


class CooperatorForm(forms.ModelForm):
    #id = forms.IntegerField()
    name = forms.CharField(help_text="name")
    agency = forms.CharField(help_text="agency")
    email = forms.CharField(help_text="email", required=False)
    phone = forms.IntegerField(help_text="phone number", required=False)
    sec_phone = forms.IntegerField(help_text="secondary phone number", required=False)
    address = forms.CharField(help_text="address", required=False)
    city = forms.CharField(help_text="city", required=False)
    state = forms.CharField(help_text="state", required=False)
    zipcode = forms.IntegerField(help_text="zipcode", required=False)
    country = forms.CharField(help_text="country", required=False)

    class Meta:
        model = Cooperator
        fields = ('name', 'agency', 'email', 'phone', 'sec_phone', 'address', 'city', 'state', 'zipcode', 'country')