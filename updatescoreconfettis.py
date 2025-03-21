import os
import re

def update_question_counts():
    templates_dir = os.path.join("quizapp", "templates")
    total_questions_adjusted = 0  # Pour suivre le nombre total ajusté de questions

    # Parcourir les fichiers dans le dossier des templates
    for root, dirs, files in os.walk(templates_dir):
        # Ignorer les dossiers contenant "synt"
        if "synt" in root:
            continue

        for file_name in files:
            if file_name.endswith(".html"):
                file_path = os.path.join(root, file_name)

                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Trouver tous les IDs des questions
                question_ids = re.findall(r'id="question-(\d+)"', content)
                if not question_ids:
                    print(f"Aucune question trouvée dans : {file_name}")
                    continue

                # Calculer le nombre brut de questions
                raw_question_count = len(question_ids)

                # Si le nombre de questions n'est pas un multiple de 5, ajuster
                if raw_question_count % 5 != 0:
                    adjusted_question_count = (raw_question_count // 5) + 1
                else:
                    adjusted_question_count = raw_question_count

                total_questions_adjusted += adjusted_question_count

                # Rechercher la ligne contenant `if (score === X)`
                match = re.search(r'if\s*\(score\s*===\s*(\d+)\)', content)

                if match:
                    existing_score = int(match.group(1))

                    if existing_score != adjusted_question_count:
                        print(f"Modification requise dans {file_name}: score {existing_score} remplacé par {adjusted_question_count}")
                        # Remplacer l'ancien score par le nombre correct de questions ajusté
                        content = re.sub(r'if\s*\(score\s*===\s*\d+\)', f'if (score === {adjusted_question_count})', content)
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(content)
                    else:
                        print(f"Ligne correcte dans {file_name}: score === {existing_score}")
                else:
                    print(f"Aucune ligne `if (score === X)` trouvée dans : {file_name}")

    print(f"Nombre total ajusté de questions dans tous les fichiers : {total_questions_adjusted}")

if __name__ == "__main__":
    update_question_counts()
