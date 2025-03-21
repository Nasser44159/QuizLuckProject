function toggleSidebar() {
    console.log("toggleSidebar: Fonction appelée.");

    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const hamburgerMenu = document.querySelector('.hamburger-menu');

    if (!sidebar || !content) {
        console.error("toggleSidebar: Élément introuvable.");
        return;
    }

    const isSidebarOpen = sidebar.classList.contains('open');

    if (isSidebarOpen) {
        // Appliquer immédiatement la classe `.closing` AVANT la transition
        sidebar.classList.add('closing');
        sidebar.style.zIndex = "800"; // S'assure qu'elle reste derrière

        // Attendre la fin de l'animation (0.3s) avant de finaliser la fermeture
        setTimeout(() => {
            sidebar.classList.remove('closing');
            sidebar.classList.add('closed');
            sidebar.style.zIndex = "900"; // Remet la sidebar derrière normalement après fermeture
        }, 300); // Correspond au temps de l'animation CSS
    } else {
        // Lorsque la sidebar s'ouvre, on la remet derrière la navbar
        sidebar.classList.remove('closed');
        sidebar.style.zIndex = "900";
    }

    sidebar.classList.toggle('open');
    content.classList.toggle('shifted');
    hamburgerMenu.classList.toggle('active');
}


// Fonction pour initialiser le toggle des modules
function initializeModuleToggle() {
    console.log("initializeModuleToggle: Initialisation des événements de bascule.");

    // Sélectionner toutes les flèches de bascule
    const semesterTitles = document.querySelectorAll('.semester-title');

    if (semesterTitles.length === 0) {
        console.warn("initializeModuleToggle: Aucun élément .semester-title trouvé.");
        return;
    }

    // Ajouter un événement 'click' à chaque titre de semestre
    semesterTitles.forEach(title => {
        title.addEventListener('click', function () {
            console.log(`initializeModuleToggle: Titre cliqué: ${this.textContent.trim()}`);

            // Récupérer la liste des modules associée
            const modulesList = this.nextElementSibling;
            const arrow = this.querySelector('.toggle-arrow');

            if (!modulesList || !arrow) {
                console.error("initializeModuleToggle: Problème avec modulesList ou arrow.");
                return;
            }

            // Basculer les classes pour afficher ou masquer les modules
            modulesList.classList.toggle('hidden');
            arrow.classList.toggle('open');

            console.log(
                `initializeModuleToggle: Modules ${modulesList.classList.contains('hidden') ? 'masqués' : 'affichés'}.`
            );
        });
    });

    console.log("initializeModuleToggle: Initialisation terminée.");
}

// Charger les semestres et initialiser le toggle après
function loadSemesters() {
    console.log("loadSemesters: Chargement des semestres...");

    const sidebarSemesters = document.getElementById('sidebar-semesters');

    if (!sidebarSemesters) {
        console.error('loadSemesters: Élément #sidebar-semesters introuvable.');
        return;
    }

    // Charger les modules accessibles depuis une API
    fetch('/api/get_accessible_modules/')
        .then(response => {
            console.log('loadSemesters: Réponse de l\'API reçue.');

            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des modules.');
            }
            return response.json();
        })
        .then(data => {
            console.log('loadSemesters: Données reçues de l\'API.', data);

            const accessibleModules = data.accessible_modules;

            if (!Array.isArray(accessibleModules) || accessibleModules.length === 0) {
                console.warn('loadSemesters: Aucun module disponible.');
                sidebarSemesters.innerHTML = '<li>Aucun module disponible</li>';
                return;
            }

            let semesterList = '';
            accessibleModules.forEach(semesterData => {
                console.log('loadSemesters: Traitement du semestre', semesterData);

                // Vérification des données
                if (!semesterData.semester_name || !Array.isArray(semesterData.modules)) {
                    console.warn('loadSemesters: Données invalides pour un semestre', semesterData);
                    return;
                }

                semesterList += `
                    <li>
                        <span class="semester-title">
                            <i class="fas fa-graduation-cap"></i> ${semesterData.semester_name}
                            <span class="toggle-arrow">▶</span>
                        </span>
                        <ul class="modules-list hidden">
                            ${semesterData.modules.map(module => {
                                return `
                                    <li>
                                        <a href="/${semesterData.semester_description}/${module.module_name}/">
                                            <i class="fas fa-book"></i> ${module.description}
                                        </a>
                                    </li>
                                `;
                            }).join('')}
                        </ul>
                    </li>
                `;
            });

            sidebarSemesters.innerHTML = `<ul>${semesterList}</ul>`;
            console.log('loadSemesters: Semestres chargés.');

            // Initialiser les événements de toggle après le chargement
            initializeModuleToggle();
        })
        .catch(error => {
            console.error('loadSemesters: Erreur lors du chargement des modules.', error);
            sidebarSemesters.innerHTML = '<li>Erreur lors du chargement des modules</li>';
        });
}

