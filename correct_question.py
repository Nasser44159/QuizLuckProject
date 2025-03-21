import os
import re

import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
django.setup()

from django.conf import settings


def process_files():
    # Récupérer le chemin absolu du répertoire `templates` de l'application `quizapp`
    template_dir = os.path.join(settings.BASE_DIR, "quizapp", "templates")

    # Stockage des noms des fichiers modifiés
    modified_files = []

    # Parcourir les fichiers dans le répertoire `templates`
    for root, _, files in os.walk(template_dir):
        for file in files:
            if file.startswith("synt") or file.endswith("P"):
                continue  # Exclure les fichiers commençant par "synt" ou se terminant par "P"

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Vérifier si le fichier contient la balise <form id="quiz-form">
                if '<form id="quiz-form">' not in content:
                    print(f"Aucune balise <form id='quiz-form'> trouvée dans {file}")
                    continue

                print(f"Traitement du fichier : {file}")

                # Vérifier si l'input hidden est déjà présent
                exam_name = os.path.splitext(file)[0]  # Nom du fichier sans extension
                hidden_input = f"<input type=\"hidden\" id='exam_name' name=\"exam_name\" value=\"{exam_name}\">"
                if hidden_input in content:
                    print(f"Le champ hidden pour {exam_name} est déjà présent dans {file}.")
                else:
                    # Ajouter le champ hidden sous <form id="quiz-form">
                    content = content.replace(
                        '<form id="quiz-form">',
                        f"<form id=\"quiz-form\">\n    {hidden_input}"
                    )
                    print(f"Ajout du champ hidden pour {exam_name} dans {file}.")

                # Supprimer la fonction existante correctQuestion
                content, num_replacements = re.subn(
                    r"// Fonction pour corriger une question\s+function correctQuestion\(.*?\}\n\}\n", 
                    "", 
                    content, 
                    flags=re.DOTALL
                )
                if num_replacements > 0:
                    print(f"Ancienne fonction `correctQuestion` supprimée dans {file}.")

                # Ajouter la nouvelle fonction correctQuestion
                if "// Fonction pour corriger une question" not in content:
                    content += """
// Fonction pour corriger une question 
function correctQuestion(questionName) {
    const form = document.getElementById('quiz-form');
    const questionDiv = document.querySelector(`input[name="${questionName}"]`).closest('.question-container');
    const selected = Array.from(form.elements[questionName]).filter(input => input.checked).map(input => input.value);

    // Calculer si la réponse est correcte
    const isCorrect = JSON.stringify(correctAnswers[questionName].sort()) === JSON.stringify(selected.sort());

    // Enregistre si la réponse est correcte ou incorrecte
    userAnswers[questionName] = {
        selected: selected,
        isCorrect: isCorrect
    };

    // Supprimer les styles précédents
    questionDiv.classList.remove('correct', 'incorrect');
    questionDiv.querySelectorAll('li').forEach(li => li.style.color = '');

    // Applique les couleurs selon la validité des réponses
    questionDiv.querySelectorAll('li').forEach(li => {
        const isChoiceCorrect = correctAnswers[questionName].includes(li.querySelector('input').value);
        const isSelected = selected.includes(li.querySelector('input').value);

        if (isChoiceCorrect) {
            // Appliquer le style vert aux bonnes réponses
            li.style.color = 'green';
            li.style.fontWeight = 'bold';
            li.style.textShadow = '1px 1px 2px rgba(0, 128, 0, 0.7)';
            li.style.backgroundColor = 'transparent'; // Remettre le fond transparent
            li.style.border = 'none'; // Supprimer la bordure
        }

        if (isSelected && !isChoiceCorrect) {
            // Appliquer le style rouge pour les mauvaises réponses sélectionnées
            li.style.color = 'red';
        }
    });

    console.log(`Début de la correction pour la question ${questionName}`);
    console.log(`Réponses sélectionnées pour ${questionName}: ${selected.join(', ')}`);
    console.log(`Résultat pour ${questionName}: ${isCorrect ? 'Correct' : 'Incorrect'}`);

    // Déterminer le nom de l'examen et l'ID complet de la question
    const examNameElement = document.getElementById('exam_name');

    // Construire les IDs complets des choix
    const examName = examNameElement.value; // Nom de l'examen (par exemple, Anatomie2023)
    const fullChoiceIds = selected.map(choice => `${examName}_${questionName.substring(1)}_${choice.toLowerCase()}`);
    console.log(`IDs complets générés pour les choix : ${fullChoiceIds.join(', ')}`);

   // Envoyer les données au serveur
    fetch('/track_attempts/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            question_name: questionName, // Nom unique de la question (q22, etc.)
            full_choice_ids: fullChoiceIds // IDs complets générés (par exemple : Anatomie2023_22_c)
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(`Données reçues du serveur : ${JSON.stringify(data)}`);

            // Mettre à jour l'état visuel des réponses correctes ou incorrectes
            if (data.is_correct) {
                console.log(`La réponse pour ${questionName} est correcte.`);
            } else {
                console.log(`La réponse pour ${questionName} est incorrecte.`);
            }

            // Supprimer les anciennes alertes et gérer les nouvelles si nécessaire
            handleAlert(data.alert, questionDiv);

            // Mettre à jour les statistiques comme les taux d'échec
            updateStatisticalAlerts(data, questionDiv);
        })
        .catch(error => {
            console.error('Erreur lors de l\'envoi des résultats au serveur :', error);
        });
}
"""
                    print(f"Nouvelle fonction `correctQuestion` ajoutée dans {file}.")

                # Écrire les modifications dans le fichier
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    modified_files.append(file)

            except Exception as e:
                print(f"Erreur lors du traitement du fichier {file}: {e}")

    print("\n=== Résumé ===")
    if modified_files:
        print(f"Fichiers modifiés : {', '.join(modified_files)}")
    else:
        print("Aucun fichier modifié.")

# Exécuter la fonction
process_files()
