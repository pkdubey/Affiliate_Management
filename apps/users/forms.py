from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,  # Allow blank when editing without changing password
        help_text='Leave blank if you do not want to change the password.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_active', 'is_staff', 'groups']
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Hash the password properly
        if commit:
            user.save()
            self.save_m2m()
        return user

class RoleForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
