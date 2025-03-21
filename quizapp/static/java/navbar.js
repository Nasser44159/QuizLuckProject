


function toggleMenu() {
    const menu = document.getElementById('dropdown-menu');
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

// Fermer le menu si on clique en dehors
document.addEventListener('click', function (event) {
    const menu = document.getElementById('dropdown-menu');
    const userProfile = document.querySelector('.user-profile');

    if (!userProfile.contains(event.target) && menu.style.display === 'block') {
        menu.style.display = 'none';
    }
});



function openAccountModal() {
    document.getElementById('account-modal').style.display = 'flex';
}

function closeAccountModal() {
    document.getElementById('account-modal').style.display = 'none';
}


// Fermer le menu si on clique en dehors
document.addEventListener('click', function (event) {
    const menu = document.getElementById('dropdown-menu');
    const userProfile = document.querySelector('.user-profile');

    if (!userProfile.contains(event.target) && menu.style.display === 'block') {
        menu.style.display = 'none';
    }
});


document.getElementById('submit-form').addEventListener('click', function () {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Récupérer les valeurs du formulaire
    const username = document.getElementById('username').value;
    const dob = document.getElementById('dob').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Vérification côté client : vérifier si les mots de passe correspondent
    if (password && password !== confirmPassword) {
        showPopup("❌ Les mots de passe ne correspondent pas.");
        return;
    }

    // Envoi des données au backend
    fetch('/update-account/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            username: username,
            dob: dob,
            password: password
        })
    })
    .then(response => response.json())  // 🔹 Convertir en JSON
    .then(data => {
        if (data.success) {
            showPopup("✅ Vos informations ont été mises à jour avec succès !");
            setTimeout(() => {
                window.location.href = '/login/';
            }, 3000); // Redirection après 3 secondes
        } 
        else if (data.next_change_allowed) {  
            // Affiche un message avec la date de la prochaine modification possible
            showPopup(`⏳ Vous ne pouvez modifier votre mot de passe qu'une fois toutes les 2 semaines. 
            Vous pourrez le changer à partir du : <b>${data.next_change_allowed}</b>.`);
        } 
        else {
            showPopup("❌ Une erreur est survenue. Veuillez réessayer.");
        }
    })
    .catch(error => {
        console.error("⚠️ Erreur :", error);
        showPopup("⚠️ Une erreur s'est produite. Vérifiez votre connexion.");
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Sélectionner les champs Nom d'utilisateur et Date de naissance
    const usernameInput = document.getElementById("username");
    const dobInput = document.getElementById("dob");

    if (usernameInput) {
        usernameInput.setAttribute("readonly", true); // Empêche la modification
        usernameInput.style.backgroundColor = "#f0f0f0"; // Change légèrement la couleur pour indiquer qu'il est verrouillé
        usernameInput.style.cursor = "not-allowed"; // Change le curseur pour montrer que c'est inactif
    }

    if (dobInput) {
        dobInput.setAttribute("readonly", true);
        dobInput.style.backgroundColor = "#f0f0f0";
        dobInput.style.cursor = "not-allowed";
    }
});


function showPopup(message) {
    const popup = document.getElementById('success-popup');
    const popupMessage = document.getElementById('popup-message');

    
    // Ajoutez l'emoji et appliquez la couleur verte via une classe CSS
    popupMessage.innerHTML = `🌟 <span class="success-text">${message}</span>`;
    popup.style.display = 'flex';
}

function closePopup() {
    const popup = document.getElementById('success-popup');
    popup.style.display = 'none';
}

   document.addEventListener("DOMContentLoaded", function () {
        // Récupérer la date de naissance depuis le champ caché
        const dobHiddenInput = document.getElementById("profile-dob");
        const dob = dobHiddenInput ? dobHiddenInput.value : null;

        // Remplir le champ de date si une date est disponible
        const dobInput = document.getElementById("dob");
        if (dob && dobInput) {
            dobInput.value = dob;
        }
    });

