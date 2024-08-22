from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Group
from .models import Invitation

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['user'] 

class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User to Add")


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
