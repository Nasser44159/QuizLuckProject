import os
import re

# Chemin de base vers le dossier templates
base_dir = r"C:\\Users\\thinkup\\Documents\\QuizLuckProject\\quizapp\\templates"

# Fonction pour modifier un fichier spécifique
def modify_file(file_path):
    try:
        print(f"Traitement du fichier : {file_path}")

        # Lire le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Vérifier si le fichier contient un bouton avec "class=\"comment-button\""
        if '<button class="comment-button"' not in content:
            print(f"Aucun bouton comment-button trouvé dans : {file_path}. Ignoré.")
            return

        print("Boutons comment-button détectés. Modification en cours...")

        # Expression régulière pour remplacer "question-X" par le data-question-id correspondant
        def replace_question_id(match):
            data_question_id = match.group(1)
            question_number = match.group(2)
            return f"data-question-id=\"{data_question_id}\" onclick=\"toggleCommentSection('{data_question_id}', event)\""

        content = re.sub(
            r'data-question-id=\"(.*?)\" onclick=\"toggleCommentSection\(\'question-(\d+)\', event\)\"',
            replace_question_id,
            content
        )

        # Écrire le contenu modifié dans le fichier
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Modifications terminées pour le fichier : {file_path}\n")

    except Exception as e:
        print(f"Une erreur s'est produite pour le fichier {file_path} : {e}")

# Parcourir le dossier templates et appliquer la modification
def process_templates(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("synt"):
                print(f"Fichier ignoré car il commence par 'synt' : {file}")
                continue

            file_path = os.path.join(root, file)
            modify_file(file_path)

# Appeler la fonction pour traiter le dossier templates
process_templates(base_dir)
