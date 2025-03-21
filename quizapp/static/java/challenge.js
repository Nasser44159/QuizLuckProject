document.addEventListener("DOMContentLoaded", () => {
    let currentQuestionIndex = 0;

    const timerOverlay = document.getElementById("timer-overlay");
    const countdown = document.getElementById("countdown");
    const questionContainer = document.getElementById("question-container");
    const questionText = document.getElementById("question-text");
    const choicesContainer = document.getElementById("choices");
    const submitButton = document.getElementById("submit-button");
    const sourceContainer = document.getElementById("source");

    function loadQuestion(index) {
        if (index >= questions.length) {
            // Masque le conteneur des questions pour le message de succès
            questionContainer.style.display = "none";

            // Affiche le message de succès
            questionContainer.innerHTML = `
                <div class="final-message success">
                    <h2>Félicitations, vous avez terminé !</h2>
                    <p>Vous avez répondu à toutes les questions.</p>
                </div>
            `;
            questionContainer.style.display = "block";
            launchConfetti(); // Lancer les confettis
            return;
        }

        questionContainer.classList.remove("hidden-container");

        const question = questions[index];
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

    function validateAnswer() {
        const selectedAnswers = Array.from(document.querySelectorAll(".answer-option:checked"))
            .map(option => option.value);
        const correctAnswers = questions[currentQuestionIndex].correct_choices;

        if (JSON.stringify(selectedAnswers.sort()) === JSON.stringify(correctAnswers.sort())) {
            currentQuestionIndex++;
            loadQuestion(currentQuestionIndex);
        } else {
            // Convertir les bonnes réponses en texte lisible
            const correctAnswerText = correctAnswers.map(choiceId => {
                const choice = questions[currentQuestionIndex].choices.find(c => c.id === choiceId);
                return choice ? choice.text : choiceId; // Récupérer le texte de la réponse ou son ID si introuvable
            }).join(", ");

            // Masque le conteneur des questions pour le message d'échec
            questionContainer.style.display = "none";

            // Affiche le message d'échec avec les bonnes réponses
            questionContainer.innerHTML = `
                <div class="final-message failure">
                    <h2>Dommage, vous avez échoué.</h2>
                    <p>Vous avez répondu à <span class="highlight">${currentQuestionIndex}</span> questions de suite correctement.</p>
                    <p>Les bonnes réponses étaient : <strong>${correctAnswerText}</strong></p>
                </div>
            `;
            questionContainer.style.display = "block"; // Réaffiche uniquement le message final
        }

        // Réinitialise le style du conteneur pour les questions suivantes
        questionContainer.classList.remove("hidden-container");
    }

    function launchConfetti() {
        const duration = 5000; // Durée des confettis en millisecondes
        const animationEnd = Date.now() + duration;

        const confettiColors = ["#bb0000", "#ffffff", "#00bb00", "#0000bb"];
        const interval = setInterval(() => {
            if (Date.now() > animationEnd) {
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

    submitButton.addEventListener("click", validateAnswer);

    loadQuestion(0); // Charge la première question
});
