from django import forms
from .models import LeaveReportStudent, SessionYearModel,Student, Subject

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

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['full_name', 'email', 'phone', 'address', 'session_year_id', 'course']  # Add other fields you want to allow for update

from django.contrib.auth.forms import PasswordChangeForm

# Custom Password Change Form (optional, if you want to customize it)
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


from django import forms
from .models import StudyMaterial

class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'subject', 'session_year', 'file']

class StudyMaterialFilterForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), empty_label="Select Subject")
    session_year = forms.ModelChoiceField(queryset=SessionYearModel.objects.all(), empty_label="Select Session Year")