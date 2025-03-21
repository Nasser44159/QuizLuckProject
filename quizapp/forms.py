from django import forms
from .models import Choice, Exam, Question

class ChoiceAdminForm(forms.ModelForm):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        required=False,
        label="Exam",
        help_text="Choisissez un examen pour filtrer les questions."
    )

    class Meta:
        model = Choice
        fields = ['id', 'exam', 'question', 'text', 'is_correct', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question'].queryset = Question.objects.none()

        if 'exam' in self.data:
            try:
                exam_id = self.data.get('exam')
                self.fields['question'].queryset = Question.objects.filter(exam__id=exam_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.question:
            self.fields['question'].queryset = Question.objects.filter(exam=self.instance.question.exam)
