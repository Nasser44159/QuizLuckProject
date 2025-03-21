from django.http import HttpResponseForbidden
import re
from quizapp.models import UserSemester


class SemesterValidationMiddleware:
    """
    Middleware pour valider l'accès aux semestres en fonction de l'utilisateur.
    Il bloque tout chemin contenant un semestre non autorisé.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Étape 1 : Vérifier si l'URL contient un semestre (ex. : '/S1/', '/S7/...')
        semester_match = re.search(r'/S(\d+)/', request.path)  # Cherche un 'S<number>'
        if semester_match:
            requested_semester = f"SEMESTRE {semester_match.group(1)}"

            # Étape 2 : Récupérer les semestres autorisés pour l'utilisateur
            user_semesters = UserSemester.objects.filter(user=request.user).first()
            if not user_semesters:
                return HttpResponseForbidden("Vous n'avez accès à aucun semestre.")

            allowed_semesters = [semester.name for semester in user_semesters.semesters.all()]
            if requested_semester not in allowed_semesters:
                return HttpResponseForbidden(f"Vous n'avez pas accès au {requested_semester} et Fuck you.")

        # Étape 3 : Continuer la requête si tout est validé
        return self.get_response(request)
