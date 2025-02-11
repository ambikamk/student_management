from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import LeaveReportStaff,Staff,LeaveRequest,NotificationStaffs

class LeaveReportStaffForm(forms.ModelForm):
    def _init_(self, *args, **kwargs):
        super(LeaveReportStaffForm, self)._init_(*args, **kwargs)
        # Customizing field attributes (e.g., adding CSS classes)
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter the reason for leave'})

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'date': 'Leave Date',
            'message': 'Reason for Leave',
        }

    def clean_date(self):
        # Example validation for the date field
        date = self.cleaned_data.get('date')
        if date is None:
            raise forms.ValidationError("Date is required.")
        return date
# forms.py


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['date', 'message']
    date = forms.DateField(widget=forms.SelectDateWidget())
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    

class NotificationForm(forms.ModelForm):
    class Meta:
        model = NotificationStaffs
        fields = ['staff_id', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'staff_id': forms.Select(attrs={'class': 'form-control'}),
}

class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['full_name', 'email', 'phone', 'address']  



# Custom Password Change Form (optional, if you want to customize it)
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

