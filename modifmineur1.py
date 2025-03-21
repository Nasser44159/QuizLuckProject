import os
import re


# Répertoire racine où se trouvent les semestres
BASE_DIR = r"C:\Users\thinkup\Documents\QuizLuckProject\quizapp\templates"

def list_semesters_modules_files(base_dir):
    """
    Parcourt les semestres, modules et fichiers pour imprimer leur structure.
    """
    print("Structure des semestres, modules et fichiers :\n")
    
    # Parcourir les semestres (dossiers à la racine)
    for semester in os.listdir(base_dir):
        semester_path = os.path.join(base_dir, semester)
        
        # Vérifier que c'est un dossier et qu'il ne commence pas par "synt"
        if os.path.isdir(semester_path) and not semester.lower().startswith("synt"):
            print(f"Semester: {semester}")
            
            # Parcourir les modules dans chaque semestre
            for module in os.listdir(semester_path):
                module_path = os.path.join(semester_path, module)
                
                # Vérifier que c'est un dossier et qu'il ne commence pas par "synt" ou "favori"
                if os.path.isdir(module_path) and not module.lower().startswith(("synt", "favori")):
                    print(f"  Module: {module}")
                    
                    # Parcourir les fichiers HTML dans chaque module
                    for file_name in os.listdir(module_path):
                        if file_name.endswith(".html") and not file_name.lower().startswith(("synt", "favori")):
                            print(f"    File: {file_name}")


# Fonction pour traiter les fichiers HTML dans les modules
def process_return_links(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remplacer le lien correspondant au retour à l'accueil
    pattern = r'<a href="\.\.\/pagedacceuil\.html" class="btn btn-primary">Retourner à l\'accueil</a>'
    replacement = r'<a href="{% url \'home\' %}" class="btn btn-primary">Retourner à l\'accueil</a>'
    updated_content = re.sub(pattern, replacement, content)

    if content == updated_content:
        # Aucun remplacement n'est effectué
        print(f"Aucun lien de retour à modifier dans : {file_path}")
    else:
        # Un remplacement est effectué
        print(f"Modifié : {file_path}")

        # Écrire le contenu mis à jour
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

# Parcourir les semestres et leurs modules
for semester in os.listdir(BASE_DIR):
    semester_path = os.path.join(BASE_DIR, semester)
    if os.path.isdir(semester_path):  # Vérifier si c'est un dossier
        for module in os.listdir(semester_path):
            module_path = os.path.join(semester_path, module)
            if os.path.isdir(module_path):  # Vérifier si c'est un dossier module (ex : Anatomie_1)
                module_file_path = os.path.join(module_path, f"{module}.html")
                if os.path.exists(module_file_path):  # Vérifier si le fichier module HTML existe
                    process_return_links(module_file_path)