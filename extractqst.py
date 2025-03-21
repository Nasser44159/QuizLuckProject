import json
import os
import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
django.setup()

from quizapp.models import Choice

def verify_and_update_choices():
    # Chemin du fichier JSON contenant les réponses correctes
    json_file_path = os.path.join('quizapp', 'static', 'data', 'syntOB2023_correct_answers.json')

    # Charger le fichier JSON
    if not os.path.exists(json_file_path):
        print(f"Fichier JSON introuvable : {json_file_path}")
        return

    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        correct_answers = json.load(json_file)

    print("Réponses correctes chargées :")
    print(correct_answers)

    # Parcourir tous les choix de la base de données
    choices_to_check = Choice.objects.filter(id__startswith='OB2023')

    for choice in choices_to_check:
        # Extraire l'ID de la question (exemple : 'OB2023_1_a' -> 'q1')
        question_id = f"q{choice.id.split('_')[1]}"
        choice_letter = choice.id.split('_')[-1].upper()  # Exemple : 'a' -> 'A'

        # Vérifier si la question est dans le JSON
        if question_id in correct_answers:
            # Vérifier si le choix fait partie des réponses correctes
            is_correct = choice_letter in correct_answers[question_id]

            # Mettre à jour la base de données si nécessaire
            if choice.is_correct != is_correct:
                choice.is_correct = is_correct
                choice.save()
                print(f"Choix mis à jour : {choice.id} -> {'Correct' if is_correct else 'Incorrect'}")
            else:
                print(f"Choix déjà correct : {choice.id}")
        else:
            print(f"Question ID {question_id} non trouvée dans le JSON. Choix ignoré : {choice.id}")

if __name__ == "__main__":
    verify_and_update_choices()
