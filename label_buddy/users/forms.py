from allauth.account.forms import SignupForm
from django import forms 

class ExtendedSignUpForm(SignupForm):
    name = forms.CharField(max_length=256, label="Full name")

    def signup(self, request, user):
        user.name = self.cleaned_data["name"]
        user.save()
        return user