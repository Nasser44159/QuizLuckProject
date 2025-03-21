import os

# Nouveau contenu de la fonction submitQuiz
new_submit_quiz_function = """
// Fonction pour soumettre le quiz et afficher le résultat
async function submitQuiz() {
    console.log("Début de la soumission du quiz.");

    const form = document.getElementById('quiz-form');
    if (!form) {
        console.error("Erreur : Formulaire introuvable.");
        alert("Formulaire introuvable. Veuillez réessayer.");
        return;
    }

    let score = 0;

    // Évaluer les réponses utilisateur
    for (const question of Object.keys(correctAnswers)) {
        correctQuestion(question); // Fonction pour corriger chaque question
        const userAnswer = userAnswers[question]?.isCorrect;
        if (userAnswer) {
            score++;
        }
    }

    console.log("Score brut calculé (frontend) :", score);
    console.log("Réponses utilisateur envoyées :", userAnswers);

    // Lancer les confettis et afficher le message de félicitations si le score est parfait (50 sur 50)
    lancerConfettisEtMessage(score);

    // Mise à jour du résultat dans la boîte de dialogue
    const resultDiv = document.getElementById('result'); // Assure-toi que tu as un div avec l'id 'result' dans ton HTML

    if (score === 50) {
        // Liste des messages de félicitations
        const messages = [
            "Félicitations ! Vous êtes en bonne voie pour devenir un médecin brillant !",
            "Impressionnant ! Vous maîtrisez cette matière comme un vrai professionnel de santé.",
            "Excellent travail ! Votre dévouement à l'étude porte ses fruits.",
            "Bravo ! Vous êtes sur la bonne voie pour une brillante carrière médicale.",
            "Quel talent ! La précision dans vos réponses est remarquable.",
            "Incroyable ! Votre compréhension de l'anatomie est sans faille.",
            "Félicitations ! Vous avez prouvé que vous avez ce qu'il faut pour réussir dans le domaine médical.",
            "C'est parfait ! Vos connaissances sont solides comme un roc.",
            "Bravo ! Vous êtes un exemple de rigueur et de détermination.",
            "Vous êtes un prodige ! Ce score parfait montre à quel point vous êtes doué(e).",
            "Félicitations ! Vous serez un atout incroyable pour la médecine.",
            "Vous avez tout juste ! Vos compétences en anatomie sont impressionnantes.",
            "Parfait ! Vous êtes prêt(e) à affronter tous les défis médicaux.",
            "Vous avez réussi haut la main ! La médecine est définitivement votre domaine.",
            "Votre score est exemplaire ! Vous avez toutes les qualités d'un futur médecin.",
            "Extraordinaire ! Vous faites preuve d'une maîtrise remarquable.",
            "Un vrai sans-faute ! Continuez comme ça, vous allez faire des miracles dans la médecine.",
            "Bravo ! Vous avez prouvé que vous avez l'étoffe d'un grand médecin.",
            "Score parfait ! Votre engagement est tout simplement admirable.",
            "Incroyable ! Vous êtes destiné(e) à un avenir brillant dans la médecine."
        ];
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        resultDiv.innerHTML = `<p>${randomMessage}</p>`;
    } else {
        resultDiv.innerHTML = `Vous avez obtenu ${score} bonnes réponses sur ${Object.keys(correctAnswers).length}.`;
    }

    // Afficher la boîte de résultat avec animation
    const resultPopup = document.getElementById('result-popup');
    const blurBackground = document.getElementById('blur-background');

    blurBackground.style.display = 'block';
    resultPopup.style.display = 'block';

    setTimeout(() => {
        blurBackground.classList.add('show'); // Ajoute l'animation de fondu sur le fond flouté
        resultPopup.classList.add('show'); // Ajoute l'animation de zoom sur la boîte de résultat
    }, 100); // Légère pause pour plus de fluidité

    document.getElementById('voir-detail-btn').style.display = 'inline-block';

    // Envoi des données au backend
    try {
        console.log("Préparation de l'enregistrement au backend...");

        const response = await fetch("/soumettre-quiz/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": "{{ csrf_token }}" // Inclure le token CSRF
            },
            body: JSON.stringify({
                exam_name: "Anatomie2023", // Remplacez par le nom réel de l'examen
                score: score,
                userAnswers: userAnswers
            })
        });

        const result = await response.json();
        if (response.ok) {
            console.log("Score enregistré avec succès :", result);
        } else {
            console.error("Erreur du serveur :", result.message);
            alert(`Erreur : ${result.message}`);
        }
    } catch (error) {
        console.error("Erreur lors de l'envoi des données :", error);
        alert("Une erreur s'est produite lors de la soumission. Veuillez réessayer.");
    }
}
"""

def process_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        modified = False

        # Ajouter {% csrf_token %} après form id="quiz-form"
        if 'id="quiz-form"' in content and '{% csrf_token %}' not in content:
            content = content.replace('id="quiz-form"', 'id="quiz-form">\n    {% csrf_token %}')
            modified = True

        # Remplacer uniquement la fonction submitQuiz
        if "function submitQuiz()" in content:
            start_index = content.find("function submitQuiz()")
            end_index = content.find("function resetAll(", start_index)
            if end_index == -1:
                end_index = content.find("}", start_index) + 1
            content = content[:start_index] + new_submit_quiz_function + content[end_index:]
            print(f"Fonction submitQuiz remplacée dans {file_path}.")
            modified = True

        # Modifier la ligne if (score === X)
        if "if (score ===" in content:
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if "if (score ===" in line:
                    lines[i] = "    if (score === 50) {"
                    print(f"Ligne if (score === X) corrigée dans {file_path}.")
                    modified = True
            content = "\n".join(lines)

        # Modifier la ligne exam_name
        if "exam_name: \"Anatomie2023\"" in content:
            file_name = os.path.basename(file_path).replace(".html", "")
            content = content.replace('exam_name: "Anatomie2023"', f'exam_name: "{file_name}"')
            print(f"Nom de l'examen mis à jour dans {file_path}.")
            modified = True

        # Sauvegarder les modifications si nécessaire
        if modified:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Modifications enregistrées dans {file_path}.")
        else:
            print(f"Aucune modification nécessaire pour {file_path}.")

    except Exception as e:
        print(f"Erreur lors du traitement de {file_path} : {e}")

def process_all_files(base_dir):
    for root, dirs, files in os.walk(base_dir):
        if "Anatomie_1" in root:
            continue

        for file_name in files:
            if file_name.startswith("synt") or not file_name.endswith(".html"):
                continue

            file_path = os.path.join(root, file_name)
            process_file(file_path)

# Process all files in the templates directory
process_all_files("quizapp/templates")