// Appeler la fonction loadSemesters au chargement du document
document.addEventListener("DOMContentLoaded", () => {
    console.log("Document chargé, démarrage des fonctionnalités.");
    loadSemesters();
});


// Initialisation au chargement de la page
document.addEventListener("DOMContentLoaded", function () {
    console.log("DOMContentLoaded: Initialisation du script...");

    const hamburgerMenu = document.querySelector('.hamburger-menu');

    // Ajoute un écouteur au bouton hamburger
    if (hamburgerMenu) {
        console.log("DOMContentLoaded: Bouton hamburger trouvé.");
        hamburgerMenu.addEventListener('click', toggleSidebar);
    } else {
        console.error('DOMContentLoaded: Le bouton hamburger-menu est introuvable.');
    }

    // Charger les semestres dans la barre latérale
    loadSemesters();
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed.');

    const floatingBtn = document.getElementById('open-contact-modal');
    const messageContainer = document.getElementById('message-container');
    const closeBtn = document.getElementById('close-btn');
    const sendMessageBtn = document.getElementById('send-message');
    const blurOverlay = document.getElementById('blur-overlay');

    // Ouverture du conteneur de message et ajout du fond flouté
    if (floatingBtn) {
        floatingBtn.addEventListener('click', () => {
            console.log('Bouton flottant cliqué.');
            messageContainer.style.display = 'block';
            blurOverlay.style.display = 'block';
        });
    }

    // Fermeture du conteneur de message et suppression du fond flouté
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            console.log('Bouton de fermeture cliqué.');
            messageContainer.style.display = 'none';
            blurOverlay.style.display = 'none';
        });
    }

    // Fermeture du conteneur en cliquant sur le fond flouté
    if (blurOverlay) {
        blurOverlay.addEventListener('click', () => {
            console.log('Fond flouté cliqué.');
            messageContainer.style.display = 'none';
            blurOverlay.style.display = 'none';
        });
    }

    // Envoi du message via AJAX et affichage d'une notification
    if (sendMessageBtn) {
        sendMessageBtn.addEventListener('click', async () => {
            const message = document.getElementById('message').value;
            const mode = document.querySelector('input[name="mode"]:checked').value;

            console.log('Message à envoyer :', message);
            console.log('Mode sélectionné :', mode);

            if (!message.trim()) {
                alert("Veuillez entrer un message !");
                return;
            }

            try {
                console.log('Envoi du message en cours...');
                const response = await fetch('/contact_page/', { // Utilisation de la bonne URL
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ message, mode })
                });

                console.log('Réponse reçue :', response);

                if (response.ok) {
                    console.log('Message envoyé avec succès.');
                    showTemporaryNotification('Votre message a été envoyé avec succès !', 'green');
                    messageContainer.style.display = 'none';
                    blurOverlay.style.display = 'none';
                } else {
                    console.error('Erreur lors de l\'envoi du message. Status:', response.status);
                    showTemporaryNotification('Erreur lors de l\'envoi du message.', 'red');
                }
            } catch (error) {
                console.error('Erreur réseau ou interne:', error);
                showTemporaryNotification('Une erreur est survenue lors de l\'envoi.', 'red');
            }
        });
    }



function showTemporaryNotification(message, color = 'green') {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.bottom = '0%'; // Centré verticalement
    notification.style.left = '50%'; // Centré horizontalement
    notification.style.transform = 'translate(-50%, -50%)'; // Correction pour centrer précisément
    notification.style.backgroundColor = color;
    notification.style.color = 'white';
    notification.style.padding = '15px 30px';
    notification.style.borderRadius = '8px';
    notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
    notification.style.zIndex = '1002';
    notification.style.fontSize = '16px';
    notification.style.textAlign = 'center';
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000); // Durée de 3 secondes
}

});
