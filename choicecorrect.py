import django
import os

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
django.setup()

from quizapp.models import Question, Choice, Exam

def classify_questions_and_choices():
    print("Classification des questions et des choix par examen...")

    # Récupérer toutes les questions
    questions = Question.objects.all()
    for question in questions:
        try:
            # Extraire le nom de l'examen à partir de l'ID de la question
            exam_name = question.id.split('_')[0]
            exam, created = Exam.objects.get_or_create(name=exam_name)

            # Associer l'examen à la question
            question.exam = exam
            question.save()

            if created:
                print(f"Examen créé : {exam_name}")
            print(f"Question mise à jour : {question.id} associée à l'examen {exam_name}")

        except Exception as e:
            print(f"Erreur lors de la classification de la question {question.id} : {e}")

    # Récupérer tous les choix
    choices = Choice.objects.all()
    for choice in choices:
        try:
            # Associer le choix à la question correspondante
            question_id = '_'.join(choice.id.split('_')[:-1])  # Retirer la partie _a, _b, etc.
            question = Question.objects.filter(id=question_id).first()

            if question:
                choice.question = question
                choice.save()
                print(f"Choix mis à jour : {choice.id} associé à la question {question.id}")
            else:
                print(f"Question introuvable pour le choix {choice.id}")

        except Exception as e:
            print(f"Erreur lors de la classification du choix {choice.id} : {e}")

if __name__ == '__main__':
    classify_questions_and_choices()