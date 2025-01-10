from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from django import forms
from .models import User, PERSONALITIES

class ProfileForm(forms.ModelForm):
    default_personality = forms.ChoiceField(
        choices=[(key, key.capitalize()) for key in PERSONALITIES.keys()],
        required=False,
        label="Default Personality"
    )

    class Meta:
        model = User
        fields = ['default_personality']