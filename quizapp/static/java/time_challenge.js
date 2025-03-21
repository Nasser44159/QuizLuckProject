console.log("Fichier time_challenge.js chargé !");

document.addEventListener("DOMContentLoaded", () => {
    console.log("Document chargé : Initialisation du script");

    let currentQuestionIndex = 0;
    let startTime = null; // Temps de départ
    const timePenalty = 30; // Pénalité de temps (en secondes)
    let timerInterval;
    let hasErrors = false; // Indicateur pour les réponses incorrectes

    const timerDisplay = document.getElementById("timer"); // Affichage du temps total
    const countdownDisplay = document.getElementById("countdown"); // Compte à rebours initial
    const questionContainer = document.getElementById("question-container");
    const questionText = document.getElementById("question-text");
    const choicesContainer = document.getElementById("choices");
    const submitButton = document.getElementById("submit-button");
    const sourceContainer = document.getElementById("source");

    console.log("Éléments du DOM récupérés :", {
        timerDisplay,
        countdownDisplay,
        questionContainer,
        questionText,
        choicesContainer,
        submitButton,
        sourceContainer
    });

    // Fonction pour lancer le compte à rebours avant de commencer le quiz
    function startCountdown(duration, callback) {
        console.log(`Début du compte à rebours : ${duration} secondes`);
        let countdown = duration; // Temps en secondes
        countdownDisplay.textContent = countdown;

        const countdownInterval = setInterval(() => {
            countdown--;
            countdownDisplay.textContent = countdown;

            if (countdown <= 0) {
                clearInterval(countdownInterval);
                console.log("Compte à rebours terminé. Démarrage du quiz.");
                document.getElementById("timer-overlay").style.display = "none"; // Cache l'overlay
                callback(); // Lance le quiz
            }
        }, 1000);
    }

    // Fonction pour démarrer le chronomètre global
    function startTimer() {
        console.log("Démarrage du chronomètre global");
        startTime = performance.now();

        timerInterval = setInterval(() => {
            const elapsedTime = performance.now() - startTime;

            const minutes = Math.floor(elapsedTime / 60000);
            const seconds = Math.floor((elapsedTime % 60000) / 1000);
            const milliseconds = Math.floor(elapsedTime % 1000);

            timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}:${String(milliseconds).padStart(3, '0')}`;
        }, 10); // Mise à jour toutes les 10ms
    }

    // Fonction pour ajouter un effet d'animation au chronomètre uniquement en cas d'erreur
    function animateTimerOnError() {
        timerDisplay.style.color = "red";
        timerDisplay.style.animation = "shake 0.5s ease";

        setTimeout(() => {
            timerDisplay.style.animation = ""; // Supprime l'animation
            timerDisplay.style.color = "green"; // Retourne à vert par défaut
        }, 500);
    }

    // Chargement d'une question
    function loadQuestion(index) {
        console.log(`Chargement de la question ${index + 1}`);
        if (index >= questions.length) {
            console.log("Toutes les questions ont été complétées. Arrêt du quiz.");
            clearInterval(timerInterval); // Stop le chronomètre à la fin du quiz
            questionContainer.innerHTML = `
                <div class="final-message success">
                    <h2>Félicitations, vous avez terminé !</h2>
                    <p>Vous avez complété le quiz en ${timerDisplay.textContent}.</p>
                    ${hasErrors ? "" : "<p>Vous n'avez fait aucune erreur. Bravo pour votre score parfait ! 🎉</p>"}
                </div>
            `;

            if (!hasErrors) {
                launchConfetti(); // Lancer les confettis uniquement s'il n'y a eu aucune erreur
            }

            return;
        }

        const question = questions[index];
        console.log("Question chargée :", question);
        questionText.textContent = question.text;
        choicesContainer.innerHTML = question.choices.map(choice => `
            <li>
                <label>
                    <input type="checkbox" class="answer-option" value="${choice.id}">
                    ${choice.text}
                </label>
            </li>
        `).join("");

        if (sourceContainer) {
            sourceContainer.innerHTML = `Source de la question : <strong>${question.source}</strong>`;
        }
    }

    // Validation de la réponse
    function validateAnswer() {
        console.log("Validation de la réponse");
        const selectedAnswers = Array.from(document.querySelectorAll(".answer-option:checked"))
            .map(option => option.value);
        const correctAnswers = questions[currentQuestionIndex].correct_choices;

        console.log("Réponses sélectionnées :", selectedAnswers);
        console.log("Réponses correctes :", correctAnswers);

        if (JSON.stringify(selectedAnswers.sort()) === JSON.stringify(correctAnswers.sort())) {
            console.log("Réponse correcte.");
            currentQuestionIndex++;
        } else {
            console.log("Réponse incorrecte. Ajout de la pénalité de temps.");
            hasErrors = true; // Marque qu'une erreur a été commise
            animateTimerOnError(); // Animation et couleur rouge en cas d'erreur
            startTime -= timePenalty * 1000; // Ajoute une pénalité au temps total
            currentQuestionIndex++;
        }

        // Charge la question suivante
        loadQuestion(currentQuestionIndex);
    }

    // Fonction pour lancer les confettis
    function launchConfetti() {
        console.log("Lancement des confettis");
        const duration = 5000; // Durée des confettis en millisecondes
        const animationEnd = Date.now() + duration;

        const confettiColors = ["#bb0000", "#ffffff", "#00bb00", "#0000bb"];
        const interval = setInterval(() => {
            if (Date.now() > animationEnd) {
                console.log("Fin des confettis");
                return clearInterval(interval);
            }

            confetti({
                particleCount: 100,
                startVelocity: 30,
                spread: 360,
                origin: {
                    x: Math.random(),
                    y: Math.random() - 0.2 // Légèrement au-dessus du centre
                },
                colors: confettiColors
            });
        }, 250);
    }

    // Événement de clic sur le bouton "Soumettre"
    submitButton.addEventListener("click", () => {
        console.log("Bouton 'Soumettre' cliqué");
        validateAnswer();
    });

    // Ajoute une animation "shake" au CSS
    const style = document.createElement("style");
    style.textContent = `
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
    `;
    document.head.appendChild(style);

    // Démarre le compte à rebours, puis le quiz
    console.log("Démarrage du compte à rebours avant le quiz");
    startCountdown(3, () => {
        startTimer();
        loadQuestion(currentQuestionIndex);
    });
});
