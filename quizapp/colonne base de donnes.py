import sys
import os

# Ajouter le répertoire parent au chemin pour éviter les problèmes d'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
import django
django.setup()

from quizapp.models import Exam, Subject

# Définissez ici vos rapports (préfixe → subject)
prefix_to_subject = {
    "Anatomie": "Anatomie",
    "Bioch": "Biochimie",
    "Chim": "Chimie",
    "Bioph": "Biophysique",
    "Gen": "Genetique",
    "Biol": "Biologie",
    "Meterm": "Methodologie et Terminologie",
    "Sp": "Sante publique et Biostatistique",
    "AnatII": "Anatomie 2",
    "HIST": "Histologie",
    "EMB": "Embryologie",
    "SH": "Sciences Humaines",
    "Ap": "Anatomie Pathologique générale",
    "AP": "Anatomie Pathologique générale",
    "MI": "Maladies infectieuses et parasitologie",
    "Rd": "Radiologie",
    "CL": "Cardiologie",
    "CV": "Chirurgie cardio-vasculaire",
    "CLC": "Chirurgie Cardiaque",
    "MR": "Maladies respiratoires",
    "AD": "Maladies digestives",
    "ADC": "Chirurgie Digestives",
    "CC": "Chirurgie Thoracique",
    "NL": "Neurologie",
    "NC": "Neurochirurgie",
    "Dt": "Dermatologie",
    "ECN": "Endocrinologie",
    "HMT": "Hematologie",
    "OC": "Oncologie",
    # Ajoutez d'autres rapports ici
}

# Fonction pour mettre à jour les sujets
def update_exam_subjects():
    # Récupérer tous les examens
    exams = Exam.objects.all()

    for exam in exams:
        # Trouver le sujet correspondant au préfixe
        for prefix, subject_name in prefix_to_subject.items():
            if exam.name.startswith(prefix):  # Si le nom commence par le préfixe
                try:
                    # Récupérer le sujet correspondant dans la base de données
                    subject = Subject.objects.get(name=subject_name)
                    # Mettre à jour l'examen avec ce sujet
                    exam.subject = subject
                    exam.save()
                    print(f"Examen '{exam.name}' mis à jour avec le sujet '{subject.name}'")
                except Subject.DoesNotExist:
                    print(f"Sujet '{subject_name}' introuvable pour l'examen '{exam.name}'")
                break  # On arrête la recherche une fois qu'un préfixe est trouvé

# Exécutez la fonction
update_exam_subjects()
