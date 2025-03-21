import os
import sys
import django
import json
from bs4 import BeautifulSoup
from django.db import transaction

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "QuizLuck.settings")
django.setup()

from quizapp.models import Question, Exam, Choice

# Chemins des fichiers
HTML_FILE_PATH = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\templates\\S1\\Anatomie_1\\anatomie2019.html"
CORRECT_ANSWERS_FILE = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\static\\data\\Anatomie2019_correct_answers.json"
EXAM_TITLE = "Anatomie2019"

def process_questions():
    """Traite le fichier HTML et insère les questions et choix dans la base de données."""
    
    if not os.path.exists(HTML_FILE_PATH):
        print(f"❌ Fichier introuvable : {HTML_FILE_PATH}")
        return

    exam, _ = Exam.objects.get_or_create(name=EXAM_TITLE)

    with open(CORRECT_ANSWERS_FILE, "r", encoding="utf-8") as f:
        correct_answers = json.load(f)

    questions = extract_questions_from_html(HTML_FILE_PATH, exam, correct_answers)
    if not questions:
        print("❌ Aucune question valide trouvée.")
        return

    store_questions_in_db(exam, questions)

def extract_questions_from_html(file_path, exam, correct_answers):
    """Extrait les questions et choix depuis le fichier HTML."""
    
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    questions = []
    question_counter = 0

    for question_container in soup.find_all("div", class_="question-container"):
        question_counter += 1
        question_id = f"{exam.name}_{question_counter}"

        # Extraction du texte de la question
        question_text_tag = question_container.find("div", class_="question").find("p")
        if not question_text_tag:
            continue

        question_text = question_text_tag.text.strip()

        # Extraction des choix
        choices = []
        for choice_li in question_container.find("ul", class_="answers").find_all("li"):
            choice_input = choice_li.find("input")
            choice_text = choice_li.text.strip()
            choice_value = choice_input["value"].lower()  # Récupérer la lettre en minuscule
            
            choice_id = f"{exam.name}_{question_counter}_{choice_value}"
            is_correct = choice_value in correct_answers.get(str(question_counter), [])

            choices.append({
                "id": choice_id,
                "text": choice_text,
                "is_correct": is_correct
            })

        questions.append({
            "question_id": question_id,
            "text": question_text,
            "choices": choices
        })

    return questions

@transaction.atomic
def store_questions_in_db(exam, questions):
    """Insère les questions et choix en base de données."""
    
    for q in questions:
        question, created = Question.objects.get_or_create(
            id=q["question_id"], 
            defaults={"exam": exam, "text": q["text"]}
        )

        if created:
            print(f"✅ Question ajoutée : {q['text'][:50]}...")

        for c in q["choices"]:
            Choice.objects.get_or_create(
                id=c["id"],
                question=question,
                defaults={"text": c["text"], "is_correct": c["is_correct"]}
            )
    
    print("✅ Insertion terminée.")

# Exécution
process_questions()
