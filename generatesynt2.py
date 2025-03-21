import os
import re

# Contenu HTML à ajouter au début
html_header = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Luck</title>
    {% load static %}
<link rel="stylesheet" href="{% static 'css/stylesynt.css' %}">


</head>
<body>

<div id="score-container" class="score-container">
    <h3>Note : <span id="score">0 / <span id="total-questions"</span></h3>
</div>

        <div class="quiz-title">
            <h1>Resultats detail</h1>

         <!-- Conteneur des cercles -->
    <div class="circle-container" id="circle-container">
        <!-- Les cercles seront générés ici par JavaScript -->
    </div>


<input type="hidden" name="file_name" value="Rd2022">
'''

# Contenu à remplacer dans le HTML d'origine
old_content = '''
 <div class="button-container">
               <button class="submit-quiz-button" onclick="submitQuiz()" type="button"> Soumettre tout le Quiz </button>
               <button class="favorite-button" id="voir-favoris-btn" onclick="voirFavoris()"> Voir Favoris </button>
               <!-- Nouveau bouton -->
            </div>
            <div class="blur-background" id="blur-background"> </div>
            <div class="result-popup" id="result-popup">
               <h3>
Résultat du Quiz
</h3>
               <div id="result"> </div>
               <button class="close-button" id="close-result" onclick="closeResult(event)"> Fermer </button>
               <button class="detail-button" id="voir-detail-btn" onclick="afficherDetails(event)" style="display: none;"> Voir Détail </button>
               <button class="reset-quiz-button" onclick="resetAll()" type="button"> Réessayer tout le Quiz </button>
            </div>
            <div class="details-section" id="details-section" style="display: none;">
               <h3>
Tableau des questions
</h3>
               <div class="question-links" id="question-links"> </div>
            </div>
            <div id="timer-container"> <span id="timer">
60:00
</span> </div>
<div class="comments-section" id="comments-section">
    <h3>Commentaires</h3>
    <textarea id="new-comment" placeholder="Écrire un commentaire..."></textarea>
    <button type="button" onclick="addComment(event)">Ajouter</button>
    <div id="comment-alert" class="alert" style="display: none;"></div>
    <div id="comments-list"></div>
</div>

    <div id="comments-list"></div>
</div>

<!-- Boutons flottants -->
<div id="floating-buttons" class="floating-buttons" style="position: fixed; bottom: 50px; right: 50px; z-index: 1000;">
    <!-- Bouton pour afficher le cours -->
    <button id="show-course-btn" class="floating-btn" type="button" 
            onclick="event.stopPropagation(); event.preventDefault(); toggleIframeSection(event)">📚</button>
    <!-- Bouton pour afficher le contact -->
<button id="open-contact-modal" class="floating-btn" type="button">
    ✉️
</button>

</div>

<!-- Section pour afficher le PDF via iframe -->
<div id="pdf-iframe-section" 
     style="display: none; position: fixed; top: 0; right: 0; height: 100%; width: 30%; background: white; box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1); z-index: 1000; overflow: hidden; transition: width 0.3s, transform 0.3s;">
    <!-- Barre de contrôle pour redimensionnement -->
    <div style="background: #f0f0f0; padding: 10px; display: flex; align-items: center; justify-content: space-between;">
        <label for="iframe-width-input" style="margin-right: 10px; font-size: 14px;">Largeur (en % ou px) :</label>
        <input id="iframe-width-input" type="text" placeholder="e.g., 50% ou 500px" 
               style="padding: 5px; border: 1px solid #ccc; border-radius: 4px; width: 100px;">
        <button id="iframe-width-btn" type="button" 
                onclick="event.stopPropagation(); event.preventDefault(); applyIframeWidth()"
                style="margin-left: 10px; padding: 5px 10px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer;">
            Appliquer
        </button>
    </div>

    <!-- Iframe -->
    <iframe id="pdf-iframe" 
            src="/static/Cours/Myologie _Oussama Essahili.pdf" 
            style="width: 100%; height: calc(100% - 40px); border: none;" 
            title="Cours">
    </iframe>
</div>

<!-- Barre pour redimensionner la largeur avec le curseur -->
<div id="resize-handle" 
     style="width: 5px; height: 100%; cursor: ew-resize; position: fixed; top: 0; right: 30%; background-color: rgba(0, 0, 0, 0.2); z-index: 1001; display: none;"
     onmousedown="event.stopPropagation(); event.preventDefault(); initResize(event)">
