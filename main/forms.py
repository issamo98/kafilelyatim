from django import forms
from .models import Student, StudyLevel, EnrolledClass
from django.forms import modelformset_factory


class StudentForm(forms.ModelForm):
    levels = forms.ModelMultipleChoiceField(
        queryset=StudyLevel.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Student
        fields = ['full_name', 'parents_name', 'parents_number', 'date_of_birth', 'levels', 'sub_payed', 'sub_montant', 'is_orphan']


class EnrolledClassForm(forms.ModelForm):
    class Meta:
        model = EnrolledClass
        fields = ['enrolled_class', 'monthly_fee']


# forms.py

from django import forms
from .models import Attendance, StudyLevel, Class

class AttendanceForm(forms.Form):
    student = forms.IntegerField(widget=forms.HiddenInput())
    status = forms.ChoiceField(choices=Attendance.STATUS_CHOICES, widget=forms.Select())

class AttendanceFilterForm(forms.Form):
    level = forms.ModelChoiceField(queryset=StudyLevel.objects.all())
    class_field = forms.ModelChoiceField(queryset=Class.objects.all(), label="Class")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


from .models import StudyLevel, Class, Teacher

class StudyLevelForm(forms.ModelForm):
    class Meta:
        model = StudyLevel
        fields = ['level', 'specialty', 'school']
        labels = {
            'level': 'Study Level',
            'specialty': 'Speciality',
            'school': 'School',
        }
        widgets = {
            'level': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter study level (e.g., Primary, Secondary)'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
        }


class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'level', 'teacher']
        labels = {
            'name': 'Class Name',
            'level': 'Study Level',
            'teacher': 'Teacher',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter A class'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter the Teacher FOR THIS CLASS'})
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['full_name', 'phone', 'email']
        labels = {
            'full_name': 'Full Name',
            'phone': 'Phone Number',
            'email': 'Email Address',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
        }