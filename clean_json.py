# Nom du fichier à convertir
source_file = "clean_data.json"
output_file = "clean_data_utf8.json"

try:
    # Lecture du fichier avec son encodage d'origine (par exemple, ISO-8859-1 ou autre)
    with open(source_file, "r", encoding="utf-8-sig") as infile:
        data = infile.read()

    # Écriture du fichier en UTF-8
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(data)

    print(f"Le fichier a été converti et enregistré sous : {output_file}")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
