import os

def remove_test_line():
    # Chemin du dossier templates
    templates_dir = os.path.join("quizapp", "templates")

    # Parcourir les fichiers et sous-dossiers dans templates_dir
    for root, dirs, files in os.walk(templates_dir):
        for file_name in files:
            # Vérifier si le fichier est un fichier HTML
            if file_name.endswith(".html"):
                file_path = os.path.join(root, file_name)

                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()

                # Rechercher et supprimer la ligne contenant le texte cible
                updated_lines = [
                    line for line in lines if "Testez vos connaissances" not in line
                ]

                # Vérifier si des modifications ont été effectuées
                if len(updated_lines) < len(lines):
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.writelines(updated_lines)
                    print(f"Fichier modifié : {file_path}")

if __name__ == "__main__":
    remove_test_line()
