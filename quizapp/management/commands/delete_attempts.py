from django.core.management.base import BaseCommand
from quizapp.models import QuestionAttempt
from datetime import datetime

class Command(BaseCommand):
    help = "Supprime les tentatives des utilisateurs le 1er mars et le 1er août de chaque année"

    def handle(self, *args, **kwargs):
        today = datetime.now()
        # Vérifiez si nous sommes le 1er mars ou le 1er août
        if today.month in [3, 8] and today.day == 1:
            # Supprimez toutes les tentatives
            deleted_count, _ = QuestionAttempt.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"{deleted_count} tentatives supprimées automatiquement."))
        else:
            self.stdout.write(self.style.WARNING("Aujourd'hui n'est pas une date de suppression programmée."))
