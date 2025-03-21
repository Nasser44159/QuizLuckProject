import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
django.setup()

from quizapp.models import UncorrectedQuestion, UncorrectedChoice, Exam

def classify_questions_and_choices_by_exam():
    # Récupérer toutes les questions non corrigées
    questions = UncorrectedQuestion.objects.all()

    print(f"Nombre total de questions non corrigées : {questions.count()}")

    for question in questions:
        try:
            # Extraire le nom de l'examen depuis l'ID de la question
            exam_name = question.id.split("_")[0]  # Extrait la partie avant le premier "_"
            print(f"Traitement de la question {question.id}, associée à l'examen {exam_name}")

            # Récupérer ou créer l'examen
            exam, created = Exam.objects.get_or_create(
                name=exam_name,
                defaults={"semester": "S1", "module": "Anatomie_1"}  # Ajustez ces valeurs par défaut si nécessaire
            )
            if created:
                print(f"Examen créé : {exam_name}")
            else:
                print(f"Examen existant : {exam_name}")

            # Mettre à jour l'examen de la question
            question.exam = exam
            question.save()
            print(f"Question {question.id} associée à l'examen {exam_name}")

        except Exception as e:
            print(f"Erreur lors du traitement de la question {question.id} : {e}")

    print("Classification des questions terminée avec succès.")

if __name__ == "__main__":
    classify_questions_and_choices_by_exam()
