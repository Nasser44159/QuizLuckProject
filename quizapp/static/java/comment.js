// PARTIE COMMENTAIRE

// Stocke l'ID de la question actuellement ouverte
let currentQuestionId = null;

// Fonction pour afficher un feedback à l'utilisateur
function showFeedback(message, type = 'info') {
    console.log(`[FEEDBACK] Message: ${message}, Type: ${type}`);
    const feedback = document.getElementById('feedback');
    if (!feedback) return;

    feedback.textContent = message;
    feedback.className = `feedback ${type}`; // Classe CSS: info, success, error
    feedback.style.display = 'block';

    // Cache le feedback après 3 secondes
    setTimeout(() => {
        feedback.style.display = 'none';
    }, 3000);
}

// Fonction pour basculer la section des commentaires
function toggleCommentSection(questionId, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const commentsSection = document.getElementById("comments-section");

    const isOpen = commentsSection.classList.contains("open");

    if (isOpen) {
        commentsSection.classList.remove("open");
        console.log("[INFO] Section fermée.");
    } else {
        commentsSection.classList.add("open");
        console.log("[INFO] Section ouverte pour la question :", questionId);

        if (questionId) {
            currentQuestionId = questionId;
            loadComments();
        }
    }
}

// Fonction pour ajouter un commentaire
function addComment(event) {
    if (event) {
        event.preventDefault(); // Empêche le comportement par défaut
    }

    const comment = document.getElementById('new-comment').value.trim();
    const alertBox = document.getElementById('comment-alert');

    // Cache l'alerte si elle est visible
    alertBox.style.display = 'none';

    if (comment === '') {
        alertBox.textContent = "Vous devez saisir un commentaire avant de l'envoyer.";
        alertBox.style.display = 'block';
        return;
    }

    console.log("[ACTION] Ajout d'un commentaire...");

    fetch('/add_comment/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
            question_id: currentQuestionId,
            content: comment,
        }),
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || "Erreur lors de l'ajout du commentaire.");
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alertBox.textContent = data.error; // Affiche le message d'erreur dans l'alerte
                alertBox.style.display = 'block';
                return;
            }

            console.log("[INFO] Commentaire ajouté avec succès :", data);
            loadComments(); // Recharge les commentaires
            document.getElementById('new-comment').value = ''; // Vide le champ de saisie
            alertBox.textContent = "Commentaire ajouté avec succès.";
            alertBox.style.backgroundColor = "#4CAF50"; // Vert pour le succès
            alertBox.style.display = 'block';

            // Cache l'alerte après 3 secondes
            setTimeout(() => {
                alertBox.style.display = 'none';
            }, 3000);
        })
        .catch(error => {
            alertBox.textContent = error.message;
            alertBox.style.display = 'block';
        });
}

// Fonction pour charger les commentaires
function loadComments() {
    const commentsList = document.getElementById('comments-list');
    commentsList.innerHTML = ''; // Réinitialise la liste des commentaires

    fetch(`/get_comments/${currentQuestionId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const comments = data.comments || [];

            console.log(`[INFO] Nombre de commentaires récupérés : ${comments.length}`);

            // Si aucun commentaire, afficher un message vide
            if (comments.length === 0) {
                const noCommentMessage = document.createElement('p');
                noCommentMessage.className = 'no-comments';
                noCommentMessage.textContent = 'Aucun commentaire pour cette question.';
                commentsList.appendChild(noCommentMessage);
                return;
            }

            // Pour chaque commentaire, créer dynamiquement un élément
            comments.forEach((comment) => {
                const commentItem = document.createElement('div');
                commentItem.className = 'comment-item';

                const commentDate = document.createElement('div');
                commentDate.textContent = comment.timestamp;

                const commentText = document.createElement('div');
                commentText.textContent = comment.content;

                // Ajout du bouton de suppression seulement si is_owner est vrai
                if (comment.is_owner) {
                    const deleteButton = document.createElement('button');
                    deleteButton.className = 'delete-button';
                    deleteButton.textContent = 'X';
                    deleteButton.onclick = () => deleteComment(comment.id);
                    commentItem.appendChild(deleteButton);
                }

                commentItem.appendChild(commentDate);
                commentItem.appendChild(commentText);
                commentsList.appendChild(commentItem);
            });
        })
        .catch(error => {
            console.error("[ERROR] Une erreur s'est produite lors du chargement des commentaires :", error);
        });
}

// Fonction pour supprimer un commentaire
function deleteComment(commentId) {
    console.log(`[ACTION] Suppression du commentaire ID: ${commentId}`);
    event.preventDefault();
    event.stopPropagation();

    fetch(`/delete_comment/${commentId}/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showFeedback(data.error, 'error');
                return;
            }

            console.log(`[INFO] Commentaire supprimé: ${data.message}`);
            loadComments(); // Recharge les commentaires
            showFeedback("Commentaire supprimé avec succès.", 'success');
        })
        .catch(error => {
            console.error("[ERROR] Une erreur s'est produite lors de la suppression :", error);
            showFeedback("Erreur lors de la suppression du commentaire.", 'error');
        });
}

// Fonction pour mettre à jour le badge de compteur de commentaires
function updateCommentCount(count) {
    const commentCountBadge = document.querySelector(`[data-comment-id="${currentQuestionId}"]`);
    if (commentCountBadge) {
        commentCountBadge.textContent = count;
    }
}

// Initialisation des badges pour toutes les questions
document.addEventListener('DOMContentLoaded', () => {
    const allQuestionIds = document.querySelectorAll('.comment-button');

    allQuestionIds.forEach(button => {
        const questionId = button.getAttribute('data-question-id');

        fetch(`/get_comments/${questionId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                const comments = data.comments || [];
                const commentCountBadge = document.querySelector(`[data-comment-id="${questionId}"]`);
                if (commentCountBadge) {
                    commentCountBadge.textContent = comments.length;
                }
            })
            .catch(error => {
                console.error(`[ERROR] Impossible de mettre à jour le badge pour la question ${questionId}:`, error);
            });
    });
});
