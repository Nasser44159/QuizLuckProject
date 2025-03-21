import os

def find_files_ending_with_p(directory, exclude_file):
    """
    Parcourt les fichiers dans le répertoire donné et affiche ceux 
    dont le nom avant .html se termine par la lettre 'P', en excluant un fichier spécifique.

    :param directory: Chemin du répertoire à parcourir.
    :param exclude_file: Nom du fichier (sans extension) à exclure.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Vérifie si le fichier a une extension .html
            if file.endswith('.html'):
                # Récupère le nom sans l'extension
                file_name_without_ext = file[:-5]
                
                # Vérifie si le fichier se termine par "P" et n'est pas l'exclu
                if file_name_without_ext.endswith('P') and file_name_without_ext != exclude_file:
                    file_path = os.path.join(root, file)
                    print(f"Fichier trouvé : {file_path}")

# Spécifie le répertoire à parcourir et le fichier à exclure
directory = "quizapp/templates"
exclude_file = "Anatomie_Pathologique_generale"

# Appelle la fonction
find_files_ending_with_p(directory, exclude_file)
