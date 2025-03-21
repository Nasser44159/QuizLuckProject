import os
import sys
import django
from django.db import transaction

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QuizLuck.settings")
django.setup()
from quizapp.models import Question, Choice, Exam


OLD_EXAM_TITLE = "anat2016"
NEW_EXAM_TITLE = "Anatomie2016"

def update_exam_names():
    print(f"🔄 Remplacement de '{OLD_EXAM_TITLE}' par '{NEW_EXAM_TITLE}' dans la base de données...")

    modified = False  # Vérifier si au moins une modification est faite

    with transaction.atomic():
        # Vérifier si l'examen "Anatomie2016" existe, sinon le créer
        exam, created = Exam.objects.get_or_create(name=NEW_EXAM_TITLE)
        if created:
            print(f"✅ Nouvel examen créé : {NEW_EXAM_TITLE}")

        # Mettre à jour toutes les questions
        questions = Question.objects.filter(exam__name=OLD_EXAM_TITLE)
        for question in questions:
            print(f"📝 Mise à jour de la question ID: {question.id} → nouvel exam: {NEW_EXAM_TITLE}")
            question.exam = exam  # Changer l'examen de la question
            question.save()
            modified = True

            # Mettre à jour tous les choix associés à cette question
            choices = Choice.objects.filter(question=question)
            for choice in choices:
                print(f"➡️ Mise à jour du choix ID: {choice.id} → nouvel exam: {NEW_EXAM_TITLE}")
                choice.question = question  # Rattacher le choix à la question mise à jour
                choice.save()
                modified = True

    if not modified:
        print("❌ Aucune modification effectuée (aucune question trouvée avec cet examen).")
    else:
        print("✅ Toutes les questions et choix ont été mis à jour avec succès !")

# Exécuter le script
update_exam_names()
