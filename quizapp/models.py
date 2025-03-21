import re
import os
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Sum
from django.conf import settings
from cryptography.fernet import Fernet
import base64
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.timezone import now

# Charger les variables d'environnement
load_dotenv()

User = get_user_model()

def get_default_user_id():
    """
    Retourne l'ID d'un utilisateur par défaut.
    Si aucun utilisateur n'existe, crée un utilisateur par défaut.
    """
    default_user = User.objects.first()
    if not default_user:
        default_user = User.objects.create_user(
            username='default_user',  # 🔥 Ajout du username obligatoire
            email='default@example.com',
            password='defaultpassword'
        )
    return default_user.id  # Renvoie l'ID, pas l'objet utilisateur

# 🔐 Chargement sécurisé de la clé Fernet depuis le fichier .env
ENCRYPTION_KEY = os.getenv("FERNET_SECRET_KEY")

if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = base64.urlsafe_b64encode(Fernet.generate_key()).decode()
    print("⚠️ Aucune clé trouvée dans .env, une nouvelle clé a été générée. Ajoutez-la à .env")
    
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

class Profile(models.Model):
    ESTABLISHMENT_CHOICES = [
        ('FMPC', 'Faculté de Médecine FMPC'),
        ('UM6', 'Université Mohammed VI'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    encrypted_password = models.TextField(blank=True, null=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    establishment = models.CharField(max_length=10, choices=ESTABLISHMENT_CHOICES, default='FMPC')

    def __str__(self):
        return f"{self.user.username} ({self.establishment})"

    def set_password(self, raw_password):
        """Chiffre et stocke le mot de passe en mettant à jour la date de changement."""
        if raw_password:
            self.encrypted_password = cipher_suite.encrypt(raw_password.encode()).decode()
            self.last_password_change = now()  # Met à jour la date de changement
            self.save()

    def get_password(self):
        """Déchiffre et retourne le mot de passe stocké de manière sécurisée."""
        if self.encrypted_password:
            try:
                return cipher_suite.decrypt(self.encrypted_password.encode()).decode()
            except Exception:
                return None  # En cas d'erreur de déchiffrement (clé invalide ou corrompue)
        return None

class QuizScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # L'utilisateur ayant soumis le score
    page = models.IntegerField()  # Numéro de la page du quiz
    score = models.FloatField()  # Score du quiz
    date = models.DateTimeField(auto_now_add=True)  # Date et heure de la soumission

    class Meta:
        ordering = ['-date']  # Tri par date décroissante

    def __str__(self):
        return f"{self.user.username} - Page {self.page} : {self.score}%"
    

class Exam(models.Model):
    ESTABLISHMENT_CHOICES = [
        ('FMPC', 'Faculté de Médecine FMPC'),
        ('UM6', 'Université Mohammed VI'),
    ]

    name = models.CharField(max_length=255, unique=True)  # Nom unique pour chaque examen
    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Semestre"
    )
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Module"
    )
    subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Matière"
    )
    is_remedial = models.BooleanField(
        default=False,
        help_text="Indique si cet examen est un rattrapage"
    )
    source = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Source générée automatiquement"
    )
    establishments = models.CharField(  # ✅ Utilisation correcte du champ `establishments`
        max_length=10,
        choices=ESTABLISHMENT_CHOICES,
        default='UM6',
        help_text="Établissement auquel l'examen est rattaché"
    )
    template_name = models.CharField(max_length=255, blank=True, null=True, help_text="Nom du fichier template")

    def save(self, *args, **kwargs):
        """
        Génération dynamique de la source en fonction de l'année, de la matière et de l'établissement.
        """
        if self.subject:
            # Extraction de l'année à partir du nom
            year_match = re.search(r'\d{4}', self.name)
            year = year_match.group(0) if year_match else "Année inconnue"

            # Construction de la source en incluant l'établissement
            base_name = f"{self.subject.name} {year}"
            if self.is_remedial:
                self.source = f"{base_name} Rattrapage - {self.get_establishments_display()}"  # ✅ Correction ici
            else:
                self.source = f"{base_name} - {self.get_establishments_display()}"  # ✅ Correction ici
        else:
            self.source = "Source inconnue"

        super().save(*args, **kwargs)

    def get_template_url(self):
        """
        Génère dynamiquement l'URL du fichier template en fonction du semestre et du module.
        """
        if not self.semester or not self.module or not self.template_name:
            return None

        semester_description = self.semester.description if self.semester.description else self.semester.name
        return reverse('dynamic_view', kwargs={
            'semester': semester_description,
            'module': self.module.id,
            'file_name': self.template_name.replace('.html', '')
        })

    def __str__(self):
        return f"{self.name} ({self.get_establishments_display()})"  # ✅ Correction ici



class ExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # L'utilisateur lié au résultat
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)  # Clé étrangère vers le modèle Exam
    score = models.FloatField()  # Le score de l'utilisateur pour cet examen
    attempt_date = models.DateTimeField(auto_now_add=True)  # Date de l'essai

    def calculate_score(self):
        # Exemple simplifié de calcul basé uniquement sur les scores existants de l'utilisateur
        correct_answers = QuizScore.objects.filter(user=self.user).aggregate(Sum('score'))['score__sum']
        total_possible_score = 50  # Exemple de total (ajustez selon vos besoins)
        if correct_answers is not None:
            return (correct_answers / total_possible_score) * 20
        return 0


def save(self, *args, **kwargs):
    if self.score is None:  # Si le score n'a pas été défini, le calculer
        self.score = self.calculate_score()
    super().save(*args, **kwargs)


class Subject(models.Model):
    name = models.CharField(max_length=100)  # Nom du sous-module
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)  # Code unique du sous-module
    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        related_name='subjects',
        null=True,
        blank=True
    )
    module = models.ForeignKey(  # Lien vers le module principal
        'Module',
        on_delete=models.CASCADE,
        related_name='subjects',
        null=True,  # Un sous-module peut exister sans module principal
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.module.name if self.module else 'Aucun module'})"

    @staticmethod
    def extract_subject_from_question_id(question_id):
        """
        Extrait le nom de la matière à partir de l'ID d'une question.
        Exemple : "Anatomie2023_23" -> "Anatomie"
        """
        match = re.match(r"([a-zA-Z]+)\d+_\d+", question_id)
        if match:
            return match.group(1)  # Retourne la partie du texte avant les chiffres
        return None


class Question(models.Model):
    id = models.CharField(
        max_length=50, 
        primary_key=True, 
        editable=True,  # Permet d'éditer l'ID
        unique=True
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        null=True,  # Permettre des valeurs NULL pour des migrations fluides
        blank=True,  # Permettre de ne pas renseigner ce champ dans l'admin
        default=None  # Facultatif : si vous ne voulez pas définir de valeur par défaut
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,  # Permet des valeurs NULL pour les lignes existantes
        blank=True  # Permet de ne pas remplir ce champ dans l'admin ou les formulaires
    )
    text = models.TextField()
    @property
    def source(self):
        """
        Dynamically fetch the source from the related exam.
        """
        if self.exam and self.exam.source:
            return self.exam.source
        return "Source inconnue"

    def __str__(self):
        return self.text
    


class Choice(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    image = models.ImageField(upload_to='choice_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Incorrect'})"

class QuestionPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    total_attempts = models.IntegerField(default=0)  # Nombre total de tentatives
    failures = models.IntegerField(default=0)  # Nombre d'échecs
    success_rate = models.FloatField(default=0.0)  # Taux de réussite (entre 0 et 1)
    last_attempt_date = models.DateTimeField(auto_now=True)  # Dernière tentative enregistrée

    def update_statistics(self, is_correct):
        """Met à jour les statistiques avec gestion des 30 dernières tentatives."""
        # Mise à jour des statistiques globales
        self.total_attempts += 1
        if not is_correct:
            self.failures += 1

        # Calcul du taux de réussite
        self.success_rate = 1 - (self.failures / self.total_attempts)
        self.save()

        # Supprimer les tentatives excédentaires (au-delà de 30)
        attempts = QuestionAttempt.objects.filter(user=self.user, question=self.question).order_by('-id')
        if attempts.count() > 30:
            attempts[30:].delete()

class QuestionAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.text} - {'Correct' if self.is_correct else 'Incorrect'}"
    
