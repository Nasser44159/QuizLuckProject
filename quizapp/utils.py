import os
from quizapp.models import QuestionAttempt

def get_valid_pagemodules(templates_dir):
    valid_pagemodules = []
    for semester in os.listdir(templates_dir):  # Parcourir les dossiers des semestres
        semester_path = os.path.join(templates_dir, semester)
        if os.path.isdir(semester_path):
            for file in os.listdir(semester_path):  # Parcourir les fichiers HTML
                if file.endswith('.html'):
                    page_name = os.path.splitext(file)[0]  # Enlever ".html"
                    valid_pagemodules.append(page_name)
    return valid_pagemodules

# Exemple d'utilisation
templates_dir = os.path.join('quizapp', 'templates')  # Remplacez par le chemin de votre dossier templates
VALID_PAGEMODULE = get_valid_pagemodules(templates_dir)


def analyze_question_performance(user, question_id, threshold=3, recent_attempts=5):
    # Récupérer les tentatives pour cette question
    attempts = QuestionAttempt.objects.filter(user=user, question_id=question_id).order_by('-timestamp')

    # Vérifier les échecs consécutifs
    consecutive_failures = 0
    for attempt in attempts:
        if attempt.is_correct:
            break  # Réinitialiser la séquence d'échecs si une réponse est correcte
        consecutive_failures += 1

    # Vérifier si le taux d'échec récent est élevé
    recent_attempts = attempts[:recent_attempts]
    recent_failures = sum(1 for attempt in recent_attempts if not attempt.is_correct)
    failure_rate = recent_failures / len(recent_attempts) if recent_attempts else 0

    return {
        "consecutive_failures": consecutive_failures,
        "failure_rate": failure_rate
    }
