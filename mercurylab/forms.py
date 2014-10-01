from django import forms
from mercuryservices.models import UserProfile, Cooperator
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    initials = forms.CharField(help_text="Please enter your initials.", required=False)
    phone = forms.IntegerField(help_text="Please enter your phone number.", required=False)

    class Meta:
        model = UserProfile
        fields = ('initials', 'phone')


class CooperatorForm(forms.ModelForm):
    name = forms.CharField(help_text="Please enter a name.")
    agency = forms.CharField(help_text="Please enter an agency.")
    email = forms.CharField(help_text="Please enter your email.", required=False)
    phone = forms.IntegerField(help_text="Please enter your phone number.", required=False)
    sec_phone = forms.IntegerField(help_text="Please enter your secondary phone number.", required=False)
    city = forms.CharField(help_text="Please enter your city.", required=False)
    state = forms.CharField(help_text="Please enter your state.", required=False)
    zipcode = forms.IntegerField(help_text="Please enter your zipcode.", required=False)
    country = forms.CharField(help_text="Please enter your country.", required=False)


    class Meta:
        model = Cooperator
        fields = ('name', 'agency', 'email', 'phone')