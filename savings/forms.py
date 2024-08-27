from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Group
from .models import Invitation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Contribution, User, Group


class InvitationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InvitationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('user', css_class='form-control')
        )
        self.helper.add_input(Submit('submit', 'Send Invitation', css_class='btn btn-primary'))

    class Meta:
        model = Invitation
        fields = ['user']

class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User to Add")

    def __init__(self, *args, **kwargs):
        super(AddMemberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('user', css_class='form-control')
        )
        self.helper.add_input(Submit('submit', 'Add Member', css_class='btn btn-primary'))


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('password1', css_class='form-control'),
            Field('password2', css_class='form-control'),
        )
        self.helper.add_input(Submit('submit', 'Register', css_class='btn btn-primary'))

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
    def __init__(self, *args, **kwargs):
        super(GroupCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control'),
        )
        self.helper.add_input(Submit('submit', 'Create Group', css_class='btn btn-primary'))

    class Meta:
        model = Group
        fields = ['name', 'description']

class ContributionForm(forms.ModelForm):
    member = forms.ModelChoiceField(queryset=User.objects.all(), label="Member")

    class Meta:
        model = Contribution
        fields = ['member', 'amount']

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super(ContributionForm, self).__init__(*args, **kwargs)
        if group:
             self.fields['member'].queryset = group.members.all() | User.objects.filter(id=group.manager.id)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('member', css_class='form-control'),
            Field('amount', css_class='form-control'),
        )
        self.helper.add_input(Submit('submit', 'Add Contribution', css_class='btn btn-primary'))