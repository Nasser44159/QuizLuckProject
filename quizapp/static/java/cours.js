document.addEventListener('DOMContentLoaded', () => {
    // PARTIE EXISTANTE (NE PAS TOUCHER)
    const pdfIframeSection = document.getElementById('pdf-iframe-section');
    const pdfIframe = document.getElementById('pdf-iframe');
    const iframeWidthInput = document.getElementById('iframe-width-input');
    const iframeWidthBtn = document.getElementById('iframe-width-btn');
    const resizeHandle = document.getElementById('resize-handle');
    const floatingButtons = document.getElementById('floating-buttons');

    // Fonction pour afficher/masquer l'iframe
    window.toggleIframeSection = function (event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        const isHidden = pdfIframeSection.style.display === 'none' || !pdfIframeSection.style.display;

        if (isHidden) {
            pdfIframeSection.style.display = 'block';
            pdfIframeSection.style.transform = 'translateX(0)';
            pdfIframeSection.style.transition = 'transform 0.3s ease';
            resizeHandle.style.display = 'block';
            floatingButtons.style.right = `calc(${pdfIframeSection.offsetWidth + 20}px)`;
        } else {
            pdfIframeSection.style.transform = 'translateX(100%)';
            setTimeout(() => {
                pdfIframeSection.style.display = 'none';
                resizeHandle.style.display = 'none';
                floatingButtons.style.right = '50px'; // Réinitialise les boutons
            }, 300);
        }
    };

    // Fonction pour appliquer la largeur personnalisée via l'input
    if (iframeWidthBtn && iframeWidthInput) {
        iframeWidthBtn.addEventListener('click', (event) => {
            event.stopPropagation();

            const widthValue = iframeWidthInput.value.trim();

            // Validation de l'entrée utilisateur
            if (!widthValue || !widthValue.match(/^\d+(px|%)?$/)) {
                alert("Veuillez entrer une largeur valide, par exemple '500px' ou '50%'.");
                return;
            }

            // Appliquer la largeur à la section iframe
            pdfIframeSection.style.width = widthValue.endsWith('%') || widthValue.endsWith('px')
                ? widthValue
                : `${widthValue}px`;

            // Ajuster la position des boutons flottants
            floatingButtons.style.right = `calc(${pdfIframeSection.offsetWidth + 20}px)`;
            resizeHandle.style.right = `${pdfIframeSection.offsetWidth}px`;
        });
    }

    // Redimensionnement avec le curseur
    if (resizeHandle) {
        resizeHandle.addEventListener('mousedown', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const startX = e.clientX; // Position initiale de la souris
            const startWidth = pdfIframeSection.offsetWidth; // Largeur initiale de la section

            const resize = (e) => {
                // Calculer la nouvelle largeur
                const newWidth = startWidth + (startX - e.clientX); // Vers la gauche augmente la largeur

                // Appliquer la nouvelle largeur si elle est dans les limites autorisées
                if (newWidth > 200 && newWidth < window.innerWidth * 0.7) {
                    pdfIframeSection.style.width = `${newWidth}px`;

                    // Ajuster la position des boutons flottants
                    floatingButtons.style.right = `${newWidth + 20}px`;
                    resizeHandle.style.right = `${newWidth}px`;
                }
            };

            const stopResize = () => {
                document.removeEventListener('mousemove', resize);
                document.removeEventListener('mouseup', stopResize);
            };

            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
        });
    }
});
