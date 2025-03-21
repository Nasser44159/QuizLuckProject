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

