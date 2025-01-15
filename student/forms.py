from django import forms
from .models import LeaveReportStudent

class LeaveReportStudentForm(forms.ModelForm):
    def _init_(self, *args, **kwargs):
        super(LeaveReportStudentForm, self)._init_(*args, **kwargs)
        # Customizing field attributes (e.g., adding CSS classes)
        self.fields['date'].widget.attrs.update({'class': 'form-control'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter the reason for leave'})

    class Meta:
        model = LeaveReportStudent
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
from django import forms
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['date', 'message']
    date = forms.DateField(widget=forms.SelectDateWidget())
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

from django import forms
from .models import NotificationStudent

class NotificationForm(forms.ModelForm):
    class Meta:
        model = NotificationStudent
        fields = ['student_id', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'student_id': forms.Select(attrs={'class': 'form-control'}),
        }