</div>



<div class="message-container" id="message-container" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); background:#f9f9f9; padding:40px; box-shadow:0 4px 12px rgba(0,0,0,0.15); border-radius:12px; z-index:1001; width:600px; max-width:90%; font-family:Arial, sans-serif;">
    <div style="text-align:center; margin-bottom:30px;">
        <h2 style="margin:0; font-size:24px; font-weight:bold; color:#333;">Posez vos observations <span>📝</span></h2>
        <p style="margin:10px 0 0; font-size:16px; color:#666;">Nous sommes à votre écoute</p>
    </div>
    <div class="mb-3" style="margin-bottom:30px;">
        <p style="font-size:16px; color:#333; margin:0;">En tant Que :</p>
        <div style="margin-top:10px;">
            <input type="radio" id="username" name="mode" value="username" style="margin-right:8px;">
            <label for="username" style="font-size:16px; color:#333; cursor:pointer;">{{ user.username }}</label>
            <br>
            <input type="radio" id="anonymous" name="mode" value="anonymous" checked style="margin-right:8px; margin-top:10px;">
            <label for="anonymous" style="font-size:16px; color:#333; cursor:pointer;">Anonyme</label>
        </div>
    </div>
    <div class="mb-3">
        <label for="message" class="form-label" style="font-size:18px; font-weight:bold; color:#333; margin-bottom:10px; display:block;">Votre message :</label>
        <textarea class="form-control" id="message" rows="6" placeholder="Precisez l'examen si c'est en rapport avec une question..." style="width:100%; font-size:16px; padding:15px; border:1px solid #ccc; border-radius:8px; box-shadow:inset 0 1px 3px rgba(0,0,0,0.1); background:#fff;"></textarea>
    </div>
<span class="close-btn" id="close-btn" style="cursor:pointer; position:absolute; top:15px; right:15px; font-size:51px; color:#ff0000; font-weight:bold;">&times;</span>
<!-- Bouton Envoyer stylé -->
<div style="text-align:center; margin-top:30px;">
    <button type="button" class="btn btn-primary" id="send-message" style="background-color:#007bff; color:white; border:none; padding:12px 30px; border-radius:8px; font-size:18px; font-weight:bold; cursor:pointer; box-shadow:0 4px 8px rgba(0, 0, 0, 0.2); transition:all 0.3s ease;">
        Envoyer
    </button>
</div>
</div>




<div id="blur-overlay" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:1000;"></div>

<script src="{% static 'java/cours.js' %}"></script>

<script src="{% static 'java/contact.js' %}"></script>

'''

# Nouveau contenu à insérer
new_content = '''
            </div>
<button type="button" class="reset-quiz-button" onclick="window.location.href = '{% url "dynamic_view" "S5" "Radiologie" "Rd2022" %}';">Réessayer tout le Quiz</button>

            <div id="details-section" class="details-section" style="display: none;">
                <h3>Tableau des questions</h3>
                <div class="question-links" id="question-links"></div>
            </div>

<script>
let loadedAnswers = {};  // Variable globale pour stocker les réponses chargées      
window.onload = function() {
    loadUserAnswersFromAnatomie(); // Charger les réponses d'Anatomie2023
    generateCircles(); // Générer les cercles
    evaluateQuiz(); // Mettre à jour les cercles en fonction des réponses
};
</script>
'''

# Contenu HTML à ajouter à la fin
html_footer = '''
let userAnswers = {}; // Stocke les réponses de l'utilisateur
let loadedAnswers = {}; // Stocke les réponses chargées pour l'évaluation

// Charger les réponses utilisateur
function loadUserAnswersFromChimie() {
    const savedAnswers = JSON.parse(localStorage.getItem('userAnswersRd2022'));

    if (savedAnswers) {
        loadedAnswers = savedAnswers; // Stocker les réponses dans la variable globale
        for (const [questionName, answerData] of Object.entries(savedAnswers)) {
            const questionDiv = document.querySelector(`input[name="${questionName}"]`)?.closest('.question-container');
            if (!questionDiv) continue;

            // Appliquer les styles pour les bonnes réponses
            correctAnswers[questionName]?.forEach(correctAnswer => {
                const correctLi = questionDiv.querySelector(`input[value="${correctAnswer}"]`)?.closest('li');
                if (correctLi) {
                    correctLi.style.color = 'green';
                    correctLi.style.fontWeight = 'bold';
                    correctLi.style.textShadow = '1px 1px 2px rgba(0, 0, 0, 0.5)';
                }
            });

            // Appliquer les styles pour les réponses sélectionnées
            answerData.selected.forEach(selectedAnswer => {
                const selectedLi = questionDiv.querySelector(`input[value="${selectedAnswer}"]`)?.closest('li');
                if (selectedLi) {
                    selectedLi.style.color = correctAnswers[questionName]?.includes(selectedAnswer) ? 'lightgreen' : 'red';
                }
            });

            // Désactiver les cases après chargement
            questionDiv.querySelectorAll('input').forEach(input => (input.disabled = true));
        }
    }
}

