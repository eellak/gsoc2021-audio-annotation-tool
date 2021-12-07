from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm
from django import forms
from .models import User


class ExtendedLogInForm(LoginForm):

    """
    An extended Log In form from Djano-allauth for adding custom styling.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs = {'class': 'myInput form-control', 'placeholder': "Email or Username", 'autocomplete': "email"}
        self.fields["password"].widget.attrs = {'class': 'myInput form-control', 'placeholder': "Password", 'autocomplete': "current-password"}


class ExtendedSignUpForm(SignupForm):

    """
    An extended Sign up form from Djano-allauth for adding custom styling.
    """

    name = forms.CharField(max_length=256)
    ordered_field_names = ['name', 'email', 'username', 'password1']

    def __init__(self, *args, **kwargs):
        # Call the init of the parent class
        super().__init__(*args, **kwargs)

        self.fields["name"].widget.attrs = {'class': 'myInput form-control', 'placeholder': 'E.g. "John Anderson"', 'autocomplete': "name"}
        self.fields["name"].label = "First & Last Name"

        self.fields["email"].widget.attrs = {'class': 'myInput form-control', 'placeholder': "E.g. JohnAnderson@mars.co", 'autocomplete': "email"}
        self.fields["email"].label = "Email Address*"

        self.fields["username"].widget.attrs = {'class': 'myInput form-control', 'placeholder': "E.g. johnanderson", 'autocomplete': "username"}
        self.fields["username"].label = "Username*"

        self.fields["password1"].widget.attrs = {'class': 'myInput form-control', 'placeholder': "Enter new password", 'autocomplete': "new-password"}
        self.fields["password1"].label = "Password*"
        self.rearrange_field_order()

        # Push error class if an error has occured
        for field in self:
            if field.errors:
                self.fields[field.name].widget.attrs["class"] += " error"

    def save(self, request):

        """
        Modify save method to save the name given by the user.
        """

        user = super(ExtendedSignUpForm, self).save(request)
        user.name = self.cleaned_data["name"]
        user.save()
        return user

    def rearrange_field_order(self):

        """
        Change the order that the fields are displayed in the Sign up page.
        """

        original_fields = self.fields
        new_fields = {}

        for field_name in self.ordered_field_names:
            field = original_fields.get(field_name)
            if field:
                new_fields[field_name] = field

        self.fields = new_fields


class ExtendedResetPasswordForm(ResetPasswordForm):

    """
    An extended Reset password form from Djano-allauth for adding custom styling.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs = {'class': 'myInput form-control', 'placeholder': "JohnAnderson@mars.co", 'autocomplete': "email"}
        self.fields["email"].label = "Email*"


class UserForm(forms.ModelForm):

    """
    User form for edit profile page.
    """

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

        """
        Ensure that uploaded avatar is less than 2mb.
        """

        image = self.cleaned_data.get("avatar", False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2mb )")
            return image
        else:
            raise forms.ValidationError("Please provide a logo")

    def clean_email(self):

        """
        User is not able to modify the email field in the edit profile page.
        """

        # When a field is cleaned, we always return the existing model field
        return self.instance.email
