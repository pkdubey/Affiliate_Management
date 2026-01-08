from django import forms
from .models import DailyRevenueSheet
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class DailyRevenueSheetForm(forms.ModelForm):
    # Add account_manager as a ChoiceField at the class level
    account_manager = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select', 
            'id': 'id_account_manager',
            'placeholder': 'Select Account Manager'
        }),
        label='Account Manager'
    )
    
    # Add MMP as a ChoiceField at the class level
    mmp = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select', 
            'id': 'id_mmp'
        }),
        label='MMP'
    )
    
    class Meta:
        model = DailyRevenueSheet
        fields = [
            'account_manager', 'start_date', 'campaign_name',
            'status', 'end_date',
            'advertiser', 'geo', 'mmp', 'campaign_revenue', 'advertiser_conversions',
            'publisher', 'pid', 'af_prt', 'payable_event_name', 'publisher_payout', 
            'publisher_conversions',
        ]
        
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'id': 'id_start_date'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'id': 'id_end_date'
            }),
            'campaign_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Campaign Name', 
                'id': 'id_campaign_name'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_status'
            }),
            'advertiser': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_advertiser'
            }),
            'geo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., US, IN, UK', 
                'id': 'id_geo'
            }),
            # REMOVE 'mmp' from here since we defined it as ChoiceField above
            'campaign_revenue': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'id': 'id_campaign_revenue'
            }),
            'advertiser_conversions': forms.NumberInput(attrs={
                'class': 'form-control', 
                'id': 'id_advertiser_conversions'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_publisher'
            }),
            'pid': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Publisher ID', 
                'id': 'id_pid'
            }),
            'af_prt': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'AF/PRT', 
                'id': 'id_af_prt'
            }),
            'payable_event_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Event Name for Payout', 
                'id': 'id_payable_event_name'
            }),
            'publisher_payout': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'id': 'id_publisher_payout'
            }),
            'publisher_conversions': forms.NumberInput(attrs={
                'class': 'form-control', 
                'id': 'id_publisher_conversions'
            }),
        }
        
        labels = {
            'campaign_revenue': 'Campaign Revenue ($)',
            'publisher_payout': 'Campaign Payout ($)',
            'af_prt': 'AF_PRT',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Get all users for account manager dropdown
        all_users = User.objects.all().order_by('username')
        
        # Build account manager choices
        account_manager_choices = [('', '---------')]
        
        for user_obj in all_users:
            # Create display name
            display_name = user_obj.username
            if hasattr(user_obj, 'get_full_name') and user_obj.get_full_name():
                display_name = f"{user_obj.username} - {user_obj.get_full_name()}"
            
            # Add role if available
            if hasattr(user_obj, 'get_role_display'):
                role_display = user_obj.get_role_display()
                display_name = f"{display_name} ({role_display})"
            
            account_manager_choices.append((user_obj.username, display_name))
        
        # Also add any existing account managers from DRS entries
        existing_managers = DailyRevenueSheet.objects.exclude(
            Q(account_manager__isnull=True) | Q(account_manager='')
        ).values_list('account_manager', flat=True).distinct()
        
        for manager in existing_managers:
            if not any(manager == choice[0] for choice in account_manager_choices):
                account_manager_choices.append((manager, manager))
        
        # Set the choices for account_manager field
        self.fields['account_manager'].choices = account_manager_choices
        
        # Set MMP choices - IMPORTANT: This is the fix
        mmp_choices = [
            ('', '---------'),
            ('Appsflyer', 'Appsflyer'),
            ('Adjust', 'Adjust'),
            ('Singular', 'Singular'),
            ('Branch', 'Branch'),
            ('AppMetrica', 'AppMetrica'),
            ('Other', 'Other')
        ]
        
        # Set MMP choices for the ChoiceField
        self.fields['mmp'].choices = mmp_choices
        
        # If we're editing an existing instance, ensure the current value is in choices
        if self.instance and self.instance.pk and self.instance.mmp:
            current_mmp = self.instance.mmp
            # Check if current value is in choices, if not add it
            if not any(current_mmp == choice[0] for choice in mmp_choices):
                mmp_choices.append((current_mmp, current_mmp))
                self.fields['mmp'].choices = mmp_choices
        
        # Set status choices - include all status options
        self.fields['status'].choices = [
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('paid', 'Paid'),
        ]
        
        # Set initial AF_PRT label
        self.fields['af_prt'].label = 'AF_PRT'
        
        # Debug logging
        print(f"DEBUG: MMP Choices: {len(self.fields['mmp'].choices)} options")
        for i, choice in enumerate(self.fields['mmp'].choices):
            print(f"  {i}. {choice}")
        
        # Debug current instance value
        if self.instance and self.instance.pk:
            print(f"DEBUG: Current instance MMP value: {self.instance.mmp}")
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Get status from form data
        status = cleaned_data.get('status')
        end_date = cleaned_data.get('end_date')
        
        # If end date is set and status is active, auto-update to paused
        if end_date and status == 'active':
            cleaned_data['status'] = 'paused'
            # Add a message to inform user
            self.add_error(None, 'Status has been automatically changed to "Paused" because an end date was set.')
        
        # If status is active and end date exists, ask user to clear end date
        elif status == 'active' and end_date:
            # We'll let it pass but add a warning
            self.add_error(None, 'Warning: Active campaigns typically don\'t have end dates.')
        
        return cleaned_data
    # Add account_manager as a ChoiceField at the class level
    account_manager = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select', 
            'id': 'id_account_manager',
            'placeholder': 'Select Account Manager'
        }),
        label='Account Manager'
    )
    
    class Meta:
        model = DailyRevenueSheet
        fields = [
            'account_manager', 'start_date', 'campaign_name',
            'status', 'end_date',
            'advertiser', 'geo', 'mmp', 'campaign_revenue', 'advertiser_conversions',
            'publisher', 'pid', 'af_prt', 'payable_event_name', 'publisher_payout', 
            'publisher_conversions',
        ]
        
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'id': 'id_start_date'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'id': 'id_end_date'
            }),
            'campaign_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Campaign Name', 
                'id': 'id_campaign_name'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_status'
            }),
            'advertiser': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_advertiser'
            }),
            'geo': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., US, IN, UK', 
                'id': 'id_geo'
            }),
            'mmp': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_mmp'
            }),
            'campaign_revenue': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'id': 'id_campaign_revenue'
            }),
            'advertiser_conversions': forms.NumberInput(attrs={
                'class': 'form-control', 
                'id': 'id_advertiser_conversions'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_publisher'
            }),
            'pid': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Publisher ID', 
                'id': 'id_pid'
            }),
            'af_prt': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'AF/PRT', 
                'id': 'id_af_prt'
            }),
            'payable_event_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Event Name for Payout', 
                'id': 'id_payable_event_name'
            }),
            'publisher_payout': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'id': 'id_publisher_payout'
            }),
            'publisher_conversions': forms.NumberInput(attrs={
                'class': 'form-control', 
                'id': 'id_publisher_conversions'
            }),
        }
        
        labels = {
            'campaign_revenue': 'Campaign Revenue ($)',
            'publisher_payout': 'Campaign Payout ($)',
            'af_prt': 'AF_PRT',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Get all users for account manager dropdown
        all_users = User.objects.all().order_by('username')
        
        # Build account manager choices
        account_manager_choices = [('', '---------')]
        
        for user_obj in all_users:
            # Create display name
            display_name = user_obj.username
            if hasattr(user_obj, 'get_full_name') and user_obj.get_full_name():
                display_name = f"{user_obj.username} - {user_obj.get_full_name()}"
            
            # Add role if available
            if hasattr(user_obj, 'get_role_display'):
                role_display = user_obj.get_role_display()
                display_name = f"{display_name} ({role_display})"
            
            account_manager_choices.append((user_obj.username, display_name))
        
        # Also add any existing account managers from DRS entries
        # (in case they're not in the User model anymore)
        existing_managers = DailyRevenueSheet.objects.exclude(
            Q(account_manager__isnull=True) | Q(account_manager='')
        ).values_list('account_manager', flat=True).distinct()
        
        for manager in existing_managers:
            # Check if this manager is already in choices
            if not any(manager == choice[0] for choice in account_manager_choices):
                account_manager_choices.append((manager, manager))
        
        # Set the choices for account_manager field
        self.fields['account_manager'].choices = account_manager_choices
        
        # Set MMP choices
        self.fields['mmp'].choices = [
            ('', '---------'),
            ('Appsflyer', 'Appsflyer'),
            ('Adjust', 'Adjust'),
            ('Singular', 'Singular'),
            ('Branch', 'Branch'),
            ('AppMetrica', 'AppMetrica'),
            ('Other', 'Other')
        ]
        
        # Ensure MMP field is NOT readonly
        self.fields['mmp'].widget.attrs.pop('readonly', None)
        self.fields['mmp'].widget.attrs.pop('disabled', None)
        self.fields['mmp'].widget.attrs['style'] = ''
        
        # Set status choices - include all status options
        self.fields['status'].choices = [
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('paid', 'Paid'),
        ]
        
        # Set initial AF_PRT label
        self.fields['af_prt'].label = 'AF_PRT'
        
        # DEBUG: Remove readonly attribute - this was preventing updates
        # self.fields['status'].widget.attrs['readonly'] = True  # REMOVE THIS LINE
        # self.fields['status'].widget.attrs['style'] = 'background-color: #f8f9fa;'  # REMOVE THIS LINE
        
        # Debug: Print available choices
        print(f"DEBUG: Account Manager Choices: {len(account_manager_choices)} options")
        for i, choice in enumerate(account_manager_choices[:10]):  # Show first 10
            print(f"  {i}. {choice}")
        if len(account_manager_choices) > 10:
            print(f"  ... and {len(account_manager_choices) - 10} more")
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Get status from form data
        status = cleaned_data.get('status')
        end_date = cleaned_data.get('end_date')
        
        # If end date is set and status is active, auto-update to paused
        if end_date and status == 'active':
            cleaned_data['status'] = 'paused'
            # Add a message to inform user
            self.add_error(None, 'Status has been automatically changed to "Paused" because an end date was set.')
        
        # If status is active and end date exists, ask user to clear end date
        elif status == 'active' and end_date:
            # We'll let it pass but add a warning
            self.add_error(None, 'Warning: Active campaigns typically don\'t have end dates.')
        
        return cleaned_data