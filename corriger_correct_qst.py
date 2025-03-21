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

                print(f"Traitement du fichier : {file}")

                # Vérifier si la fonction `correctQuestion` est déjà présente
                if "function correctQuestion(questionName)" in content:
                    # Supprimer l'ancienne fonction `correctQuestion`
                    content, num_replacements = re.subn(
                        r"// Fonction pour corriger une question\s+function correctQuestion\(.*?\}\n\}\n",
                        "",
                        content,
                        flags=re.DOTALL
                    )
                    if num_replacements > 0:
                        print(f"Ancienne fonction `correctQuestion` supprimée dans {file}.")
                else:
                    print(f"Aucune ancienne fonction `correctQuestion` trouvée dans {file}.")

                # Ajouter la nouvelle balise <script> contenant la fonction si elle n'est pas déjà présente
                new_script = """
<script>
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
            question_name: questionName,
            full_choice_ids: fullChoiceIds
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log(`Données reçues du serveur : ${JSON.stringify(data)}`);
            handleAlert(data.alert, questionDiv);
            updateStatisticalAlerts(data, questionDiv);
        })
        .catch(error => console.error('Erreur lors de l’envoi des données:', error));
}

// Fonction pour gérer les alertes
function handleAlert(alertData, questionDiv) {
    const existingAlert = questionDiv.querySelector('.alert-indicator');
    if (existingAlert) {
        existingAlert.remove();
    }

    if (alertData) {
        const alertIndicator = document.createElement('div');
        alertIndicator.className = 'alert-indicator';
        alertIndicator.style.backgroundColor = alertData.color || '#f8d7da';
        alertIndicator.style.padding = '10px';
        alertIndicator.style.marginTop = '10px';
        alertIndicator.style.borderRadius = '5px';
        alertIndicator.style.fontWeight = 'bold';
        alertIndicator.style.color = '#721c24';
        alertIndicator.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
        alertIndicator.textContent = alertData.message;

        questionDiv.appendChild(alertIndicator);
        saveAlertToLocalStorage(questionDiv.getAttribute('data-question-id'), alertData);
    } else {
        removeAlertFromLocalStorage(questionDiv.getAttribute('data-question-id'));
    }
}

// Charger les alertes persistantes
function loadAlertsFromLocalStorage() {
    const storedAlerts = JSON.parse(localStorage.getItem('alerts')) || {};
    Object.keys(storedAlerts).forEach(questionId => {
        const questionDiv = document.querySelector(`.question-container[data-question-id="${questionId}"]`);
        if (questionDiv) {
            handleAlert(storedAlerts[questionId], questionDiv);
        }
    });
}

// Sauvegarder les alertes dans localStorage
function saveAlertToLocalStorage(questionId, alertData) {
    const storedAlerts = JSON.parse(localStorage.getItem('alerts')) || {};
    storedAlerts[questionId] = alertData;
    localStorage.setItem('alerts', JSON.stringify(storedAlerts));
}

// Supprimer une alerte de localStorage
function removeAlertFromLocalStorage(questionId) {
    const storedAlerts = JSON.parse(localStorage.getItem('alerts')) || {};
    delete storedAlerts[questionId];
    localStorage.setItem('alerts', JSON.stringify(storedAlerts));
}

// Mise à jour des alertes statistiques
function updateStatisticalAlerts(data, questionDiv) {
    const existingStatisticalAlerts = questionDiv.querySelectorAll('.statistical-alert');
    existingStatisticalAlerts.forEach(alert => alert.remove());

    if (data.failure_rate > 0.6) {
        const failureRateAlert = document.createElement('div');
        failureRateAlert.className = 'statistical-alert';
        failureRateAlert.style.backgroundColor = '#add8e6';
        failureRateAlert.style.padding = '10px';
        failureRateAlert.style.marginTop = '10px';
        failureRateAlert.style.borderRadius = '5px';
        failureRateAlert.style.fontWeight = 'bold';
        failureRateAlert.style.color = '#004085';
        failureRateAlert.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
        failureRateAlert.textContent = `🔵 Votre taux d'échec est de ${(data.failure_rate * 100).toFixed(0)}%. Revoir cette question est conseillé.`;

        questionDiv.appendChild(failureRateAlert);
    }
}

// Charger les alertes au démarrage
document.addEventListener('DOMContentLoaded', () => {
    loadAlertsFromLocalStorage();
});

</script>
"""

                if new_script not in content:
                    content += "\n" + new_script
                    print(f"Nouvelle balise <script> ajoutée dans {file}.")
                else:
                    print(f"La nouvelle fonction `correctQuestion` est déjà présente dans {file}.")

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
