from django import forms
from django.contrib.auth.forms import UserCreationForm

from .access import assignments
from .models import Lesson, User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["assignment", "starts_at", "topic"]

        labels = {
            "assignment": "Группа / дисциплина / преподаватель",
            "starts_at": "Дата и время",
            "topic": "Тема",
        }

        widgets = {
            "starts_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)

        # В списке показываем назначения, доступные текущему пользователю.
        self.fields["assignment"].queryset = assignments(user)

        # Каждое поле занимает ширину формы, в том числе на узком экране.
        for field in self.fields.values():
            field.widget.attrs["style"] = "width: 100%; min-width: 0;"

    def clean_assignment(self):
        assignment = self.cleaned_data["assignment"]

        if (
            self.instance.pk
            and self.instance.marks.exists()
            and assignment.pk != self.instance.assignment_id
        ):
            raise forms.ValidationError(
                "Назначение занятия с отметками менять нельзя."
            )

        return assignment