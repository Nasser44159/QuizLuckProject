import os

# Chemin vers le dossier contenant les fichiers templates dans quizapp
base_dir = 'quizapp/templates'

# Contenu à rechercher et à remplacer
old_content = """
            <div class="comments-section" id="comments-section">
    <button class="toggle-arrow" id="toggle-arrow" onclick="toggleCommentSection(null, event)">❯</button>
    <h3>Commentaires</h3>
    <textarea id="new-comment" placeholder="Écrire un commentaire..."></textarea>
    <button type="button" onclick="addComment(event)">Ajouter</button>
    <div id="comment-alert" class="alert" style="display: none;"></div>
    <div id="comments-list"></div>
</div>
"""

new_content = """
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
"""

# Liste des fichiers non modifiés et exclus
not_modified_files = []
excluded_files = []

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.startswith("synt"):
            excluded_files.append(os.path.join(root, file))
            continue

        file_path = os.path.join(root, file)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if old_content in content:
                print(f"Modification du fichier : {file_path}")
                content = content.replace(old_content, new_content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                not_modified_files.append(file_path)
        except Exception as e:
            print(f"Erreur lors du traitement de {file_path} : {e}")

print("\nFichiers non modifiés :")
for file in not_modified_files:
    print(file)

print("\nFichiers exclus :")
for file in excluded_files:
    print(file)
