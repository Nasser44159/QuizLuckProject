
import os
import sys
import django
import json
from bs4 import BeautifulSoup
from django.db import transaction

# Configuration du projet Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QuizLuck.settings")  # Assurez-vous que c'est le bon nom

django.setup()

# Importer après la configuration Django
from quizapp.models import Question, Choice, Exam

# Définir le chemin spécifique du fichier à traiter
SPECIFIC_HTML_FILE = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\templates\\S1\\Anatomie_1\\syntanat2016.html"
JSON_DIR = "quizapp/static/data"

def process_specific_file():
    print(f"Traitement du fichier : {SPECIFIC_HTML_FILE}")

    # Vérifier si le fichier existe
    if not os.path.exists(SPECIFIC_HTML_FILE):
        print(f"Fichier introuvable : {SPECIFIC_HTML_FILE}")
        return

    # Extraire le titre de l'examen en retirant "synt" du nom du fichier
    file_name = os.path.basename(SPECIFIC_HTML_FILE)  # Récupérer le nom du fichier
    exam_title = file_name.replace("syntanat", "Anatomie").replace(".html", "").strip()  # Supprimer "synt" et ".html"

    print(f"Examen détecté : {exam_title}")

    # Vérifier si l'examen existe
    if not Exam.objects.filter(name=exam_title).exists():
        print(f"Examen '{exam_title}' non trouvé dans la base de données. Ignoré.")
        return

    # Vérifier si le fichier a déjà été traité
    if Question.objects.filter(id__startswith=exam_title).exists():
        print(f"Questions pour l'examen '{exam_title}' déjà existantes. Fichier ignoré.")
        return

    # Extraire les questions depuis le fichier HTML
    questions = extract_questions_from_html(SPECIFIC_HTML_FILE, exam_title)
    if not questions:
        print(f"Aucune question valide trouvée dans le fichier : {SPECIFIC_HTML_FILE}")
        return

    # Trouver le fichier JSON correspondant
    json_file = find_json_file(exam_title)
    corrections = load_corrections_from_json(json_file)

    # Insérer les données en base de données
    store_questions_in_db(exam_title, questions, corrections)

    print(f"Questions sauvegardées pour l'examen : {exam_title}")

    # Afficher le résumé de la base de données
    summarize_database()


# Extraction des questions depuis un fichier HTML
def extract_questions_from_html(file_path, exam_title):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    questions = []
    ignored_questions = []

    question_counter = 0  # Pour générer un ID unique pour chaque question

    for question_container in soup.find_all("div", class_="question-container"):
        question_counter += 1
        question_id = f"{exam_title}_{question_counter}"  # ID unique basé sur l'examen et le numéro de la question

        # Vérifier la présence d'une balise <p>
        question_text_tag = question_container.find("p")
        if not question_text_tag:
            print(f"Question ignorée (pas de balise <p>) : {question_id}")
            ignored_questions.append(question_id)
            continue

        question_text = question_text_tag.text.strip()  # Le texte de la question
        choices = []

        for li in question_container.find_all("li"):
            input_tag = li.find("input")
            choice_value = input_tag.get("value")  # Exemple : "A", "B", etc.
            choice_text = li.text.strip()

            choice_id = f"{question_id}_{choice_value.lower()}"  # ID unique pour chaque choix

            choices.append({
                "id": choice_id,
                "value": choice_value,
                "text": choice_text
            })

        questions.append({
            "question_id": question_id,
            "text": question_text,
            "choices": choices
        })

    if ignored_questions:
        print(f"Questions ignorées (sans balise <p>) : {', '.join(ignored_questions)}")

    return questions


# Trouver le fichier JSON correspondant
def find_json_file(exam_title):
    json_file_name = f"{exam_title}_correct_answers.json"
    json_path = os.path.join(JSON_DIR, json_file_name)

    if os.path.exists(json_path):
        return json_path

    print(f"Fichier JSON {json_file_name} non trouvé.")
    return None


# Charger les corrections depuis le fichier JSON
def load_corrections_from_json(json_file):
    if not json_file:
        print("Fichier JSON non trouvé ou vide.")
        return {}

    with open(json_file, "r", encoding="utf-8") as file:
        corrections = json.load(file)

    return corrections


# Insérer les données en base de données
@transaction.atomic
def store_questions_in_db(exam_title, questions, corrections):
    exam = Exam.objects.get(name=exam_title)

    for question_data in questions:
        if Question.objects.filter(id=question_data["question_id"]).exists():
            print(f"Question '{question_data['question_id']}' déjà existante. Ignorée.")
            continue

        question = Question.objects.create(
            id=question_data["question_id"],  # ID personnalisé
            exam=exam,
            text=question_data["text"]
        )

        for choice_data in question_data["choices"]:
            is_correct = False

            # Vérifier si cette réponse est correcte à partir du fichier JSON
            json_question_id = f"q{int(question_data['question_id'].split('_')[-1])}"
            question_correction = corrections.get(json_question_id, [])
            if question_correction:
                is_correct = choice_data["value"] in question_correction

            Choice.objects.create(
                id=choice_data["id"],
                question=question,
                text=choice_data["text"],
                is_correct=is_correct
            )

            print(f"Créé choix: {choice_data['id']} (correct: {is_correct})")


# Résumé de la base de données
def summarize_database():
    exams = Exam.objects.all()
    print(f"Nombre total d'examens dans la base de données : {exams.count()}")
    for exam in exams:
        question_count = exam.questions.count()
        print(f"- {exam.name} : {question_count} questions")


# Exécution du traitement pour le fichier spécifique
process_specific_file()
