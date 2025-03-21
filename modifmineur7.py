import re
import os

# Chemin vers le dossier "templates"
TEMPLATES_DIR = r"C:\Users\thinkup\Documents\QuizLuckProject\quizapp\templates"

def modify_html_file(file_path):
    try:
        print(f"Traitement du fichier : {file_path}")

        # Lire le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Vérifier si le fichier contient une section commentaire
        if '<div class="comments-section"' not in content:
            print(f"Aucune section commentaires trouvée dans : {file_path}. Ignoré.")
            return

        # 1. Supprimer le bloc script contenant //PARTIE COMMENTAIRE
        print("1. Suppression du script contenant //PARTIE COMMENTAIRE...")
        content = re.sub(
            r"<script>\s*//PARTIE COMMENTAIRE.*?</script>",
            "",  # Remplacer par une chaîne vide
            content,
            flags=re.DOTALL
        )

        # 2. Remplacer la section comments-section
        print("2. Remplacement de la section comments-section...")
        content = re.sub(
            r'<div class="comments-section" id="comments-section">.*?</div>',
            '''<div class="comments-section" id="comments-section">
    <button class="toggle-arrow" id="toggle-arrow" onclick="toggleCommentSection(null, event)">❯</button>
    <h3>Commentaires</h3>
    <textarea id="new-comment" placeholder="Écrire un commentaire..."></textarea>
    <button type="button" onclick="addComment(event)">Ajouter</button>
    <div id="comment-alert" class="alert" style="display: none;"></div>
    <div id="comments-list"></div>
</div>''',
            content,
            flags=re.DOTALL
        )

        # 3. Modifier data-question-id, data-comment-id, et onclick
        print("3. Modification des attributs data-question-id, data-comment-id, et onclick...")

        def replace_question_ids(match):
            question_id = match.group(1)  # Capture "question-2" ou similaire
            question_number = question_id.split('-')[-1]  # Extraire le numéro
            file_name = os.path.splitext(os.path.basename(file_path))[0]  # Nom du fichier sans extension
            return f"{file_name}_{question_number}"

        # Remplacer data-question-id
        content = re.sub(
            r'data-question-id="(question-\d+)"',
            lambda m: f'data-question-id="{replace_question_ids(m)}"',
            content
        )

        # Remplacer data-comment-id
        content = re.sub(
            r'data-comment-id="(question-\d+)"',
            lambda m: f'data-comment-id="{replace_question_ids(m)}"',
            content
        )

        # Remplacer onclick="toggleCommentSection('question-2', event)"
        content = re.sub(
            r'onclick="toggleCommentSection\(\'(question-\d+)\'",',
            lambda m: f'onclick="toggleCommentSection(\'{replace_question_ids(m)}\'",',
            content
        )

        # 4. Ajouter une ligne <script> à la fin du fichier
        print("4. Ajout du script à la fin du fichier...")
        if "<script src=\"{% static 'java/comment.js' %}\"></script>" not in content:
            content += '\n    <script src="{% static \'java/comment.js\' %}"></script>'

        # Écrire le contenu modifié dans le même fichier
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"Modifications terminées avec succès pour le fichier : {file_path}\n")

    except Exception as e:
        print(f"Une erreur s'est produite pour le fichier {file_path} : {e}")

def process_all_html_files(directory):
    print(f"Recherche de fichiers HTML dans le dossier : {directory}\n")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html") and not file.startswith("synt"):
                file_path = os.path.join(root, file)
                modify_html_file(file_path)

# Lancer le traitement pour tous les fichiers dans le dossier templates
process_all_html_files(TEMPLATES_DIR)
