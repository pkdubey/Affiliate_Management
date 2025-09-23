# apps/users/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.text import slugify

User = get_user_model()


class UserForm(forms.ModelForm):
    # Bootstrap-styled inputs
    full_name = forms.CharField(
        label="Full Name",
        widget=forms.TextInput(attrs={"class": "form-control",
                                      "placeholder": "Full Name"})
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control",
                                      "placeholder": "Username"})
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={"class": "form-control",
                                       "placeholder": "Email Address"})
    )

    # show Password **before** Role
    password = forms.CharField(
        label="Password",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control",
                                          "placeholder": "Password"}),
        help_text=""
    )

    groups = forms.ModelChoiceField(
        label="Role",
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    publishers = forms.ModelMultipleChoiceField(
        label="Assign Publishers (optional)",
        queryset=User._meta.get_field("publishers").remote_field.model.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select",
                                           "data-placeholder": "0 selected"}),
        help_text=("If no advertisers or publishers are assigned, "
                   "the user will have access to all of them.")
    )

    advertisers = forms.ModelMultipleChoiceField(
        label="Assign Advertisers (optional)",
        queryset=User._meta.get_field("advertisers").remote_field.model.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select",
                                           "data-placeholder": "0 selected"}),
        help_text=""
    )

    class Meta:
        model = User
        # groups handled manually, so omit
        fields = [
            "full_name",
            "username",
            "email",
            "password",     # password now comes before role
            "publishers",
            "advertisers",
        ]

    # enforce display order: email → password → role
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["full_name"].initial = (
                f"{self.instance.first_name} {self.instance.last_name}".strip()
            )

        # explicit field order for rendering
        self.order_fields([
            "full_name",
            "username",
            "email",
            "password",     # password first
            "groups",       # then role
            "publishers",
            "advertisers",
        ])

    def save(self, commit=True):
        user = super().save(commit=False)

        # split Full Name
        name = self.cleaned_data.get("full_name", "").strip()
        first, *last = name.split(" ", 1)
        user.first_name = first
        user.last_name  = last[0] if last else ""

        # ensure username
        uname = self.cleaned_data.get("username") or user.username
        if not uname:
            uname = slugify(self.cleaned_data["email"].split("@")[0])
        user.username = uname

        # optional password hashing
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)

        # defaults for brand-new users
        if not user.pk:
            user.is_active = True
            user.is_staff  = True   # staff by default

        if commit:
            user.save()

            # single selected role
            group = self.cleaned_data["groups"]
            user.groups.set([group] if group else [])

            # remaining M2M fields
            self.save_m2m()

        return user


class RoleForm(forms.ModelForm):
    class Meta:
        model  = Group
        fields = ["name"]
