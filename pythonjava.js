 // Variable globale pour stocker l'intervalle du timer
            let timerInterval;
            const userAnswers = {}; // Object pour stocker les réponses de l'utilisateur
            // Fonction pour démarrer le timer
            function startTimer(duration, display) {
               let timer = duration,
                  minutes, seconds;
               timerInterval = setInterval(() => {
                  minutes = parseInt(timer / 60, 10);
                  seconds = parseInt(timer % 60, 10);
                  minutes = minutes < 10 ? "0" + minutes : minutes;
                  seconds = seconds < 10 ? "0" + seconds : seconds;
                  display.textContent = minutes + ":" + seconds;
                  // Vérifie si le temps est écoulé
                  if (--timer < 0) {
                     clearInterval(timerInterval);
                     showEndMessage();
                  }
               }, 1000);
            }
            // Fonction pour afficher le message de fin de test
            function showEndMessage() {
               const blurBackground = document.createElement('div');
               blurBackground.id = 'test-end-blur';
               blurBackground.style.position = 'fixed';
               blurBackground.style.top = '0';
               blurBackground.style.left = '0';
               blurBackground.style.width = '100%';
               blurBackground.style.height = '100%';
               blurBackground.style.background = 'rgba(0, 0, 0, 0.5)';
               blurBackground.style.zIndex = '100';
               blurBackground.style.display = 'flex';
               blurBackground.style.alignItems = 'center';
               blurBackground.style.justifyContent = 'center';
               const endMessage = document.createElement('div');
               endMessage.id = 'test-end-message';
               endMessage.style.padding = '40px';
               endMessage.style.background = '#ffffff';
               endMessage.style.borderRadius = '8px';
               endMessage.style.textAlign = 'center';
               endMessage.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
               endMessage.innerHTML = '<h2>Test terminé</h2><p>Le temps imparti est écoulé.</p><button onclick="location.reload()">Recommencer</button>';
               blurBackground.appendChild(endMessage);
               document.body.appendChild(blurBackground);
               // Optionnel : masquer le conteneur de timer
               const timerContainer = document.getElementById('timer-container');
               timerContainer.classList.add('hide');
            }
 // Fonction pour réinitialiser une seule question
            function resetQuestion(questionName) {
               const form = document.getElementById('quiz-form');
               const questionDiv = document.querySelector(`input[name="${questionName}"]`).closest('.question-container');
               // Décocher toutes les cases de cette question
               const inputs = Array.from(form.elements[questionName]);
               inputs.forEach(input => {
                  input.checked = false;
               });
               // Supprimer les styles correct/incorrect et remettre les couleurs par défaut
               questionDiv.classList.remove('correct', 'incorrect');
               questionDiv.querySelectorAll('li').forEach(li => {
                  li.style.color = ''; // Réinitialiser la couleur
                  li.style.fontWeight = ''; // Réinitialiser le texte en gras
                  li.style.textShadow = ''; // Réinitialiser l'ombre du texte
                  li.style.backgroundColor = ''; // Réinitialiser le fond
                  li.style.border = ''; // Réinitialiser la bordure
               });
               // Supprimer les informations enregistrées sur la réponse de cette question
               delete userAnswers[questionName];
            }
            // Fonction pour soumettre le quiz et afficher le résultat
            
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

    if (score === 0) { resultDiv.innerHTML = `<p>Vous avez aucune réponse juste, bozo !</p>`; } else if (score === 50) {
        // Liste des messages de félicitations
        const messages = [
"Félicitations ! Votre maîtrise des techniques d'imagerie médicale est remarquable !",
"Bravo ! Vous excellez dans l'interprétation des images radiologiques.",
"Incroyable ! Votre compréhension des principes de la radiologie est impressionnante.",
"Parfait ! Vous êtes sur le chemin pour devenir un(e) expert(e) en diagnostic par imagerie.",
"Votre précision dans l'analyse des radiographies est admirable.",
"Impressionnant ! Vous appliquez les concepts d'imagerie médicale avec rigueur.",
"Bravo ! Votre aptitude à identifier les anomalies radiologiques est exceptionnelle.",
"Extraordinaire ! Vous utilisez les outils d'imagerie avec une grande maîtrise.",
"Félicitations ! Vous êtes prêt(e) à contribuer à des diagnostics précis et rapides.",
"Votre capacité à relier les images radiologiques aux conditions cliniques est impressionnante.",
"Impressionnant ! Vous démontrez une compréhension approfondie des techniques avancées de radiologie.",
"Bravo ! Votre passion pour l'imagerie médicale est évidente.",
"Votre expertise en interprétation d'IRM et de scanner est un véritable atout.",
"Parfait ! Vous démontrez une aptitude exceptionnelle pour la radiologie interventionnelle.",
"Félicitations ! Vous êtes sur le chemin pour devenir un(e) pionnier(ère) en imagerie médicale.",
"Votre précision dans l'utilisation des technologies de pointe est exemplaire.",
"Bravo ! Vous appliquez les connaissances radiologiques avec rigueur et précision.",
"Incroyable ! Vous interprétez les images complexes avec une facilité admirable.",
"Félicitations ! Votre curiosité pour les technologies d'imagerie est une source d'inspiration.",
"Votre capacité à interpréter les résultats radiologiques est impressionnante.",

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
                exam_name: "Rd2019", // Remplacez par le nom réel de l'examen
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

            function resetAll() {
               const form = document.getElementById('quiz-form');
               // Réinitialiser toutes les questions
               for (const question of Object.keys(correctAnswers)) {
                  const questionDiv = document.querySelector(`input[name="${question}"]`).closest('.question-container');
                  form.elements[question].forEach(input => {
                     input.checked = false; // Décocher toutes les cases
                  });
                  // Supprimer les styles correct/incorrect sans toucher au style des bonnes réponses
                  questionDiv.classList.remove('correct', 'incorrect');
                  questionDiv.querySelectorAll('li').forEach(li => {
                     li.style.color = ''; // Réinitialiser la couleur du texte
                     li.style.fontWeight = ''; // Supprimer les styles ajoutés
                     li.style.textShadow = ''; // Réinitialiser l'ombre du texte
                     li.style.backgroundColor = ''; // Remettre le fond par défaut
                     li.style.border = ''; // Réinitialiser la bordure
                  });
               }
               // Réinitialiser l'affichage du timer
               const timerDuration = 60 * 60; // Remettre à 60 minutes (ou 10 secondes pour le test)
               const display = document.querySelector('#timer');
               startTimer(timerDuration, display); // Redémarrer le timer
               // Masquer la boîte de résultat
               const resultPopup = document.getElementById('result-popup');
               const blurBackground = document.getElementById('blur-background');
               resultPopup.classList.remove('show');
               blurBackground.classList.remove('show');
               setTimeout(() => {
                  resultPopup.style.display = 'none';
                  blurBackground.style.display = 'none';
               }, 500);
               // Remonter en haut de la page
               window.scrollTo({
                  top: 0,
                  behavior: 'smooth'
               });
               document.getElementById('voir-detail-btn').style.display = 'none'; // Masquer le bouton "Voir Détail"
            }
            // Fonction pour fermer la popup et garder les couleurs des bonnes/mauvaises réponses
            function closeResult(event) {
               event.preventDefault(); // Empêche le comportement par défaut du bouton
               const resultPopup = document.getElementById('result-popup');
               const blurBackground = document.getElementById('blur-background');
               // Masquer la boîte de résultat
               resultPopup.classList.remove('show');
               blurBackground.classList.remove('show');
               setTimeout(() => {
                  resultPopup.style.display = 'none';
                  blurBackground.style.display = 'none';
               }, 500);
               // Décocher toutes les cases sans changer la couleur des bonnes/mauvaises réponses
               const form = document.getElementById('quiz-form');
               for (const question of Object.keys(correctAnswers)) {
                  form.elements[question].forEach(input => {
                     input.checked = false; // Décocher toutes les cases
                  });
               }
            }
            // Fonction pour afficher les détails et rediriger vers SyntRd2019
            function afficherDetails(event) {
               event.preventDefault(); // Empêche le comportement par défaut du bouton
               saveUserAnswers(); // Enregistrer les réponses avant de quitter la page
               window.location.href = '{% url 'dynamic_view' 'S5' 'Radiologie' 'syntRd2019' %}'; // Redirection vers SyntRd2019
            }
            // Fonction pour défiler jusqu'à la question
            function scrollToQuestion(questionNumber) {
               const questionDiv = document.querySelector(`.question-container:nth-of-type(${questionNumber})`);
               if (questionDiv) {
                  questionDiv.scrollIntoView({
                     behavior: 'smooth'
                  });
               }
            }

            function saveUserAnswers() {
               // Change la clé pour la version 2019
               localStorage.setItem('userAnswersRd2019', JSON.stringify(userAnswers));
            }
            // Fonction pour afficher les confettis et ajouter le message de félicitations dans la popup de résultats
            function lancerConfettisEtMessage(score) {
    if (score === 50) {
                  // Lancer les confettis
                  confetti({
                     particleCount: 200,
                     spread: 70,
                     origin: {
                        y: 0.6
                     },
                     colors: ['#bb0000', '#ffffff'], // Couleurs de confettis
                  });
                  // Ajouter un message de félicitations à la boîte de résultat
                  const resultDiv = document.getElementById('result');
                  const felicitationMessage = `<p>Félicitations! Vous avez obtenu ${score} bonnes réponses. Vous serez un grand médecin !</p>`;
                  // Ajouter le message à la fin du résultat
                  resultDiv.innerHTML += felicitationMessage;
               }
            }
            // Partie favori pour Anatomie2020
            // Tableau pour stocker les questions favorites, récupéré depuis le localStorage (Anatomie2019)
            let favoriteQuestionsRD2019 = JSON.parse(localStorage.getItem('favoriteQuestionsRD2019')) || [];
            console.log('Favorite questions loaded from localStorage:', favoriteQuestionsRD2019);

            function toggleFavorite(event, questionNumber) {
               event.preventDefault(); // Empêche le rafraîchissement de la page
               const button = document.querySelector(`.favorite-button[data-question="${questionNumber}"]`);
               const questionContent = document.querySelector(`#question-${questionNumber}`).innerHTML; // Récupère le contenu HTML de la question
               // Vérifie si la question est déjà dans les favoris
               const isFavorited = favoriteQuestionsRD2019.includes(questionNumber);
               if (isFavorited) {
                  // Si elle est déjà favorisée, on la retire des favoris
                  favoriteQuestionsRD2019 = favoriteQuestionsRD2019.filter(q => q !== questionNumber);
                  button.classList.remove('favorited'); // Retire la classe favori
                  localStorage.removeItem(`favoriteContent2019-${questionNumber}`); // Supprime le contenu de la question
               } else {
                  // Si elle n'est pas favorisée, on l'ajoute
                  favoriteQuestionsRD2019.push(questionNumber);
                  button.classList.add('favorited'); // Ajoute la classe favori
                  localStorage.setItem(`favoriteContent2019-${questionNumber}`, questionContent); // Stocke le contenu de la question dans le localStorage
               }
               // Sauvegarde uniquement les favoris
               saveFavoriteState2019(); // <== Remplacez par saveFavoriteState2019
               // Mise à jour du bouton "Voir Favori" sans rafraîchir la page
               showFavoriteButton();
            }

            function saveFavoriteState2019() {
               localStorage.setItem('favoriteQuestionsRD2019', JSON.stringify(favoriteQuestionsRD2019)); // Sauvegarde les questions favorites
            }

            function initializeFavoriteButtons() {
               const allFavoriteButtons = document.querySelectorAll('.favorite-button');
               allFavoriteButtons.forEach(button => {
                  const questionNumber = parseInt(button.getAttribute('data-question'), 10);
                  // Vérifie si cette question est dans les favoris et applique la classe
                  if (favoriteQuestionsRD2019.includes(questionNumber)) {
                     button.classList.add('favorited'); // Ajoute l'état favori
                  } else {
                     button.classList.remove('favorited'); // Retire l'état favori
                  }
                  // Ajoute un événement de clic pour chaque bouton et empêche le rafraîchissement
                  button.addEventListener('click', (event) => toggleFavorite(event, questionNumber));
               });
            }

            function showFavoriteButton() {
               const voirFavorisBtn = document.getElementById('voir-favoris-btn');
               if (favoriteQuestionsRD2019.length > 0) {
                  voirFavorisBtn.style.display = 'inline-block'; // Affiche le bouton si des questions sont favorisées
               } else {
                  voirFavorisBtn.style.display = 'none'; // Cache le bouton si aucun favori
               }
            }
            // Appelle cette fonction après avoir ajouté ou retiré des favoris
            window.onload = function() {
               console.log('Page loaded, initializing favorite buttons for 2019.');
               initializeFavoriteButtons(); // Charger les boutons de favoris
               showFavoriteButton(); // Afficher le bouton "Voir Favori" si des favoris existent
               const timerDuration = 60 * 60; // 60 minutes
               const display = document.querySelector('#timer');
               startTimer(timerDuration, display);
               // Récupère toutes les listes (li) qui contiennent des propositions
               const propositions = document.querySelectorAll('li');
               propositions.forEach(function(proposition) {
                  // Trouve la checkbox dans chaque liste
                  const checkbox = proposition.querySelector('input[type="checkbox"]');
                  if (checkbox) {
                     // Créer un label
                     const label = document.createElement('label');
                     // Donner un id à la checkbox si elle n'en a pas
                     if (!checkbox.id) {
                        checkbox.id = checkbox.name + '-' + checkbox.value; // Ex: q1-A
                     }
                     // Déplacer le texte de la proposition dans le label
                     label.htmlFor = checkbox.id; // Le 'for' du label correspond à l'id de la checkbox
                     label.appendChild(checkbox); // Déplacer la checkbox dans le label
                     label.appendChild(document.createTextNode(proposition.textContent.trim())); // Ajouter le texte de la proposition
                     // Remplacer le contenu original par le nouveau label
                     proposition.innerHTML = ''; // Vider le contenu de l'élément <li>
                     proposition.appendChild(label); // Ajouter le label modifié
                  }
               });
            };
            try {
               localStorage.setItem('testKey', 'testValue');
               const testValue = localStorage.getItem('testKey');
               if (testValue !== 'testValue') {
                  console.error('localStorage is not functioning as expected.');
               }
            } catch (error) {
               console.error('localStorage error:', error);
            }

            function voirFavoris() {
    // Définir dynamiquement le favori correspondant
    const currentFavorite = 'favori9'; // Vous pouvez ajuster cette logique en fonction de la page actuelle
    
    // Rediriger vers la page du favori correspondant
    console.log('Redirection vers le favori :', currentFavorite); // Pour debug
    window.location.href = `/favoris/${currentFavorite}/`;
}



            </script>
            <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.4.0/dist/confetti.browser.min.js">


            </script>
         </form>
      </div>
      
   </body>

</html>      <script>
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

    <script src="{% static 'java/comment.js' %}"></script>