class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    unique_id = models.CharField(max_length=100, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Récupérer le plus grand numéro d'ordre existant pour la question
            last_comment = Comment.objects.filter(question=self.question).order_by('-unique_id').first()

            # Déterminer le prochain numéro d'ordre
            if last_comment and "_" in last_comment.unique_id:
                # Extraire la partie après "_" pour obtenir le numéro d'ordre
                last_order = int(last_comment.unique_id.split("_")[-1])
                comment_order = last_order + 1
            else:
                # Aucun commentaire existant, commencer à 1
                comment_order = 1

            # Générer l'ID unique basé sur le numéro d'ordre
            self.unique_id = f"{self.question.id}_{comment_order}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.question.text}"

class Message(models.Model):
    content = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    username = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('content', 'username', 'created_at')  # Empêche les doublons exacts

class Semester(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Description du semestre (remplissage manuel)")

    def __str__(self):
        return self.name


class Module(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du module")
    description = models.CharField(max_length=100, verbose_name="Description", editable=False)
    semester = models.ForeignKey(
        'Semester', on_delete=models.CASCADE, related_name='semester_modules', null=True, blank=True
    )  # Lien vers le semestre

    def save(self, *args, **kwargs):
        # Générer la description sans underscores à partir du nom
        self.description = self.name.replace('_', ' ')
        super(Module, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class UserSemester(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_semesters'
    )
    semesters = models.ManyToManyField(
        'Semester', 
        related_name='user_semesters',
        blank=True  # Permet de laisser ce champ vide
    )
    modules = models.ManyToManyField(
        'Module', 
        related_name='user_semesters',
        blank=True  # Permet de laisser ce champ vide
    )
    date_added = models.DateTimeField(default=now)  # 🆕 Date d'ajout automatique

    def __str__(self):
        semester_names = ", ".join(s.name for s in self.semesters.all()) if self.semesters.exists() else "Aucun semestre"
        return f"{self.user.username} - {semester_names} (Ajouté le {self.date_added.strftime('%Y-%m-%d %H:%M')})"

class UncorrectedQuestion(models.Model):
    id = models.CharField(
        max_length=50,
        primary_key=True,
        editable=True,  # Allow editing of IDs
        unique=True
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='uncorrected_questions',
        null=True,  # Allow null for smoother migrations
        blank=True,  # Optional in admin forms
        default=None
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    text = models.TextField()

    def __str__(self):
        return self.text


class UncorrectedChoice(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    question = models.ForeignKey(UncorrectedQuestion, on_delete=models.CASCADE, related_name='uncorrected_choices')
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text
    
    
class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(UncorrectedChoice, on_delete=models.CASCADE)
    question = models.ForeignKey(UncorrectedQuestion, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # Date et heure de la réponse


class Chapter(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='chapters',
        default=1  # Remplacez `1` par l'ID d'un sujet valide dans votre base de données
    )

    def __str__(self):
        return f"{self.name} - {self.subject.name}"

    



class Flashcard(models.Model):
    id = models.CharField(
        max_length=100,
        primary_key=True,
        editable=False
    )
    question = models.TextField()
    answer = models.TextField()
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='flashcards')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='flashcards',
        null=True,  # Permet de définir des flashcards sans utilisateur
        blank=True
    )
    is_global = models.BooleanField(default=False)  # Indique si la flashcard est globale

    def save(self, *args, **kwargs):
        if not self.id:
            # Compter le nombre de flashcards existantes pour cet utilisateur ou ce chapitre global
            flashcard_count = Flashcard.objects.filter(
                user=self.user, chapter=self.chapter
            ).count() + 1 if self.user else Flashcard.objects.filter(
                is_global=True, chapter=self.chapter
            ).count() + 1

            # Générer un ID personnalisé
            user_prefix = self.user.username if self.user else "global"
            self.id = f"{user_prefix}_{self.chapter.name}_{flashcard_count}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Flashcard for {self.chapter.name} by {self.user.username if self.user else 'Global'}"
    
class Source(models.Model):
    subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="La matière liée à cette source"
    )
    year = models.IntegerField(help_text="Année de la source")
    is_remedial = models.BooleanField(
        default=False,
        help_text="Indique si cette source correspond à un rattrapage"
    )

    def text_source(self):
        # Générer le texte synthétisé
        text = f"{self.subject.name} {self.year}"
        if self.is_remedial:
            text += " Rattrapage"
        return text

    text_source.short_description = "Text Source"  # Nom de la colonne dans l'admin

    def __str__(self):
        return self.text_source()