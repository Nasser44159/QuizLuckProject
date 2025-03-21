def generate_html_from_questions(questions, js_file_path):
    # Lire le contenu du fichier JavaScript
    try:
        with open(js_file_path, "r", encoding="utf-8") as js_file:
            js_content = js_file.read()
    except FileNotFoundError:
        print(f"JavaScript file not found: {js_file_path}")
        js_content = "// JavaScript file not found. Ensure the file path is correct.\n"


        
    # Début du HTML output
    html_output = '''
    <!DOCTYPE html>
    <html lang="fr">
    
      <head>
        <meta charset="utf-8" />
        <meta content="width=device-width, initial-scale=1.0" name="viewport" />
        <title>
          Quiz Luck
        </title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/stylequiz.css' %}">
    
      </head>
    
      <body>
        <div class="container">
          <div class="quiz-title">
            <h1>
         Traumotologie 2020
        </h1>
            <p>
            </p>
          </div>
          <form id="quiz-form">
    {% csrf_token %}
        <input type="hidden" id='exam_name' name="exam_name" value="Anatomie2020RP">
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
                <ul class="answers">
        '''
        for i, option in enumerate(options):
            # Ensure the checkbox matches the requested structure
            question_html += f'''
                    <li>
                        <input name="{question_id}" type="checkbox" value="{chr(65 + i)}" /> {chr(65 + i)}- {option}
                    </li>
            '''

        question_html += f'''
                </ul>
            </div>
            <div class="action-buttons">
                <button class="correct-button" onclick="correctAndSubmitQuestion('{question_id}')" type="button">Corriger</button>
                <button class="reset-button" onclick="resetQuestion('{question_id}')" type="button">Réessayer</button>
                <button class="favorite-button" data-question="{question_number}">
                  ❤
                </button>
                <button class="comment-button" data-question-id="Anatomie2020RP_{question_number}" onclick="toggleCommentSection('Anatomie2020RP_{question_number}', event)">
                  💬
                  <span class="badge" data-comment-id="Anatomie2020RP_{question_number}">0</span>
                </button>
            </div>
        </div>
        '''
        html_output += question_html
        question_number += 1

    # Ajout de la section après la dernière question
    html_output += '''
 <div class="button-container">
               <!-- Bouton pour soumettre tout le quiz -->
               <button class="submit-quiz-button" onclick="submitQuiz()" type="button"> Soumettre tout le Quiz </button>
               <button class="favorite-button" id="voir-favoris-btn" onclick="voirFavoris()"> Voir Favoris </button>
            </div>
            <!-- Fond flouté pour l'effet d'arrière-plan -->
            <div class="blur-background" id="blur-background"> </div>
            <!-- Popup de résultat -->
            <div class="result-popup" id="result-popup">
               <h3>
Résultat du Quiz
</h3>
               <div id="result"> </div>
               <button class="close-button" id="close-result" onclick="closeResult(event)"> Fermer </button>
               <button class="detail-button" id="voir-detail-btn" onclick="afficherDetails(event)" style="display: none;"> Voir Détail </button>
               <button class="reset-quiz-button" onclick="resetAll()" type="button"> Réessayer tout le Quiz </button>
            </div>
         </form>
      </div>
      <div class="details-section" id="details-section" style="display: none;">
         <h3>
Tableau des questions
</h3>
         <div class="question-links" id="question-links"> </div>
      </div>
      <!-- Conteneur du timer -->
      <div id="timer-container"> <span id="timer">
60:00
</span> </div>
      <!-- Section pour afficher le tableau avec les numéros encerclés -->
      <div id="details-section" style="display:none;">
         <h2>
Questions :
</h2>
         <div class="question-links" id="question-links">
            <!-- Le tableau de numéros va être généré ici -->
         </div>
      </div>
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

        # Ajouter le contenu JavaScript au script intégré
    html_output += f"{js_content}\n"

    with open(r"C:\Users\thinkup\Documents\QuizLuckProject\output.html", "w", encoding="utf-8") as f:
        f.write(html_output)

    print("HTML file has been generated successfully.")

# Exemple d'utilisation
questions = [
    # 1
("Le cervelet assure un rôle :",
    [
        "Sensitif",
        "Sensoriel",
        "Moteur",
        "Végétatif",
        "D’équilibre"
    ]),

# 2
("Le cervelet établit des connexions avec le cerveau grâce :",
    [
        "Aux pédoncules cérébraux",
        "Aux pédoncules cérébelleux supérieurs",
        "À la moelle épinière",
        "À l’olive bulbaire",
        "Aux pédoncules cérébelleux antérieurs"
    ]),

# 3
("Dans la configuration interne du cervelet :",
    [
        "La substance blanche est corticale",
        "La substance grise est corticale",
        "Il existe 4 paires de noyaux gris centraux",
        "La cellule de Purkinje est spécifique au cervelet",
        "Il existe 2 paires de noyaux gris centraux"
    ]),

# 4
("Le cervelet se situe au niveau de :",
    [
        "L’étage antérieur",
        "L’étage moyen",
        "La selle turcique",
        "La fosse cérébrale postérieure",
        "La fosse temporale"
    ]),

# 5
("L’hypophyse est situé au niveau :",
    [
        "De la tente du cervelet",
        "Du sinus sphénoïdal",
        "De la selle turcique",
        "De l’étage antérieur",
        "De l’étage postérieur"
    ]),

# 6
("L’hypophyse assure un rôle :",
    [
        "Moteur",
        "Sensitif",
        "Végétatif",
        "Neuroglandulaire",
        "Sensoriel"
    ]),

# 7
("L’hypophyse :",
    [
        "Est composée de 4 parties différentes",
        "Est réniforme",
        "A un aspect homogène",
        "Est recouverte par l’arachnoïde",
        "Est recouverte par la pie mère"
    ]),

# 8
("L’antéhypophyse :",
    [
        "Est réniforme",
        "A une couleur grisâtre",
        "Sécrète de l’ocytocine",
        "De situation postérieure",
        "D’origine embryonnaire nerveuse"
    ]),

# 9
("La neurohypophyse :",
    [
        "Est de couleur jaune chamois",
        "De situation postérieure",
        "Sécrète la prolactine",
        "Est composée de tissu glandulaire",
        "Sécrète de la prostaglandine"
    ]),

# 10
("Les connexions hypothalamo-hypophysaires :",
    [
        "Permettent le contrôle du fonctionnement de l’hypophyse",
        "Ont toujours un rôle freinater",
        "Sont assurées par le système porte",
        "Sont assurées par des connexions nerveuses",
        "Sont végétatives"
    ]),

# 11
("Le thalamus :",
    [
        "Est le plus gros noyau gris central",
        "Est formé uniquement par la substance blanche",
        "A une situation superficielle",
        "A une forme ronde",
        "Est parcouru par la lame médullaire interne"
    ]),

# 12
("Les rapports importants du thalamus sont :",
    [
        "Le lobe frontal en bas",
        "Le lobe temporal",
        "La capsule interne",
        "Le tronc cérébral en haut",
        "Le troisième ventricule en dedans"
    ]),

# 13
("Le thalamus assure un rôle :",
    [
        "Hormonal",
        "Dans la déglutition",
        "Dans la motricité extrapyramidale",
        "Dans la vision",
        "Dans l’audition"
    ]),

# 14
("Dans les noyaux gris centraux :",
    [
        "Le noyau caudé a une forme triangulaire",
        "Le noyau lenticulaire a une forme en arc",
        "Le noyau lenticulaire est superficiel",
        "Le locus Niger ne fait pas partie de ces noyaux",
        "Ont un rôle dans la motricité extrapyramidale"
    ]),

# 15
("L’hypothalamus :",
    [
        "Est une zone peu fonctionnelle",
        "A la taille d’un pois chiche",
        "Assure un rôle végétatif",
        "A un rôle moteur",
        "Est divisé en 5 groupes de noyaux"
    ]),

# 16
("L’épiphyse :",
    [
        "Est un noyau gris central",
        "Est située en bas de l’hypophyse",
        "A des rapports avec les tubercules quadrijumeaux",
        "Sécrète l’hormone de croissance",
        "Sécrète la mélatonine"
    ]),

# 17
("Le système ventriculaire :",
    [
        "Assure un rôle d’amortisseur",
        "Est composé de 4 cavités",
        "Est de situation corticale",
        "A une paroi épendymaire",
        "Comprend les plexus choroïdes"
    ]),

# 18
("Le système ventriculaire est en communication avec :",
    [
        "Le tronc cérébral",
        "Le canal épendymaire",
        "Les noyaux gris centraux",
        "Le thalamus",
        "Le lobe occipital"
    ]),

# 19
("L’aqueduc de Sylvius fait communiquer :",
    [
        "La 3e ventricule avec les ventricules latéraux",
        "Les 2 ventricules latéraux",
        "Le 3e et le 4e ventricule",
        "Les ventricules latéraux avec le 4e ventricule",
        "Le 4e ventricule avec le canal épendymaire"
    ]),

# 20
("Le liquide céphalorachidien :",
    [
        "Est résorbé par les granulations de Pacchioni",
        "Se renouvelle une seule fois par jour",
        "A une composition constante même en cas de méningite",
        "Est résorbé par le plexus choroïde",
        "Est sécrété par le plexus choroïde"
    ]),

# 21
("Le liquide céphalorachidien :",
    [
        "A un rôle nutritif",
        "Véhicule les neurotransmetteurs",
        "A un rôle végétatif",
        "A un rôle moteur",
        "A un rôle sensoriel"
    ]),

# 22
("Dans le bulbe, le trou borgne de Vicq d’Azyr est interrompu en bas par l’entrecroisement des fibres :",
    [
        "Auditives",
        "Visuelles",
        "Des faisceaux pyramidaux",
        "Des faisceaux sensitifs lemniscaux",
        "Des faisceaux sensitifs extra lemniscaux"
    ]),

# 23
("Du sillon collatéral antérieur du bulbe naît le nerf :",
    [
        "Olfactif",
        "Optique",
        "Oculomoteur commun",
        "Glossopharyngien",
        "Grand hypoglosse"
    ]),

# 24
("Les limites inférieures de la protubérance sont :",
    [
        "Le mésencéphale",
        "La moelle épinière",
        "Les pédoncules cérébraux",
        "Le diencéphale",
        "Les pédoncules cérébelleux"
    ]),

# 25
("La face antérieure du mésencéphale est constituée des pédoncules :",
    [
        "Cérébelleux supérieurs",
        "Cérébelleux inférieurs",
        "Cérébelleux moyens",
        "Cérébraux",
        "Épiphysaires"
    ]),

# 26
("La face postérieure du mésencéphale est formée par la lame des tubercules :",
    [
        "Quadrijumeaux",
        "Mamillaires",
        "De Pacchioni",
        "Hypophysaires",
        "Olfactifs"
    ]),

# 27
("Les bras conjonctivaux antérieurs unissent :",
    [
        "Les tubercules quadrijumeaux antérieurs aux corps genouillés internes",
        "Les tubercules quadrijumeaux antérieurs aux corps genouillés externes",
        "Les tubercules quadrijumeaux postérieurs aux corps genouillés internes",
        "Les tubercules quadrijumeaux postérieurs aux corps genouillés externes",
        "Les tubercules quadrijumeaux postérieurs aux tubercules quadrijumeaux antérieurs"
    ]),

# 28
("Le tronc cérébral est situé dans :",
    [
        "L’étage antérieur",
        "L’étage moyen",
        "La fosse cérébrale postérieure",
        "Le canal rachidien",
        "La partie postérieure de l’étage antérieur"
    ]),

# 29
("La décussation pyramidale décapite les cornes antérieures :",
    [
        "Du bulbe",
        "De la moelle épinière",
        "Du mésencéphale",
        "De la protubérance",
        "Du mésencéphale et du bulbe"
    ]),

# 30
("La déhiscence du canal de l’épendyme à la partie postérieure du tronc cérébral entraîne la formation du :",
    [
        "3e ventricule",
        "4e ventricule",
        "La corne frontale",
        "La corne temporale",
        "La corne occipitale"
    ]),

# 31
("La croissance inégale de la colonne vertébrale et de la moelle a 3 conséquences :",
    [
        "Formation du filum terminal",
        "Formation des renflements",
        "Ascension apparente de la moelle",
        "Terminaison jusqu’à S2",
        "Terminaison en l2"
    ]),

# 32
("La longueur de la moelle épinière est de :",
    [
        "65 cm",
        "45 cm",
        "75 cm",
        "85 cm",
        "25 cm"
    ]),

# 33
("Dans la moelle épinière autour du canal de l’épendyme, on trouve la substance :",
    [
        "De Waldeyer",
        "Gélatineuse de Rolando",
        "Gélatineuse centrale de Stilling",
        "De Lissauer",
        "De Clarke"
    ]),

# 34
("La tête de la corne antérieure représente le centre de la :",
    [
        "Sensibilité proprioceptive consciente",
        "Sensibilité proprioceptive inconsciente",
        "Motricité volontaire des muscles striés",
        "Motricité automatique",
        "Motricité viscérale"
    ]),

# 35
("Les noyaux de la tête de la corne postérieure sont constitués de deutoneurones de la :",
    [
        "Sensibilité proprioceptive consciente",
        "Sensibilité proprioceptive inconsciente",
        "Sensibilité tactile thermique",
        "Sensibilité tactile douloureuse",
        "Motricité automatique"
    ]),

# 36
("Les fibres de la sensibilité épicritique :",
    [
        "Sont responsables de la sensibilité discriminative",
        "Sont couvertes de la gaine de myéline",
        "Sont responsables du cheminement rapide",
        "Sont responsables de la sensibilité thermique",
        "Sont responsables de la sensibilité protopathique"
    ]),

# 37
("Les fibres de la sensibilité proprioceptive inconsciente :",
    [
        "Font relais dans la corne postérieure",
        "Font relais dans les faisceaux de Goll et Burdach",
        "Font relais dans les faisceaux de Clarke",
        "Font relais dans les faisceaux de Bechterew",
        "Transportent la sensibilité musculaire et osseuse"
    ]),

# 38
("Le poids moyen du cerveau humain est de :",
    [
        "1100g",
        "1370g",
        "1600g",
        "1700g",
        "900g"
    ]),

# 39
("Le lobe frontal est limité par :",
    [
        "La scissure de Rolando en avant",
        "La scissure de Rolando en arrière",
        "La scissure de Sylvius en haut",
        "La scissure de Sylvius en bas",
        "La scissure de Sylvius en avant"
    ]),

# 40
("Le lobe pariétal :",
    [
        "Est limité par la scissure de Rolando en avant",
        "Est limité par la scissure de Rolando en arrière",
        "Comprend 3 circonvolutions",
        "Comprend 4 circonvolutions",
        "Comprend 5 circonvolutions"
    ]),

# 41
("Le lobe temporal :",
    [
        "Est limité par la scissure de Sylvius en haut",
        "Est limité par la scissure de Sylvius en bas",
        "Comprend 3 circonvolutions",
        "Comprend 4 circonvolutions",
        "Comprend 5 circonvolutions"
    ]),

# 42
("La vascularisation du cerveau fait appel aux artères suivantes :",
    [
        "Artère carotide externe",
        "Artère carotide interne",
        "Artères vertébrales",
        "Artère méningée",
        "Artère temporale"
    ]),

# 43
("L’artère récurrente de Heubner :",
    [
        "Est une branche de l’artère cérébrale moyenne",
        "Est une branche de l’artère cérébrale postérieure",
        "Est une branche de l’artère cérébrale antérieure",
        "Pénètre l’espace perforé antérieur",
        "Pénètre l’espace perforé postérieur"
    ]),

# 44
("Le cervelet est vascularisé par :",
    [
        "Le système vertébro basilaire",
        "Le système médullaire",
        "Deux artères cérébelleuses",
        "Trois artères cérébelleuses deux artères inférieures et une dorsale",
        "Les artères spinales postérieures"
    ]),

# 45
("L’artère spinale antérieure :",
    [
        "Vascularise toute la moelle épinière",
        "Vascularise le tronc cérébral",
        "Est une artère paire",
        "Elle devient grêle quand elle descend vers la moelle thoracique",
        "Elle ne s’anastomose pas avec les artères spinales postérieures"
    ]),

# 46
("L’artère communicante postérieure :",
    [
        "Relie la carotide interne avec l’artère cérébrale postérieure",
        "Relie les deux artères cérébrales postérieures",
        "Relie la carotide interne avec les artères vertébrales",
        "Vascularise l’hypophyse + corps mamillaires + thalamus",
        "Passe dans le sillon latéral ou scissure de Sylvius"
    ]),

# 47
("L’artère sylvienne :",
    [
        "Est une branche de la carotide interne",
        "Est une branche de la carotide externe",
        "Est une branche du tronc basilaire",
        "Passe dans la scissure inter-hémisphérique",
        "Se termine par l’artère péri-calleuse"
    ]),

# 48
("L’artère calloso-marginale :",
    [
        "Se trouve sur la face médiale du cerveau",
        "Donne les artères frontales médiales",
        "Vascularise le lobe temporal",
        "Vascularise le lobe occipital",
        "Vascularise la face médiale du lobe frontal"
    ]),

# 49
("Les artères spinales :",
    [
        "Sont des branches du tronc basilaire",
        "Proviennent des artères vertébrales",
        "Vascularisent toute la moelle",
        "Sont divisées en deux artères spinales antérieures et une postérieure",
        "Donnent les artères radiculo-médullaires"
    ]),

# 50
("Les branches de l’artère carotide interne sont :",
    [
        "L’artère ophtalmique",
        "L’artère choroïdienne antérieure",
        "L’artère communicante antérieure",
        "L’artère sylvienne",
        "L’artère cérébrale postérieure"
    ]),


]

js_file_path = r"C:\\Users\\thinkup\\Documents\\QuizLuckProject\\pythonjavaP.js"  # Chemin complet vers votre fichier JavaScript

generate_html_from_questions(questions, js_file_path)
