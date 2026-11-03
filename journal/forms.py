from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Lesson
from .access import assignments
class RegisterForm(UserCreationForm):
    class Meta: model=User; fields=['username','first_name','last_name']
class LessonForm(forms.ModelForm):
    class Meta:
        model=Lesson; fields=['assignment','starts_at','topic']
        labels={'assignment':'Группа / дисциплина / преподаватель','starts_at':'Дата и время','topic':'Тема'}
        widgets={'starts_at':forms.DateTimeInput(format='%Y-%m-%dT%H:%M',attrs={'type':'datetime-local'})}
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['assignment'].queryset=assignments(user)
    def clean_assignment(self):
        value=self.cleaned_data['assignment']
        if self.instance.pk and self.instance.marks.exists() and value.pk!=self.instance.assignment_id: raise forms.ValidationError('Назначение занятия с отметками менять нельзя.')
        return value
