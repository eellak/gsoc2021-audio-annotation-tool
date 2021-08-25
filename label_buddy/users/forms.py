from allauth.account.forms import SignupForm
from django import forms 
from .models import User

class ExtendedSignUpForm(SignupForm):
    name = forms.CharField(max_length=256, label="First & Last Name", widget=forms.TextInput(attrs={
        'class':'myInput',
        'placeholder': "E.g. John Anderson"
    }))
    email = forms.CharField(max_length=256, label="Email Address", widget=forms.TextInput(attrs={
        'class':'myInput',
        'placeholder': "E.g. JohnAnderson@mars.co"
    }))
    username = forms.CharField(max_length=256, label="Username", widget=forms.TextInput(attrs={
        'class':'myInput',
        'placeholder': "E.g. johnanderson"
    }))
    password1 = forms.CharField(max_length=256, label="Password", widget=forms.PasswordInput(attrs={
        'class':'myInput',
        'placeholder': "Enter new password"
    }))

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