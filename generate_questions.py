import os
import re
import json



def remplacer_rd2019(contenu, nom_fichier):
    """
    Remplace toutes les occurrences de 'Rd2019' ou 'RD2019' par le nom du fichier.
    :param contenu: Texte à modifier.
    :param nom_fichier: Nom du fichier à utiliser pour le remplacement.
    :return: Contenu modifié.
    """
    return re.sub(r'\b[Rr][Dd]2019\b', nom_fichier, contenu)

def sauvegarder_reponses_correctes(correct_answers, nom_fichier):
    """
    Sauvegarde les réponses correctes dans un fichier JSON.
    :param correct_answers: Dictionnaire des réponses correctes.
    :param nom_fichier: Nom du fichier JSON à générer avec un incrément si déjà existant.
    """
    compteur = 1
    fichier_json = f"{nom_fichier}_correct_answers.json"
    while os.path.exists(fichier_json):
        fichier_json = f"{nom_fichier}_correct_answers_{compteur}.json"
        compteur += 1

    with open(fichier_json, "w", encoding="utf-8") as json_file:
        json.dump(correct_answers, json_file, ensure_ascii=False, indent=4)
    print(f"Fichier JSON '{fichier_json}' généré avec succès.")

def parse_correct_answers(answers_str):
    correct_answers = {}
    answers_list = answers_str.split()
    for i, answers in enumerate(answers_list, start=1):
        question_id = f"q{i}"
        correct_answers[question_id] = list(answers)
    return correct_answers

def generate_html_from_questions(questions, answers_str, js_file_path):
    
    nom_fichier = "VR_RUBIVIRUS"

    # Parse correct answers
    correct_answers = parse_correct_answers(answers_str)
    correct_answers_js = "const correctAnswers = {\n"
    for question_id, answers in correct_answers.items():
        answers_formatted = ", ".join(f"'{answer}'" for answer in answers)
        correct_answers_js += f"    {question_id}: [{answers_formatted}],\n"
    correct_answers_js += "};\n"

    # Lire le contenu du fichier JavaScript
    with open(js_file_path, "r", encoding="utf-8") as js_file:
        js_content = js_file.read()

    # Début du HTML output
    html_output = '''
<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Luck</title>
      {% load static %}
      <link rel="stylesheet" href="{% static 'css/stylequiz.css' %}"> </head>
    </head>
    <body>
        <div class="container">
            <div class="quiz-title">
                <h1>QCM Ophtalmologie</h1>
            </div>
            <form id="quiz-form">
                <input type="hidden" id='exam_name' name="exam_name" value="Rd2019">
    {% csrf_token %}
    '''

    # Génération des questions
    question_number = 1
    for question_text, options in questions:
        question_id = f"q{question_number}"

        # Format de chaque question en HTML
        question_html = f'''
        <div id="question-{question_number}" class="question-container">
            <div class="question">
                <p>{question_number}.) {question_text}</p>
                <ul>
        '''
        for i, option in enumerate(options):
            option_id = f"{question_id}{chr(97 + i)}"
            question_html += f'''
                    <li><input type="checkbox" id="{option_id}" name="{question_id}" value="{chr(65 + i)}"> {chr(65 + i)}- {option}</li>
            '''

        # Remplace directement les placeholders par `question_id` et `question_number`
        question_html += f'''
                </ul>
            </div>
            <div class="action-buttons">
                <button type="button" class="correct-button" onclick="correctQuestion('{question_id}')">Corriger</button>
                <button type="button" class="reset-button" onclick="resetQuestion('{question_id}')">Réessayer</button>
                <button class="favorite-button" data-question="{question_number}">&#10084;</button>
                <button class="comment-button" data-question-id="Rd2019_{question_number}" onclick="toggleCommentSection('Rd2019_{question_number}', event)"> 💬 <span class="badge" data-comment-id="Rd2019_{question_number}">
0
</span> </button>
            </div>
        </div>
        '''
        # Remplacer 'Rd2019' dans la question HTML
        question_html = remplacer_rd2019(question_html, "quiz_project")
        html_output += question_html
        question_number += 1

    # Ajout de la section après la dernière question
    html_output += '''
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
            <div id="details-section" style="display:none;">
               <h2>
Questions :
</h2>
               <div class="question-links" id="question-links"> </div>
            </div>
<div class="comments-section" id="comments-section">
    <h3>Commentaires</h3>
    <textarea id="new-comment" placeholder="Écrire un commentaire..."></textarea>
    <button type="button" onclick="addComment(event)">Ajouter</button>
    <div id="comment-alert" class="alert" style="display: none;"></div>
    <div id="comments-list"></div>
</div>

<!-- Boutons flottants -->
<div id="floating-buttons" class="floating-buttons" style="position: fixed; bottom: 50px; right: 50px; z-index: 1000;">
    <!-- Bouton pour afficher le cours -->
<button id="show-course-btn" class="floating-btn" type="button" 
        onclick="window.open('https://drive.google.com/drive/folders/1Xd_FaJbPk4FJv3G5-96L7G0UlQnUZuSf', '_blank');">📚</button>
    <!-- Bouton pour afficher le contact -->
<button id="open-contact-modal" class="floating-btn" type="button">
    ✉️
</button>

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

<script src="{% static 'java/contact.js' %}"></script>
    '''

    # Ajout des réponses correctes et inclusion du contenu du fichier JavaScript
    html_output += f'''
            <script>
                // Réponses correctes pour les questions
                {correct_answers_js}

                // Contenu du fichier JavaScript
                {js_content}
        </body>
    </html>
    '''

    with open(r"C:\Users\thinkup\Documents\QuizLuckProject\output.html", "w", encoding="utf-8") as f:
      f.write(html_output)

    print("HTML file has been generated successfully.")

