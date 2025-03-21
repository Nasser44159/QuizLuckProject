import os
import re

# Définir le chemin de base des fichiers Favori
BASE_DIR = "C:/Users/thinkup/Documents/QuizLuckProject/quizapp/templates"

def update_window_location_in_favori(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Expression régulière pour trouver la ligne avec window.location.href
    pattern = r'        <button class="home-button".*?>Retourner à l\'accueil</button>'
    replacement = '<a href="{% url \'home\' %}" class="home-button">Retourner à l\'accueil</a>'

    # Remplacement
    updated_content = re.sub(pattern, replacement, content)

    if content != updated_content:
        # Écrire les modifications dans le fichier
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"Modifié : {file_path}")
    else:
        print(f"Aucune modification nécessaire dans : {file_path}")


# Parcourir les semestres et les fichiers Favori
for semester in os.listdir(BASE_DIR):
    semester_path = os.path.join(BASE_DIR, semester)
    if os.path.isdir(semester_path):  # Vérifier que c'est un dossier
        for file_name in os.listdir(semester_path):
            if file_name.startswith("Favori") and file_name.endswith(".html"):
                file_path = os.path.join(semester_path, file_name)
                update_window_location_in_favori(file_path)
