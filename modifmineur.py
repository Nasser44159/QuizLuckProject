import os

def remplacer_ligne_html(chemin_racine):
    ancienne_ligne = '<link rel="stylesheet" href="stylepagedexam.css">'
    nouvelle_ligne = '{% load static %}\n<link rel="stylesheet" href="{% static \'css/stylepagedexam.css\' %}">'

    for dossier, sous_dossiers, fichiers in os.walk(chemin_racine):
        for fichier in fichiers:
            if fichier.endswith(".html"):
                chemin_fichier = os.path.join(dossier, fichier)
                
                # Lire le fichier
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    contenu = f.read()
                
                # Remplacer la ligne
                if ancienne_ligne in contenu:
                    contenu_modifie = contenu.replace(ancienne_ligne, nouvelle_ligne)
    # Éviter de réécrire si aucune modification n'est nécessaire
                    if contenu != contenu_modifie:
                        with open(chemin_fichier, 'w', encoding='utf-8') as f:
                            f.write(contenu_modifie)
                        print(f"Ligne remplacée dans : {chemin_fichier}")
                    else:
                        print(f"Aucune modification nécessaire pour : {chemin_fichier}")


# Remplacez ceci par le chemin de votre dossier contenant les fichiers HTML
chemin_racine = r"C:\Users\thinkup\Documents\QuizLuckProject\quizapp\templates"
remplacer_ligne_html(chemin_racine)
