(function($) {
    $(document).ready(function() {
        // Surveille les changements dans le champ Exam
        $('#id_exam').change(function() {
            const examId = $(this).val();
            const questionField = $('#id_question');
            
            if (!examId) {
                questionField.html('<option value="">--------</option>'); // Reset if no exam
                return;
            }

            // Effectuer une requête AJAX pour récupérer les questions associées
            $.ajax({
                url: `/admin/quizapp/questions_for_exam/${examId}/`, // Endpoint pour récupérer les questions
                success: function(data) {
                    questionField.html('<option value="">--------</option>'); // Reset options
                    for (const question of data) {
                        questionField.append(
                            `<option value="${question.id}">${question.text}</option>`
                        );
                    }
                },
                error: function() {
                    alert("Impossible de charger les questions pour cet examen.");
                }
            });
        });
    });
})(django.jQuery);
