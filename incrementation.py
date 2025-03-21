import os
import sys
import django
from django.db import transaction

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QuizLuck.settings")
django.setup()
from quizapp.models import Choice, Question


EXAM_TITLE = "anat2016"  # Préfixe des questions
CHOICE_PREFIX = "Anatomie2016"  # Préfixe des choix
THRESHOLD = 19  # Ne pas modifier les IDs inférieurs ou égaux à ce chiffre

def correct_choice_ids():
    print(f"Correction des IDs des choix pour l'examen : {EXAM_TITLE}")

    modified = False  # Vérifier si au moins une modification est faite

    with transaction.atomic():
        # Modifier les IDs des choix
        choices = Choice.objects.filter(id__startswith=CHOICE_PREFIX).order_by("-id")  # Trier par ID décroissant
        for choice in choices:
            parts = choice.id.split("_")
            
            if len(parts) == 3 and parts[0] == CHOICE_PREFIX:
                try:
                    num = int(parts[1])
                    if num > THRESHOLD:
                        new_num = num + 1
                        choice_value = parts[2]  # Lettre du choix (a, b, c, ...)
                        new_id = f"{CHOICE_PREFIX}_{new_num}_{choice_value}"

                        # Récupérer la nouvelle question associée
                        old_question_id = f"{EXAM_TITLE}_{num}"
                        new_question_id = f"{EXAM_TITLE}_{new_num}"

                        try:
                            new_question = Question.objects.get(id=new_question_id)
                            choice.question = new_question  # Mise à jour de la relation Question-Choice
                        except Question.DoesNotExist:
                            print(f"⚠️ Question {new_question_id} introuvable. Choix ignoré : {choice.id}")
                            continue  # Passer au choix suivant

                        print(f"Modification Choix: {choice.id} → {new_id}")
                        choice.id = new_id
                        choice.save()
                        modified = True
                except ValueError:
                    print(f"ID non modifié (format incorrect) : {choice.id}")

    if not modified:
        print("Aucune modification effectuée.")

    print("Correction des choix terminée avec succès !")


# Exécuter le script
correct_choice_ids()