# Exemple d'utilisation
questions = [

# 1
("Devant une otite séro-muqueuse, quels sont les indications de la pose d’un aérateur transtympanique ?",
 [
     "Un épisode de surinfection (otite moyenne aiguë) par an",
     "Retard de langage chez l’enfant",
     "Rétraction tympanique non évolutive",
     "Une fente vélo-palatine associée",
     "Une surdité de transmission supérieure à 30 dB"
 ]),

# 2
("Quel est le diagnostic le plus probable devant ce tableau clinique ?",
 [
     "Cholestéatome de l’oreille droite",
     "Otite externe nécrosante",
     "Paralysie faciale à Frigore",
     "Accident vasculaire cérébral",
     "Zona du nerf facial"
 ]),

# 3
("Quelles sont les bases de votre conduite diagnostique et thérapeutique ?",
 [
     "Prescrire une ordonnance à base d’antibiothérapie et d’antalgiques en ambulatoire et revoir le patient dans 48 heures",
     "Demander une TDM des rochers en coupes axiales et coronales",
     "Indiquer d’emblée une chirurgie d’évidemment pétro-mastoïdien de l’oreille droite",
     "Demander un bilan biologique complet comportant une glycémie à jeun, Hb A1c, bilan infectieux et bilan rénal",
     "Démarrer une antibiothérapie parentérale à large spectre en hospitalier"
 ]),

# 4
("Quelle est votre conduite à tenir pour ce nourrisson ?",
 [
     "Réaliser une paracentèse à visée antalgique",
     "Prescrire un traitement antipyrétique et antalgique associé à un lavage oculaire et nasal au sérum physiologique",
     "Prescrire des gouttes antibiotiques auriculaires",
     "Prescrire une antibiothérapie orale à base de céphalosporine de 1ère génération ou d’Amoxicilline à la dose de 80-90 mg/Kg/j pendant 8 jours",
     "Prescrire une antibiothérapie orale à base d’Amoxicilline-Acide clavulanique à la dose de 80 mg/kg/j pendant 8 à 10 jours"
 ]),

# 5
("Concernant les rhinosinusites, quelles sont les propositions vraies ?",
 [
     "La sinusite maxillaire est la forme la plus fréquente chez l’enfant",
     "Une rhinosinusite chronique se définit par des symptômes évoluant pendant plus de 3 mois",
     "Le diagnostic d’une sinusite maxillaire est basée sur la radiographie standard en incidence de Blondeau",
     "Le bilan radiologique est systématique devant une sinusite sphénoïdale",
     "La chirurgie est indiquée en première intention devant toute sinusite aiguë"
 ]),

# 6
("Parmi les signes cliniques suivants, quels sont ceux qui doivent alarmer et faire penser à une complication devant une Rhinosinusite ?",
 [
     "Diplopie",
     "Une rhinorrhée purulente",
     "Les céphalées matinales",
     "Œdème palpébral ou des parties molles de la face",
     "Exophtalmie"
 ]),

# 7
("Quels sont les deux diagnostics les plus probables pour des vertiges récurrents associés à des acouphènes et une surdité du côté droit ?",
 [
     "La maladie de Ménière",
     "Le cholestéatome de l’oreille moyenne",
     "Accident vasculaire cérébral",
     "Le schwanome vestibulaire",
     "La névrite vestibulaire"
 ]),

# 8
("S’il s’agit d’une maladie de Ménière débutante, quels sont les éléments qu’on va retrouver à l’examen clinique ?",
 [
     "Un nystagmus vers le côté droit",
     "Un nystagmus vers le côté gauche",
     "Des déviations segmentaires vers le côté droit",
     "Des déviations segmentaires vers le côté gauche",
     "Signe d’Halmagyi négatif : le regard reste fixé sur la cible"
 ]),

# 9
("Quel traitement proposez-vous à ce patient atteint de maladie de Ménière ?",
 [
     "Un traitement médical",
     "Des manœuvres libératoires thérapeutiques",
     "Une rééducation vestibulaire ultérieure si nécessaire",
     "Un traitement chirurgical",
     "Des injections intra-tympaniques de corticoïdes en cas d’échec"
 ]),

# 10
("Quelle est votre conduite à tenir devant un cholestéatome suspecté ?",
 [
     "Examen otoscopique au microscope",
     "IRM des rochers",
     "L’audiométrie tonale liminaire (audiogramme)",
     "Traitement chirurgical d’emblée",
     "TDM des rochers"
 ]),

# 11
("Le bilan montre un cholestéatome de l’oreille moyenne très limité. Quel(s) traitement(s) proposez-vous à ce patient ?",
 [
     "Un traitement médical",
     "Un traitement chirurgical",
     "Si chirurgie, une technique fermée est indiquée",
     "Si chirurgie, une technique ouverte est indiquée",
     "La réhabilitation de l’audition si nécessaire"
 ]),

# 12
("Quelle est votre conduite diagnostique devant une dysphonie chronique de 6 mois ?",
 [
     "Rechercher les facteurs de risque d’un cancer des VADS",
     "Prescrire un traitement médical seul",
     "Faire une Nasofibroscopie",
     "Faire une TDM du larynx si nécessaire",
     "Faire une laryngoscopie en suspension avec biopsies si nécessaire"
 ]),

# 13
("Le bilan montre un carcinome épidermoïde des 3 étages avec fixité du larynx et des adénopathies latéro-cervicales. Que proposez-vous à ce patient ?",
 [
     "Faire un bilan préthérapeutique",
     "Le traitement médical seul",
     "Un curage ganglionnaire",
     "Une laryngectomie totale",
     "Une laryngectomie partielle"
 ]),

# 14
("Quelle(s) est (sont) parmi ces tuméfactions celle(s) pouvant être de siège cervical antérieur ?",
 [
     "Kyste du tractus thyréoglosse",
     "Tumeur du pôle inférieur de la parotide",
     "Adénopathie métastatique des voies aérodigestives supérieures",
     "Nodule thyroïdien",
     "Lipome"
 ]),

# 15
("L’interrogatoire dans le cadre du bilan étiologique d’une épistaxis doit rechercher la notion de :",
 [
     "Hypertension artérielle connue",
     "Prise de Vitamine K",
     "Consommation de cocaïne",
     "Consommation de Vitamine D",
     "Chirurgie endonasale"
 ]),
# 16
("La gravité d’une épistaxis est appréciée sur :",
 [
     "Uniquement par l’abondance de l’épistaxis",
     "L’abondance, la répétition, la persistance (continuité) de l’épistaxis",
     "L’état clinique du patient",
     "La mesure de la pression artérielle",
     "Le bilan biologique"
 ]),

# 17
("Une obstruction nasale :",
 [
     "Peut être à l’origine, chez le nouveau-né, d’une détresse respiratoire aiguë imposant une prise en charge rapide.",
     "Peut être à l’origine d’une respiration buccale avec sécheresse buccale.",
     "Peut être à l’origine d’une mauvaise aération de l’oreille moyenne et des sinus.",
     "Peut avoir un rôle bénéfique sur le développement facial chez l’enfant.",
     "Peut être à l’origine d’un trouble de l’odorat et du goût et trouble de l’appétit."
 ]),

# 18
("La classification échographique EU-TIRADS (European Union-Thyroid Imaging And Data System) :",
 [
     "Comprend 5 catégories de réponses.",
     "Permet d’homogénéiser les descriptions échographiques.",
     "Permet d’homogénéiser la conduite à tenir thérapeutique.",
     "Permet d’évaluer le risque de malignité.",
     "Suffit à elle seule pour prendre une décision chirurgicale."
 ]),

# 19
("Quel diagnostic retenir en premier ?",
 [
     "Pharyngite",
     "Angine virale non compliquée",
     "Angine virale compliquée",
     "Angine bactérienne non compliquée",
     "Angine bactérienne compliquée"
 ]),

# 20
("Quelle complication suppurative de l’angine peut-on redouter ?",
 [
     "Le rhumatisme articulaire aigu (RAA) = maladie de Bouillaud.",
     "La glomérulonéphrite aiguë (GNA) post-streptococcique.",
     "Le phlegmon péri-amygdalien",
     "Le syndrome de choc toxique.",
     "La scarlatine"
 ]),

# 21
("Quel(s) est(sont) Le (les) diagnostic(s) à évoquer cliniquement en premier chez ce patient ?",
 [
     "Un aphte.",
     "Un carcinome épidermoïde de la face interne de la joue.",
     "Une candidose buccale.",
     "Une leucoplasie de la face interne de la joue.",
     "Un lichen plan de la face interne de la joue."
 ]),

# 22
("Pour confirmer le diagnostic, quel(s) est(sont) le(les) examen(s) à demander ?",
 [
     "La tomodensitométrie.",
     "L’IRM.",
     "Le PET scan.",
     "La biopsie de la lésion.",
     "L’examen mycologique."
 ]),

# 23
("Quelle est la cause probable de la diplopie ?",
 [
     "Une lésion du muscle releveur de la paupière supérieure.",
     "Une atteinte du nerf infra-orbitaire.",
     "Une incarcération du muscle droit médial.",
     "Une incarcération du muscle droit inférieur.",
     "Une paralysie du nerf facial (VII)."
 ]),

# 24
("Quel est le diagnostic le plus probable ?",
 [
     "Une fracture orbito-nasale.",
     "Une fracture du plancher de l’orbite avec incarcération musculaire.",
     "Une fracture Lefort I.",
     "Une fracture orbito-zygomatique.",
     "Une fracture Lefort II."
 ]),

# 25
("Devant ce tableau clinique, Quel(s) est(sont) le(les) diagnostic(s) à évoquer ?",
 [
     "Une cellulite cervico-faciale.",
     "Une tumeur mandibulaire.",
     "Une adénite.",
     "Une lithiase sous mandibulaire.",
     "Un accident d’éruption de la dent de sagesse."
 ]),

# 26
("En l’absence de traitement, quelles sont les complications possibles chez ce patient ?",
 [
     "Une ostéite mandibulaire",
     "Une métastase à distance",
     "Une sous-mandibulite.",
     "Un abcès du plancher buccal.",
     "Un phlegmon amygdalien."
 ]),

# 27
("Quelles sont les causes locales du trismus ?",
 [
     "Le cancer de la commissure intermaxillaire.",
     "La péricoronarite de la dent de sagesse.",
     "Le phlegmon amygdalien.",
     "La rétraction cicatricielle.",
     "L’ankylose temporo-mandibulaire."
 ]),

# 28
("Quels sont les signes de gravité d’une cellulite cervico-faciale ?",
 [
     "L’odynophagie.",
     "La dysphonie.",
     "La fistule cutanée.",
     "La tuméfaction jugale qui ferme l’œil.",
     "La tuméfaction sus-hyoïdienne."
 ]),

# 29
("Quels sont les signes évoquant une tumeur maxillaire ?",
 [
     "Le déplacement des dents.",
     "L’obstruction nasale.",
     "L’image en géode sur la radio panoramique.",
     "L’exophtalmie.",
     "Les bruits articulaires."
 ]),

# 30
("Quels sont les facteurs favorisant la luxation temporo-mandibulaire ?",
 [
     "L’âge jeune.",
     "L’alimentation molle.",
     "Les anomalies de l’articulé dentaire.",
     "L’hyperlaxité ligamentaire.",
     "La malformation osseuse mandibulaire."
 ]),






]

answers_str = "BDE  B  BDE  BE  BD  ADE  AD  AD  ACE  ACE  BCE  ACDE  ACD  ADE  ACE  BCDE  ABCE  ABCD  E  C  B  D  D  B  D  CD  ABC  ADE  ABCD  CDE"
js_file_path = r"C:\\Users\\thinkup\\Documents\\QuizLuckProject\\pythonjava.js"  # Chemin complet vers votre fichier JavaScript

generate_html_from_questions(questions, answers_str, js_file_path)
