import os
import re

# Chemin du projet
BASE_DIR = "C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\templates"

def process_js_file(file_path, semester):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remplacement des chemins statiques par les URLs Django dynamiques
    def replace_exam_link(match):
        year = match.group(1)  # Extraire l'année
        return f'window.location.href = "{{% url \'render_favorite\' \'{semester}\' \'Favori{year}\' %}}";'

    pattern = r'window\.location\.href\s*=\s*[\'"]\.\/favori(\d+)\.html[\'"];'
    updated_content = re.sub(pattern, replace_exam_link, content)

    if content != updated_content:
        print(f"Modifié : {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
    else:
        print(f"Aucun lien à modifier dans : {file_path}")

def update_js_links(base_dir):
    for semester in os.listdir(base_dir):
        semester_path = os.path.join(base_dir, semester)
        if os.path.isdir(semester_path):
            for file in os.listdir(semester_path):
                if file.endswith(".js"):  # Rechercher les fichiers JavaScript
                    file_path = os.path.join(semester_path, file)
                    process_js_file(file_path, semester)

update_js_links(BASE_DIR)
