import os
import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
django.setup()

from quizapp.models import Semester, Exam

def process_templates():
    # Chemin spécifique pour le dossier templates
    templates_dir = os.path.join('quizapp', 'templates')

    # Vérifier si le dossier templates existe
    if not os.path.exists(templates_dir):
        print(f"Dossier introuvable : {templates_dir}")
        return

    # Parcourir les sous-dossiers directs de templates
    for semester_folder in os.listdir(templates_dir):
        semester_path = os.path.join(templates_dir, semester_folder)

        # Vérifier si c'est un dossier
        if not os.path.isdir(semester_path):
            print(f"Ignoré (pas un dossier) : {semester_folder}")
            continue

        # Créer ou récupérer le semestre
        semester_name = semester_folder.upper()  # Exemple : S1 devient S1
        semester, created = Semester.objects.get_or_create(name=semester_name)

        if created:
            print(f"Semestre ajouté : {semester_name}")
        else:
            print(f"Semestre existant : {semester_name}")

        # Parcourir les fichiers HTML dans ce sous-dossier
        for file_name in os.listdir(semester_path):
            # Ignorer les fichiers qui commencent par "synt" ou qui ne sont pas HTML
            if file_name.startswith("synt") or not file_name.endswith(".html"):
                print(f"Ignoré (synt ou non-HTML) : {file_name}")
                continue

            # Extraire le nom de l'examen à partir du fichier
            exam_name = file_name.replace(".html", "")  # Supprimer l'extension .html

            # Créer ou ignorer l'examen s'il existe déjà
            exam, created = Exam.objects.get_or_create(
                name=exam_name,
                defaults={
                    'semester': semester,
                    'template_name': file_name
                }
            )

            if created:
                print(f"Examen ajouté : {exam_name}, Semestre : {semester.name}, Template : {file_name}")
            else:
                print(f"Examen existant : {exam_name}, Semestre : {semester.name}")

if __name__ == '__main__':
    process_templates()
