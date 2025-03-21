import os
import re

BASE_DIR = "C:/Users/thinkup/Documents/QuizLuckProject/quizapp/templates"  # Remplacez par le chemin correct

# Fonction pour traiter chaque fichier HTML
def process_file(file_path, semester, module):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Modèle pour les lignes à remplacer
    pattern = r'window\.location\.href = \'{% url "dynamic_file" "(.+?)" "(.+?)" "(.+?)" %}\';'
    
    def replacement(match):
        old_semester = match.group(1)
        old_module = match.group(2)
        old_file = match.group(3)
        
        # Construction de la nouvelle ligne
        return (
            f'<button type="button" class="reset-quiz-button" '
            f'onclick="window.location.href = \'{{% url "dynamic_file" "{semester}" "{module}" "{old_file}" %}}\';">'
            f'Réessayer tout le Quiz</button>'
    )

    # Remplacer les lignes correspondant au modèle
    updated_content = re.sub(pattern, replacement, content)

    # Si du contenu a été modifié
    if content != updated_content:
        print(f"Modifié : {file_path}")  # Affiche les fichiers modifiés
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

# Parcourir les semestres et modules
def process_qcm_files():
    for semester in os.listdir(BASE_DIR):
        semester_path = os.path.join(BASE_DIR, semester)
        if os.path.isdir(semester_path):
            for module in os.listdir(semester_path):
                module_path = os.path.join(semester_path, module)
                if os.path.isdir(module_path):
                    for file_name in os.listdir(module_path):
                        # Modifier uniquement les fichiers commençant par "synt"
                        if not file_name.startswith("synt"):
                            continue
                        # Modifier uniquement les fichiers .html
                        if file_name.endswith(".html"):
                            file_path = os.path.join(module_path, file_name)
                            process_file(file_path, semester, module)

# Lancer le script
process_qcm_files()
