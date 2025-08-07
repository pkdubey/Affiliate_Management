from django import forms
from django.contrib.auth.models import User, Group

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff', 'groups']
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