// Générer les cercles pour les questions
function generateCircles() {
    const totalQuestions = Object.keys(correctAnswers).length;
    const circleContainer = document.getElementById('circle-container');

    for (let i = 1; i <= totalQuestions; i++) {
        const circle = document.createElement('div');
        circle.classList.add('circle', 'yellow'); // Couleur par défaut : jaune
        circle.innerText = i;

        circle.onclick = function () {
            scrollToQuestion(i);
        };

        circleContainer.appendChild(circle);
    }
}

// Mettre à jour les cercles après évaluation
function updateCircles() {
    const circles = document.querySelectorAll('.circle');
    let totalCorrectCircles = 0; // Compteur pour les réponses correctes
    for (let i = 1; i <= Object.keys(correctAnswers).length; i++) {
        const selectedAnswers = loadedAnswers[`q${i}`]?.selected || [];
        const circle = circles[i - 1];

        if (JSON.stringify(correctAnswers[`q${i}`]?.sort()) === JSON.stringify(selectedAnswers.sort())) {
            circle.classList.add('green');
            circle.classList.remove('yellow', 'red');
            totalCorrectCircles++;
        } else if (selectedAnswers.length > 0) {
            circle.classList.add('red');
            circle.classList.remove('yellow', 'green');
        } else {
            circle.classList.add('yellow');
            circle.classList.remove('green', 'red');
        }
    }

    // Mettre à jour la note avec le nombre de cercles verts
    document.getElementById('score').textContent = `${totalCorrectCircles} / ${Object.keys(correctAnswers).length}`;
}

// Défiler jusqu'à une question spécifique
function scrollToQuestion(questionNumber) {
    const questionDiv = document.getElementById(`question-${questionNumber}`);
    if (questionDiv) {
        questionDiv.scrollIntoView({ behavior: 'smooth' });
    }
}

// Charger les réponses et générer les cercles au chargement de la page
window.onload = function () {
    document.getElementById('total-questions').textContent = Object.keys(correctAnswers).length; // Nombre total de questions
    loadUserAnswersFromChimie();
    generateCircles();
    updateCircles();
};




    </script>
