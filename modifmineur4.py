import os
import re

# Répertoire racine où se trouvent les fichiers des semestres
BASE_DIR = r"C:\Users\thinkup\Documents\QuizLuckProject\quizapp\templates"

# Expression régulière pour détecter les lignes `window.location.href`
pattern = r"window\.location\.href\s*=\s*['\"]([^'\"]+\.html)['\"]\s*;"

# Nouvelle ligne à insérer (échappement des accolades pour str.format)
replacement_template = "window.location.href = '{{% url 'dynamic_file' '{semester}' '{module}' '{file_name}' %}}';"

def process_file(file_path, semester, module):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Vérifier si des modifications sont nécessaires
    updated_content = content
    for match in re.finditer(pattern, content):
        # Extraire le nom du fichier depuis `window.location.href`
        file_target_name = match.group(1).replace(".html", "")  # Extraire le nom sans extension

        # Construire la ligne de remplacement avec le nom d'origine
        replacement = replacement_template.format(
            semester=semester,
            module=module,
            file_name=file_target_name
        )

        # Remplacer la ligne complète
        updated_content = updated_content.replace(match.group(0), replacement)

    # Si le contenu a été modifié, sauvegarder et informer
    if content != updated_content:
        print(f"Modifications effectuées dans le fichier : {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
    else:
        print(f"Aucune modification nécessaire dans : {file_path}")



def process_qcm_files():
    for semester in os.listdir(BASE_DIR):
        semester_path = os.path.join(BASE_DIR, semester)
        if not os.path.isdir(semester_path):
            continue

        # Parcourir chaque dossier "module" (comme Anatomie_1, Biochimie_et_chimie, etc.)
        for module in os.listdir(semester_path):
            module_path = os.path.join(semester_path, module)
            if not os.path.isdir(module_path):
                continue

            # Parcourir les fichiers dans chaque dossier module
            for file_name in os.listdir(module_path):
                # Traiter uniquement les fichiers HTML
                if file_name.endswith(".html"):
                    file_path = os.path.join(module_path, file_name)
                    process_file(file_path, semester, module)

# Lancer le traitement
process_qcm_files()
