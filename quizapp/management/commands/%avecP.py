import os
import sys
import django
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from quizapp.models import UncorrectedQuestion, UncorrectedChoice, Exam

# Configuration de Django
sys.path.append("c:/Users/thinkup/Documents/QuizLuckProject")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')

try:
    django.setup()
    print("Django configuré avec succès.")
except Exception as e:
    print(f"Erreur lors de la configuration de Django : {e}")
    sys.exit(1)

class Command(BaseCommand):
    help = "Importe des questions et des choix à partir de fichiers HTML situés directement dans S1 à S10 (pas de sous-dossier) et se terminant par 'P.html'."

    def handle(self, *args, **kwargs):
        # Dossiers racines contenant les fichiers HTML
        templates_dir = os.path.join("quizapp", "templates")
        semesters = [f"S{i}" for i in range(1, 11)]  # Génère S1 à S10

        for semester in semesters:
            semester_dir = os.path.join(templates_dir, semester)

            if not os.path.exists(semester_dir):
                print(f"Dossier introuvable : {semester_dir}")
                continue

            print(f"Parcours du répertoire : {semester_dir}")

            # Parcourir les fichiers directement dans le dossier (pas de sous-dossier)
            for file in os.listdir(semester_dir):
                filepath = os.path.join(semester_dir, file)

                # Vérifier si c'est un fichier et s'il correspond aux critères
                if os.path.isfile(filepath) and file.endswith("P.html") and not file.startswith("synt"):
                    print(f"Fichier HTML accepté : {filepath}")

                    with open(filepath, "r", encoding="utf-8") as f:
                        soup = BeautifulSoup(f, "html.parser")
                        print(f"Analyse du fichier : {file}")

                        # Récupérer l'examen correspondant
                        exam_name = file.split('.')[0]
                        print(f"Nom de l'examen détecté : {exam_name}")

                        try:
                            exam_instance = Exam.objects.get(name=exam_name)
                            print(f"Examen trouvé dans la base de données : {exam_instance.name}")
                        except Exam.DoesNotExist:
                            print(f"Examen {exam_name} introuvable. Ignoré.")
                            continue

                        # Récupérer toutes les questions
                        questions = soup.find_all("p")
                        print(f"Nombre de questions trouvées : {len(questions)}")

                        for question_index, question_tag in enumerate(questions):
                            question_text = question_tag.get_text(strip=True)

                            # Vérifier si la question contient seulement "a"
                            if question_text.lower() == "a":
                                print(f"Question ignorée car son texte est 'a'.")
                                continue

                            question_id = f"{exam_name}_{question_index + 1}"
                            print(f"Création de la question ID : {question_id}")

                            question, created = UncorrectedQuestion.objects.get_or_create(
                                id=question_id,
                                text=question_text,
                                exam=exam_instance
                            )
                            if created:
                                print(f"Question créée avec l'ID : {question_id}")
                            else:
                                print(f"Question déjà existante avec l'ID : {question_id}")

                            # Récupérer les choix associés
                            choices_container = question_tag.find_next("ul")
                            if choices_container:
                                choices = choices_container.find_all("li")
                                print(f"Nombre de choix pour la question #{question_index + 1} : {len(choices)}")

                                for choice_index, choice_tag in enumerate(choices):
                                    choice_text = choice_tag.get_text(strip=True)
                                    choice_id = f"{question_id}_{chr(97 + choice_index)}"
                                    print(f"Création du choix : {choice_text} (ID : {choice_id})")

                                    choice, created = UncorrectedChoice.objects.get_or_create(
                                        id=choice_id,
                                        question=question,
                                        text=choice_text
                                    )
                                    if created:
                                        print(f"Choix créé avec l'ID : {choice_id}")
                                    else:
                                        print(f"Choix déjà existant avec l'ID : {choice_id}")

        print("Importation terminée avec succès.")