</body>
</html>
<script src="{% static 'java/question-stats.js' %}" defer></script>
'''
def remove_doctype_and_head(content):
    """
    Supprime tout le contenu depuis <!DOCTYPE html> jusqu'à la fermeture de </head>.
    """
    return re.sub(r'<!DOCTYPE html>.*?</head>', '', content, flags=re.DOTALL)


def remove_action_buttons_and_section(content):
    """
    Supprime les sections inutiles comme les boutons et autres balises spécifiques.
    """
    # Supprimer les boutons sous chaque question (<div class="action-buttons">)
    content = re.sub(r'<div class="action-buttons">.*?</div>', '', content, flags=re.DOTALL)

    # Supprimer les blocs contenant des boutons spécifiques (<div class="button-container">)
    content = re.sub(r'<div class="button-container">.*?</div>', '', content, flags=re.DOTALL)

    # Supprimer d'autres boutons individuels si nécessaire
    content = re.sub(r'<button[^>]*class="close-button"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
    content = re.sub(r'<button[^>]*class="detail-button"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
    content = re.sub(r'<button[^>]*class="reset-quiz-button"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
    content = re.sub(r'<button[^>]*class="comment-button"[^>]*>.*?</button>', '', content, flags=re.DOTALL)


   # Supprimer le conteneur du timer (<div id="timer-container">)
    content = re.sub(r'<div id="timer-container">.*?</div>', '', content, flags=re.DOTALL)

    # Supprimer le fond flouté (blur-background)
    content = re.sub(r'<div class="blur-background" id="blur-background">.*?</div>', '', content, flags=re.DOTALL)

    # Supprimer le popup de résultat (result-popup)
    content = re.sub(r'<div class="result-popup" id="result-popup">.*?</div>', '', content, flags=re.DOTALL)

    return content


def extract_correct_answers(content):
    """
    Conserve uniquement la section contenant 'const correctAnswers = {...};'
    et supprime la fermeture de la balise </script> juste après.
    """
    # Trouver 'const correctAnswers = {...};' et supprimer la fermeture </script>
    match = re.search(r'const correctAnswers = \{.*?\};', content, re.DOTALL)
    if match:
        # Retourner uniquement le bloc correctAnswers sans la fermeture </script>
        return f"<script>\n{match.group(0)}\n"  # Supprime </script>
    return ''  # Si rien n'est trouvé, retourner une chaîne vide


def remove_unwanted_js(content):
    """
    Supprime tout le JavaScript après 'const correctAnswers = {...};', mais conserve le contenu HTML.
    """
    # Trouver la fin de 'const correctAnswers' et tout supprimer après
    split_content = re.split(r'<script>.*?const correctAnswers = \{.*?\};.*?</script>', content, flags=re.DOTALL)
    if len(split_content) > 1:
        # Retourner la partie avant le JavaScript inutile
        return split_content[0]  # Conserve le HTML sans le JS inutile
    return content  # Si rien n'est trouvé, retourner tout le contenu d'origine


def generate_html(input_html_content, original_filename):
    """
    Génère un nouveau fichier HTML avec uniquement les sections utiles et les questions.
    Remplace 'userAnswersChimie2023' par un nom basé sur le fichier.
    """
    # Étape 1 : Extraire le nom de base du fichier sans extension
    base_filename = os.path.splitext(original_filename)[0]

    # Étape 2 : Remplacer 'userAnswersChimie2023' par 'userAnswers<base_filename>'
    dynamic_content = re.sub(
        r'userAnswersChimie2023',
        f'userAnswers{base_filename}',
        input_html_content
    )

    # Étape 3 : Supprimer <!DOCTYPE html> à </head>
    cleaned_content = remove_doctype_and_head(dynamic_content)

    # Étape 4 : Supprimer les boutons spécifiques et les rubriques inutiles
    cleaned_content = remove_action_buttons_and_section(cleaned_content)

    # Étape 5 : Supprimer le JavaScript inutile tout en conservant le HTML
    html_with_questions = remove_unwanted_js(cleaned_content)

    # Étape 6 : Ajouter un bouton pour réessayer après la dernière question
    retry_button = f'<button type="button" class="reset-quiz-button" onclick="window.location.href=\'{base_filename}.html\'"><b>Réessayer tout le Quiz</b></button>'
    html_with_questions = re.sub(
        r'(</div>\s*</div>\s*</div>)',  # Trouver la fermeture de la dernière question
        fr'\1\n{retry_button}',        # Ajouter le bouton juste après
        html_with_questions,
        flags=re.DOTALL
    )

    # Étape 7 : Extraire uniquement les réponses correctes
    correct_answers_section = extract_correct_answers(cleaned_content)

    # Étape 8 : Mettre à jour le footer pour inclure le nom dynamique
    html_footer_dynamic = html_footer.replace("{base_filename}", base_filename)

    # Contenu complet du fichier HTML avec header, questions, réponses correctes et footer
    full_html_content = html_header + html_with_questions + correct_answers_section + html_footer_dynamic

    # Créer le nom de fichier en ajoutant "synt" au nom original sans l'extension
    output_filename = f"synt{base_filename}.html"

    # Écriture dans un nouveau fichier
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(full_html_content)

    print(f"Fichier généré : {output_filename}")



def main():
    """
    Point d'entrée principal pour traiter tous les fichiers HTML dans le dossier spécifié.
    """
    # Chemin du répertoire contenant les fichiers HTML d'entrée
    input_directory = "./input_html_files"

    # Vérifier si le dossier de sortie existe, sinon le créer
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)

    # Obtenir tous les fichiers HTML dans le répertoire
    html_files = [f for f in os.listdir(input_directory) if f.endswith('.html')]

    # Parcourir chaque fichier HTML et le traiter
    for html_file in html_files:
        # Lire le contenu HTML original
        with open(os.path.join(input_directory, html_file), 'r', encoding='utf-8') as file:
            original_html_content = file.read()

        # Générer un fichier HTML modifié
        generate_html(original_html_content, html_file)


# Exécution du script principal
if __name__ == "__main__":
    main()
