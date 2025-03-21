import os
import sys
import django
import json
from django.db import transaction

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QuizLuck.settings")
django.setup()

from quizapp.models import Question, Choice

# Chemin du fichier JSON contenant les bonnes réponses
CORRECT_ANSWERS_FILE = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\static\\data\\Anatomie2019_correct_answers.json"
EXAM_TITLE = "Anatomie2019"

def correct_choices():
    """Corrige les choix existants dans la base de données en fonction du fichier JSON des réponses correctes."""

    if not os.path.exists(CORRECT_ANSWERS_FILE):
        print(f"❌ Fichier JSON introuvable : {CORRECT_ANSWERS_FILE}")
        return

    # Charger les réponses correctes depuis le fichier JSON
    with open(CORRECT_ANSWERS_FILE, "r", encoding="utf-8") as f:
        correct_answers = json.load(f)

    with transaction.atomic():
        for question in Question.objects.filter(exam__name=EXAM_TITLE):
            question_number = question.id.split("_")[-1]  # Extraire le numéro de la question
            expected_correct_choices = correct_answers.get(f"q{question_number}", [])

            print(f"\n🔍 Vérification de la question {question.id} - Réponses correctes attendues : {expected_correct_choices}")

            for choice in question.choices.all():
                choice_letter = choice.id.split("_")[-1].lower()  # Extraire la lettre en minuscule
                is_expected_correct = choice_letter in [c.lower() for c in expected_correct_choices]  # Vérification

                if choice.is_correct != is_expected_correct:
                    choice.is_correct = is_expected_correct
                    choice.save()

                print(f"   - {choice.id} : {'✅ Correct' if choice.is_correct else '❌ Incorrect'}")

    print("\n✅ Correction terminée.")

# Exécution du script
correct_choices()
