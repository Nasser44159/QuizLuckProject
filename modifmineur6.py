import os

# Chemin du répertoire des templates
template_dir = "C:/Users/thinkup/Documents/QuizLuckProject/quizapp/templates"

# Parcours de tous les fichiers HTML dans les sous-répertoires
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            modified = False

            # Lecture du contenu du fichier
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Vérification de la présence de la balise </html>
            if "</html>" in content:
                # Séparation à partir de la balise </html>
                before_html, after_html = content.split("</html>", 1)

                # Suppression de tout après </html> jusqu'à la prochaine balise <script>
                if "<script>" in after_html:
                    # Reconstruction du fichier
                    updated_content = before_html + "</html>" + after_html.split("<script>", 1)[1]
                    modified = True
                else:
                    updated_content = before_html + "</html>"

                # Écriture du contenu mis à jour
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)

            # Log des fichiers modifiés ou non
            if modified:
                print(f"Modifications effectuées dans : {file_path}")
            else:
                print(f"Aucune modification nécessaire pour : {file_path}")
