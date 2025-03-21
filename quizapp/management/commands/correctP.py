from django.core.management.base import BaseCommand
from quizapp.models import UncorrectedQuestion, UncorrectedChoice

class Command(BaseCommand):
    help = "Corrige les IDs des questions et choix en les décrémentant de 1."

    def handle(self, *args, **kwargs):
        prefixes = ["URG", "OB", "MCB", "SML", "SC", "NA", "COM", "AnatIV", "CP", "Pd", "IMP", "IMN", "RHU", "TRM", "SD", "SM", "ORL", "OPH", "URO", "NP"]
        
        self.stdout.write("Mise à jour des IDs des questions et choix...")

        # Traiter les questions
        questions = UncorrectedQuestion.objects.all()
        for question in questions:
            for prefix in prefixes:
                if question.id.startswith(prefix):
                    parts = question.id.split("_")
                    if len(parts) > 1:
                        number = int(parts[1])
                        if number == 1:
                            self.stdout.write(f"Suppression de la question : {question.id}")
                            question.delete()
                        else:
                            new_id = f"{parts[0]}_{number - 1}"
                            self.stdout.write(f"Modification de la question : {question.id} -> {new_id}")
                            question.id = new_id
                            question.save()
                    break

        # Traiter les choix
        choices = UncorrectedChoice.objects.all()
        for choice in choices:
            for prefix in prefixes:
                if choice.id.startswith(prefix):
                    parts = choice.id.split("_")
                    if len(parts) > 2:
                        number = int(parts[1])
                        if number == 1:
                            self.stdout.write(f"Suppression du choix : {choice.id}")
                            choice.delete()
                        else:
                            new_id = f"{parts[0]}_{number - 1}_{parts[2]}"
                            self.stdout.write(f"Modification du choix : {choice.id} -> {new_id}")
                            choice.id = new_id
                            choice.save()
                    break

        self.stdout.write("Mise à jour terminée avec succès.")
