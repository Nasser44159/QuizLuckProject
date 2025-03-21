import os
import sys
import django
import json
from bs4 import BeautifulSoup
from django.db import transaction

# Configuration de Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QuizLuck.settings")
django.setup()
from quizapp.models import Choice, Question

# Fichiers sources
HTML_FILE_PATH = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\templates\\S1\\Anatomie_1\\Anatomie2016.html"
JSON_FILE_PATH = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\static\\data\\Anatomie2016_correct_answers.json"

# Plage des questions à traiter
QUESTION_START = 21
QUESTION_END = 50

def load_correct_answers():
    """Charge les réponses correctes depuis le fichier JSON."""
    if not os.path.exists(JSON_FILE_PATH):
        print(f"❌ Fichier JSON introuvable : {JSON_FILE_PATH}")
        return {}

    with open(JSON_FILE_PATH, "r", encoding="utf-8") as json_file:
        correct_answers = json.load(json_file)

    return correct_answers

def extract_choices_from_html():
    """Extrait les choix des questions 21 à 50 depuis le fichier HTML."""
    if not os.path.exists(HTML_FILE_PATH):
        print(f"❌ Fichier HTML introuvable : {HTML_FILE_PATH}")
        return []

    with open(HTML_FILE_PATH, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    choices_data = []
    for question_num in range(QUESTION_START, QUESTION_END + 1):
        question_id = f"Anatomie2016_{question_num}"  # ID attendu en base
        html_question_id = f"q{question_num}"  # ID dans le fichier HTML

        question_container = soup.find("input", {"name": html_question_id})  # Trouver la bonne question
        if not question_container:
            print(f"⚠️ Question {question_id} introuvable dans le fichier HTML.")
            continue

        # Trouver les choix sous forme de liste
        choice_elements = question_container.find_parent("ul").find_all("li") if question_container.find_parent("ul") else []
        if not choice_elements:
            print(f"⚠️ Aucun choix trouvé pour la question {question_id}.")
            continue

        for li in choice_elements:
            input_tag = li.find("input")
            if not input_tag:
                continue

            choice_value = input_tag.get("value")  # Exemple : "A", "B", etc.
            choice_text = li.text.strip()

            choices_data.append({
                "question_id": question_id,
                "choice_id": f"Anatomie2016_{question_num}_{choice_value.lower()}",
                "choice_text": choice_text,
                "choice_value": choice_value
            })

    return choices_data

@transaction.atomic
def insert_choices_into_db(choices_data, correct_answers):
    """Insère les choix en base de données en les reliant aux questions existantes."""
    for choice_data in choices_data:
        question_id = choice_data["question_id"]
        choice_id = choice_data["choice_id"]
        choice_text = choice_data["choice_text"]
        choice_value = choice_data["choice_value"]

        # Vérifier si la question existe en base
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            print(f"⚠️ Question {question_id} introuvable en base. Choix ignoré : {choice_text}")
            continue

        # Déterminer si le choix est correct en fonction du JSON
        json_question_id = f"q{int(question_id.split('_')[-1])}"  # Convertir en format JSON
        is_correct = choice_value in correct_answers.get(json_question_id, [])

        # Vérifier si le choix existe déjà
        if Choice.objects.filter(id=choice_id).exists():
            print(f"⚠️ Choix {choice_id} déjà existant. Ignoré.")
            continue

        # Insérer le choix en base
        Choice.objects.create(
            id=choice_id,
            question=question,
            text=choice_text,
            is_correct=is_correct
        )

        print(f"✅ Choix ajouté : {choice_id} ({'Correct' if is_correct else 'Incorrect'})")

def main():
    print(f"🔄 Extraction des choix pour les questions {QUESTION_START} à {QUESTION_END}...")

    # Charger les réponses correctes
    correct_answers = load_correct_answers()
    if not correct_answers:
        print("❌ Impossible de charger les réponses correctes. Arrêt du script.")
        return

    # Extraire les choix depuis le fichier HTML
    choices_data = extract_choices_from_html()
    if not choices_data:
        print("❌ Aucun choix trouvé dans le fichier HTML. Arrêt du script.")
        return

    # Insérer les choix en base de données
    insert_choices_into_db(choices_data, correct_answers)

    print("✅ Tous les choix ont été enregistrés avec succès !")

# Exécuter le script
main()
