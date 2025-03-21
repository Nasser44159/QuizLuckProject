    const csrfToken = "{{ csrf_token }}"; // CSRF Token for POST requests

    document.addEventListener('DOMContentLoaded', () => {
        console.log("DOM chargé. Début de la récupération des statistiques des questions.");

        // Get the file name for identifying questions
        const fileNameInput = document.querySelector('input[name="file_name"]');
        if (!fileNameInput) {
            console.error("Erreur : L'élément <input name='file_name'> est introuvable dans le DOM.");
            return;
        }
        const fileName = fileNameInput.value;
        console.log(`Nom du fichier récupéré : ${fileName}`);

        // Collect all question containers
        const questionContainers = document.querySelectorAll('.question-container');
        if (!questionContainers.length) {
            console.warn("Aucun conteneur de question trouvé dans le DOM.");
            return;
        }

        // Map question IDs to transformed IDs for API lookup
        const idMapping = {};
        questionContainers.forEach(container => {
            const questionId = container.getAttribute('id'); // Original ID (e.g., question-1)
            const transformedId = `${fileName}_${questionId.split('-')[1]}`; // Transformed ID (e.g., Anatomie2023_1)
            idMapping[transformedId] = questionId; // Map transformed ID to original ID
            console.log(`Question trouvée : ID brut = ${questionId}, ID transformé = ${transformedId}`);
        });

        console.log("Mapping entre IDs transformés et IDs bruts :", idMapping);

        // Fetch stats from the server
        fetch('/api/get_attempts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Add CSRF token for security
            },
            body: JSON.stringify({ question_ids: Object.keys(idMapping) }) // Send transformed IDs
        })
            .then(response => {
                console.log(`Statut de la réponse : ${response.status}`);
                if (!response.ok) {
                    throw new Error(`Erreur HTTP : ${response.status}`);
                }
                return response.json();
            })
            .then(stats => {
                console.log("Statistiques récupérées :", stats);

                // Add stats and toggle switches dynamically
                Object.keys(stats).forEach(transformedId => {
                    const stat = stats[transformedId];
                    console.log(`Ajout des statistiques pour la question ID transformé: ${transformedId}`, stat);

                    // Find the base ID for DOM manipulation
                    const baseId = idMapping[transformedId];
                    if (!baseId) {
                        console.warn(`Aucun conteneur correspondant trouvé pour l'ID transformé: ${transformedId}`);
                        return;
                    }

                    // Find or create stats container
                    const questionContainer = document.querySelector(`#${baseId}`);
                    if (questionContainer) {
                        // Create stats container if it doesn't exist
                        let statsContainer = document.getElementById(`stats-${baseId}`);
                        if (!statsContainer) {
                            statsContainer = document.createElement('div');
                            statsContainer.id = `stats-${baseId}`;
                            statsContainer.className = 'stats-container';
                            statsContainer.style.display = 'none'; // Hide initially
                            statsContainer.innerHTML = `
                                <p>Tentatives totales : ${stat.total_attempts}</p>
                                <p>Échecs : ${stat.failures}</p>
                                <p>Taux d'échec : ${stat.failure_rate}%</p>
                            `;
                            questionContainer.appendChild(statsContainer);
                        }

                        // Add toggle switch dynamically
                        let toggleContainer = questionContainer.querySelector('.toggle-container');
                        if (!toggleContainer) {
                            toggleContainer = document.createElement('div');
                            toggleContainer.className = 'toggle-container';
                            toggleContainer.innerHTML = `
                                <label class="switch">
                                    <input type="checkbox" class="toggle-stats-switch" data-question-id="${baseId}">
                                    <span class="slider"></span>
                                </label>
                                <label class="switch-label">Voir vos statistiques pour cette question</label>
                            `;
                            questionContainer.appendChild(toggleContainer);
                        }
                    } else {
                        console.warn(`Conteneur DOM non trouvé pour l'ID brut: ${baseId}`);
                    }
                });

                // Configure toggles after all stats and switches are added
                configureToggles();
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des statistiques :', error);
            });
    });

    // Function to configure toggle switches
    function configureToggles() {
        console.log("Configuration des switches de statistiques.");

        // Add event listeners to toggle switches
        document.querySelectorAll('.toggle-stats-switch').forEach(toggle => {
            toggle.addEventListener('change', () => {
                const questionId = toggle.getAttribute('data-question-id');
                const statsContainer = document.getElementById(`stats-${questionId}`);

                if (statsContainer) {
                    if (toggle.checked) {
                        statsContainer.style.display = 'block'; // Show stats
                        console.log(`Statistiques affichées pour la question: ${questionId}`);
                    } else {
                        statsContainer.style.display = 'none'; // Hide stats
                        console.log(`Statistiques masquées pour la question: ${questionId}`);
                    }
                } else {
                    console.warn(`Conteneur de statistiques introuvable pour la question: ${questionId}`);
                }
            });
        });
    }
