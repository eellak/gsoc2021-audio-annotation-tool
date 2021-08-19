from allauth.account.forms import SignupForm
from django import forms 
from .models import User

class ExtendedSignUpForm(SignupForm):
    name = forms.CharField(max_length=256, label="Full name")

    def signup(self, request, user):
        user.name = self.cleaned_data["name"]
        user.save()
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "name",
            "email",
            "phone_number",
            "avatar",
        ]
        labels = {
            'name': '<b>Name:</b>',
            'email': '<b>Email:</b>',
            'phone_number': '<b>Phone number:</b>',
            'avatar': '<b>Avatar:</b>',
        }

    
    def clean_avatar(self):
        image = self.cleaned_data.get("avatar", False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
            return image
        else:
            raise forms.ValidationError("Please provide a logo")

    def clean_email(self):
        # when field is cleaned, we always return the existing model field.
        return self.instance.email