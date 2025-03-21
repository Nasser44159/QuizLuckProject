import os
import re
import json

# Définir le chemin du projet et du dossier templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Chemin du fichier Python
QUIZAPP_DIR = os.path.join(BASE_DIR, "quizapp")
TEMPLATES_DIR = os.path.join(QUIZAPP_DIR, "templates")
OUTPUT_DIR = os.path.join(QUIZAPP_DIR, "static/data")
EXCLUDED_DIR = "Anatomie_1"

# Créer le dossier de sortie s'il n'existe pas
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_correct_answers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher l'objet correctAnswers
        match = re.search(r'const correctAnswers\s*=\s*(\{.*?\});', content, re.DOTALL)
        if match:
            correct_answers_js = match.group(1)
            
            # Étape 1 : Ajouter des guillemets doubles aux clés
            corrected_keys = re.sub(r'(\bq\d+\b):', r'"\1":', correct_answers_js)
            
            # Étape 2 : Remplacer les guillemets simples par des guillemets doubles pour les valeurs
            corrected_json = corrected_keys.replace("'", '"')
            
            # Supprimer les éventuelles virgules finales (erreur fréquente dans le JSON)
            corrected_json = re.sub(r',\s*}', '}', corrected_json)
            
            # Charger en tant que JSON valide
            try:
                correct_answers = json.loads(corrected_json)
                return correct_answers
            except json.JSONDecodeError as e:
                print(f"Erreur JSON : {e}")
                print(f"JSON problématique : {corrected_json}")
        else:
            print(f"Aucune donnée correcte trouvée dans : {file_path}")
    except Exception as e:
        print(f"Erreur : {e}")
    return None

def process_files():
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        # Exclure le dossier Anatomie_1
        if EXCLUDED_DIR in root:
            print(f"Dossier exclu : {root}")
            continue

        for file_name in files:
            if file_name.startswith("synt") and file_name.endswith(".html"):
                print(f"Fichier correspondant trouvé : {file_name}")
                file_path = os.path.join(root, file_name)
                
                # Extraire les réponses correctes
                correct_answers = extract_correct_answers(file_path)
                
                if correct_answers:
                    # Construire le nom du fichier JSON
                    json_file_name = file_name.replace("synt", "").replace(".html", "_correct_answers.json")
                    json_file_path = os.path.join(OUTPUT_DIR, json_file_name)
                    
                    # Vérifier si le fichier existe déjà
                    if os.path.exists(json_file_path):
                        print(f"Le fichier JSON existe déjà : {json_file_path}. Aucun fichier n'a été créé.")
                        continue
                    
                    # Écrire dans le fichier JSON
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(correct_answers, json_file, indent=4, ensure_ascii=False)
                        print(f"Fichier JSON créé : {json_file_path}")
                else:
                    print(f"Aucune donnée trouvée dans : {file_path}")

if __name__ == "__main__":
    process_files()
