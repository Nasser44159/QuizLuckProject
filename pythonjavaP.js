<script>
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
      // Fonction pour afficher les détails et rediriger vers Syntanatomie2023
      function afficherDetails(event) {
         event.preventDefault(); // Empêche le comportement par défaut du bouton
         saveUserAnswers(); // Enregistrer les réponses avant de quitter la page
         window.location.href = '{% url 'dynamic_view' 'S1' 'Biochimie_et_chimie' 'syntanat2020' %}'; // Redirection vers Syntanatomie2023
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
         // Change la clé pour la version 2020
         localStorage.setItem('userAnswersAnatomie2020', JSON.stringify(userAnswers));
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
      // Tableau pour stocker les questions favorites, récupéré depuis le localStorage (Anatomie2017RP)
      let favoriteQuestions2017RP = JSON.parse(localStorage.getItem('favoriteQuestions2017RP')) || [];
      console.log('Favorite questions loaded from localStorage:', favoriteQuestions2017RP);

      function toggleFavorite(event, questionNumber) {
         event.preventDefault(); // Empêche le rafraîchissement de la page
         const button = document.querySelector(`.favorite-button[data-question="${questionNumber}"]`);
         const questionContent = document.querySelector(`#question-${questionNumber}`).innerHTML; // Récupère le contenu HTML de la question
         // Vérifie si la question est déjà dans les favoris
         const isFavorited = favoriteQuestions2017RP.includes(questionNumber);
         if (isFavorited) {
            // Si elle est déjà favorisée, on la retire des favoris
            favoriteQuestions2017RP = favoriteQuestions2017RP.filter(q => q !== questionNumber);
            button.classList.remove('favorited'); // Retire la classe favori
            localStorage.removeItem(`favoriteContent2017RP-${questionNumber}`); // Supprime le contenu de la question
         } else {
            // Si elle n'est pas favorisée, on l'ajoute
            favoriteQuestions2017RP.push(questionNumber);
            button.classList.add('favorited'); // Ajoute la classe favori
            localStorage.setItem(`favoriteContent2017RP-${questionNumber}`, questionContent); // Stocke le contenu de la question dans le localStorage
         }
         // Sauvegarde uniquement les favoris
         saveFavoriteState2017RP(); // <== Remplacez par saveFavoriteState2017RP
         // Mise à jour du bouton "Voir Favori" sans rafraîchir la page
         showFavoriteButton();
      }

      function saveFavoriteState2017RP() {
         localStorage.setItem('favoriteQuestions2017RP', JSON.stringify(favoriteQuestions2017RP)); // Sauvegarde les questions favorites
      }

      function initializeFavoriteButtons() {
         const allFavoriteButtons = document.querySelectorAll('.favorite-button');
         allFavoriteButtons.forEach(button => {
            const questionNumber = parseInt(button.getAttribute('data-question'), 10);
            // Vérifie si cette question est dans les favoris et applique la classe
            if (favoriteQuestions2017RP.includes(questionNumber)) {
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
         if (favoriteQuestions2017RP.length > 0) {
            voirFavorisBtn.style.display = 'inline-block'; // Affiche le bouton si des questions sont favorisées
         } else {
            voirFavorisBtn.style.display = 'none'; // Cache le bouton si aucun favori
         }
      }
      // Appelle cette fonction après avoir ajouté ou retiré des favoris
      window.onload = function() {
         console.log('Page loaded, initializing favorite buttons for 2017RP.');
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
         console.log('Redirection vers la page des favoris');
         window.location.href = "{% url 'render_favorite' 'S1' 'favori2' %}";
      }
      // Fonction pour afficher les confettis et ajouter le message de félicitations dans la popup de résultats
      function lancerConfettisEtMessage(score) {
    if (score === 7) {
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

      </script>
      <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.4.0/dist/confetti.browser.min.js">


      </script>
      
   </body>

</html>      <script>
// Fonction pour réinitialiser une seule question
function resetQuestion(questionName) {
    console.log(`[DEBUG] Réinitialisation de la question : ${questionName}`);

    const form = document.getElementById('quiz-form');
    const questionDiv = document.querySelector(`input[name="${questionName}"]`).closest('.question-container');

    if (!form || !questionDiv) {
        console.error(`[ERROR] Formulaire ou conteneur de la question introuvable pour : ${questionName}`);
        return;
    }

    // Décocher toutes les cases de cette question
    const inputs = Array.from(form.elements[questionName]);
    inputs.forEach(input => {
        input.checked = false;
        console.log(`[DEBUG] Case décochée : ${input.value}`);
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

    // Supprimer les conteneurs ou les éléments liés aux pourcentages
    const percentageContainers = questionDiv.querySelectorAll('.percentage-container');
    percentageContainers.forEach(container => {
        console.log(`[DEBUG] Suppression du conteneur de pourcentage :`, container);
        container.remove();
    });

    // Supprimer les informations enregistrées sur la réponse de cette question
    if (userAnswers && userAnswers[questionName]) {
        delete userAnswers[questionName];
        console.log(`[DEBUG] Réponse supprimée pour la question : ${questionName}`);
    }

    console.log(`[DEBUG] Question réinitialisée avec succès : ${questionName}`);
}


function correctAndSubmitQuestion(questionId) {
    console.log("Début de la fonction correctAndSubmitQuestion.");
    console.log("ID de la question reçue :", questionId);

    // Transform the ID to match the backend's expected format
    const transformedId = questionId.replace('question-', 'Bioch2017RP_');
    console.log("ID transformé pour le backend :", transformedId);

    // Get the question number from the questionId
    const questionNumber = questionId.split('-')[1];
    console.log("Numéro de la question extrait :", questionNumber);

    // Get selected choices (checkbox values) dynamically for the specific question
    const selectedChoices = [];
    const checkboxes = document.querySelectorAll(`input[name="q${questionNumber}"]:checked`);
    console.log(`Nombre de checkboxes sélectionnées pour la question ${questionNumber}:`, checkboxes.length);

    checkboxes.forEach((checkbox) => {
        // Append the transformed choice ID in the format "question_id_l"
        const choiceId = `${transformedId}_${checkbox.value.toLowerCase()}`;
        selectedChoices.push(choiceId);
        console.log(`Transformed choice ID ajouté : ${choiceId}`);
    });

    console.log("Choix sélectionnés après transformation :", selectedChoices);

    if (selectedChoices.length === 0) {
        console.log("Aucune réponse sélectionnée. Alerte affichée.");
        alert("Veuillez sélectionner au moins une réponse.");
        return;
    }

    // Step 1: Submit the user's response
    const formData = new URLSearchParams();
    formData.append("question_id", transformedId);
    selectedChoices.forEach((choice) => formData.append("choices[]", choice));
    console.log("Données envoyées au backend :", [...formData.entries()]);

    fetch("/submit_response/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCsrfToken(),
        },
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                console.error("Erreur lors de l'enregistrement des réponses.");
                throw new Error("Erreur lors de l'enregistrement des réponses.");
            }
            console.log("Réponse soumise avec succès.");
            return response.json();
        })
        .then((data) => {
            console.log("Données reçues après soumission :", data);

            // Step 2: Fetch updated percentages for this question
            console.log(`Requête pour calculer les pourcentages pour l'ID ${transformedId}.`);
            return fetch(`/calculate_percentages/${transformedId}/`);
        })
        .then((response) => {
            if (!response.ok) {
                console.error("Erreur lors du calcul des pourcentages.");
                throw new Error("Erreur lors du calcul des pourcentages.");
            }
            console.log("Calcul des pourcentages réussi.");
            return response.json();
        })
        .then((data) => {
            console.log("Pourcentages reçus :", data);

            // Display percentages for each choice
            const questionContainer = document.getElementById(questionId);
            Object.entries(data.percentages).forEach(([choiceId, percentage]) => {
                console.log(`Traitement du choix ${choiceId} avec pourcentage ${percentage}%.`);
                const choiceElement = questionContainer.querySelector(`input[value="${choiceId.split('_').pop().toUpperCase()}"]`);
                if (choiceElement) {
                    // Ajouter un conteneur pour le pourcentage si nécessaire
                    let percentageContainer = choiceElement.parentElement.querySelector(".percentage-container");

                    if (!percentageContainer) {
                        console.log(`Conteneur de pourcentage manquant pour ${choiceId}. Création en cours.`);
                        percentageContainer = document.createElement("span");
                        percentageContainer.classList.add("percentage-container");

                        // Ajout du conteneur dans la parentElement
                        choiceElement.parentElement.style.display = "flex";
                        choiceElement.parentElement.style.alignItems = "center";
                        choiceElement.parentElement.appendChild(percentageContainer);
                    }

                    // Mettre à jour le texte avec le pourcentage
                    percentageContainer.textContent = `${percentage}%`;
percentageContainer.style.color = "blue";
percentageContainer.style.fontWeight = "bold";
percentageContainer.style.marginLeft = "auto"; // Aligne le pourcentage à droite
percentageContainer.style.textAlign = "right"; // Alignement du texte dans le conteneur
percentageContainer.style.paddingLeft = "10px"; // Optionnel, ajoute un espace entre la case et le pourcentage

                    console.log(`Pourcentage mis à jour pour ${choiceId}: ${percentage}%.`);
                } else {
                    console.warn(`Checkbox non trouvée pour le choix ${choiceId}.`);
                }
            });
        })
        .catch((error) => {
            console.error("Erreur :", error);
            alert("Une erreur est survenue lors de la soumission ou du calcul des pourcentages.");
        })
        .finally(() => {
            console.log("Fin de la fonction correctAndSubmitQuestion.");
        });
}


// Function to retrieve CSRF token
function getCsrfToken() {
    const csrfCookie = document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='));
    return csrfCookie ? csrfCookie.split('=')[1] : null;
}



</script>

    <script src="{% static 'java/comment.js' %}"></script>