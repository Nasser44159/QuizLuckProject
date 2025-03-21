import os
import re

# Chemin du dossier contenant les fichiers HTML
base_dir = "quizapp/templates"

# Parcourir les fichiers dans le dossier
for root, _, files in os.walk(base_dir):
    # Exclure le dossier "Anatomie_1"
    if "Anatomie_1" in root:
        continue

    for file in files:
        if file.startswith("synt") and file.endswith(".html"):
            file_path = os.path.join(root, file)
            print(f"Modification du fichier : {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Remplacement de <style> par le fichier CSS externe
            content = re.sub(
                r"<style>[\s\S]*?</style>",
                r'{% load static %}\n<link rel="stylesheet" href="{% static \'css/stylesynt.css\' %}">',
                content,
                flags=re.MULTILINE,
            )

            # Ajout de l'input hidden avec file_name
            match = re.search(r'<form id="quiz-form">', content)
            if match:
                file_name = os.path.basename(file).replace("synt", "").replace(".html", "").strip()
                input_hidden = f'<form id="quiz-form">\n<input type="hidden" name="file_name" value="{file_name}">'
                content = content.replace(match.group(0), input_hidden)

            # Ajout du script JavaScript à la fin
            if '<script src="{% static \'java/question-stats.js\' %}" defer></script>' not in content:
                content += '\n<script src="{% static \'java/question-stats.js\' %}" defer></script>'

            # Sauvegarder le fichier modifié
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

print("Tous les fichiers nécessaires ont été modifiés.")
