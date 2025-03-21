import json

# Charger le fichier JSON
with open("jsonvalidator.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Exclure les objets liés aux profils
filtered_data = [entry for entry in data if entry["model"] != "quizapp.profile"]

# Sauvegarder le fichier nettoyé
with open("backup_no_profiles.json", "w", encoding="utf-8") as outfile:
    json.dump(filtered_data, outfile, indent=4, ensure_ascii=False)

print("Les profils ont été supprimés du fichier.")
