from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import Exam, ExamResult, Question, Choice, Subject, Comment, Message, Semester, UserSemester, Module, Profile
from django import forms
from .models import UncorrectedQuestion, UncorrectedChoice
from .models import Module, Chapter, Flashcard, Source
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.contrib.admin.filters import SimpleListFilter
from django.contrib.admin.filters import RelatedOnlyFieldListFilter


class ChoiceAdminForm(forms.ModelForm):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        required=False,
        label="Exam",
        help_text="Choisissez un examen pour filtrer les questions."
    )

    class Meta:
        model = Choice
        fields = ['id', 'exam', 'question', 'text', 'is_correct', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Par défaut, la liste des questions est vide
        self.fields['question'].queryset = Question.objects.none()

        # Si un examen est déjà sélectionné
        if 'exam' in self.data:
            try:
                exam_id = self.data.get('exam')
                self.fields['question'].queryset = Question.objects.filter(exam__id=exam_id)
            except (ValueError, TypeError):
                pass  # Aucun examen valide sélectionné
        elif self.instance.pk and self.instance.question:
            self.fields['question'].queryset = Question.objects.filter(exam=self.instance.question.exam)


# Affichage des images dans l'interface admin
def image_preview(obj):
    if obj.image:
        return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
    return "Pas d'image"
image_preview.short_description = "Aperçu de l'image"

# Admin pour les Questions
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface admin pour le modèle Question.
    - Affichage optimisé
    - Recherche avancée
    - Filtrage combiné Subject -> Exam
    - Attribution automatique du Subject lors de la sauvegarde
    """

    # Colonnes affichées dans l'interface admin
    list_display = ('id', 'text', 'exam', 'subject', 'get_source')  

    # Recherche par ID, texte, nom de l'examen et du sujet
    search_fields = ('id', 'text', 'exam__name', 'subject__name')  

    # Filtres : d'abord par subject, ensuite par exam (affichant uniquement les examens du subject sélectionné)
    list_filter = (
        ('subject', admin.RelatedOnlyFieldListFilter),  # Filtrer par Subject uniquement
        ('exam', admin.RelatedOnlyFieldListFilter),  # Ensuite filtrer par Exam du subject choisi
    )  

    # Champs inclus dans le formulaire d'édition
    fields = ('id', 'text', 'exam', 'subject')  

    def get_source(self, obj):
        """
        Récupère dynamiquement la source associée à l'examen.
        """
        return obj.exam.source if obj.exam and obj.exam.source else "Source inconnue"
    
    get_source.short_description = "Source"  # Titre de la colonne dans l'interface admin

    def save_model(self, request, obj, form, change):
        """
        Lors de l'enregistrement d'une question :
        - Si elle est liée à un examen, récupérer automatiquement son sujet.
        - Empêcher toute suppression accidentelle du subject si l'examen est défini.
        """
        if obj.exam and obj.exam.subject:
            obj.subject = obj.exam.subject  # Synchronisation automatique du sujet
        super().save_model(request, obj, form, change)



@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface admin pour le modèle Choice.
    - Recherche avancée
    - Filtrage combiné Subject -> Exam
    - Attribution automatique du Subject lors de la sauvegarde
    """

    list_display = ('id', 'text', 'is_correct', 'get_exam', 'get_subject', 'image_preview')  
    search_fields = ('text', 'question__text', 'question__exam__name', 'question__exam__subject__name')  

    # Filtrage : d'abord par subject, ensuite par exam (lié au subject sélectionné)
    list_filter = (
        ('question__exam__subject', admin.RelatedOnlyFieldListFilter),  # Filtrage par Subject
        ('question__exam', admin.RelatedOnlyFieldListFilter),  # Ensuite filtrage par Exam du subject choisi
    )  

    readonly_fields = ('image_preview',)  
    ordering = ['question__exam__name']  # Trie les examens par nom

    def get_exam(self, obj):
        """
        Récupère dynamiquement l'examen associé à la question du choix.
        """
        return obj.question.exam.name if obj.question and obj.question.exam else "Pas d'examen"
    get_exam.short_description = "Exam"

    def get_subject(self, obj):
        """
        Récupère dynamiquement le subject via question.exam.
        """
        return obj.question.exam.subject.name if obj.question and obj.question.exam and obj.question.exam.subject else "Pas de sujet"
    get_subject.short_description = "Subject"

    def image_preview(self, obj):
        """
        Affiche un aperçu de l'image associée au choix (si disponible).
        """
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = "Aperçu de l'image"

    def save_model(self, request, obj, form, change):
        """
        Lors de l'enregistrement d'un choix :
        - Si sa question est liée à un examen, attribuer automatiquement son subject.
        - Empêcher toute suppression accidentelle du subject si l'examen est défini.
        """
        if obj.question and obj.question.exam and obj.question.exam.subject:
            obj.subject = obj.question.exam.subject  # Synchronisation automatique du sujet
        super().save_model(request, obj, form, change)


class CustomUserAdmin(BaseUserAdmin):
    """Admin User qui gère `default` et `FMPC` en fonction de l'URL."""

    def get_queryset(self, request):
        """Affiche les Users selon l'interface admin utilisée."""
        if 'admin-fmpc' in request.path:
            return super().get_queryset(request).using('FMPC')  # Charge les users depuis FMPC
        return super().get_queryset(request).using('default')  # Charge depuis default

    def save_model(self, request, obj, form, change):
        """Sauvegarde l'utilisateur dans la bonne base selon l'interface utilisée."""
        if 'admin-fmpc' in request.path:
            obj.save(using='FMPC')  # Sauvegarde dans FMPC
        else:
            obj.save(using='default')  # Sauvegarde dans default
        super().save_model(request, obj, form, change)

admin.site.unregister(User)  # Désenregistrement de User s'il est déjà enregistré
admin.site.register(User, CustomUserAdmin)  # Réenregistrement propre

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'module', 'get_establishment', 'template_url', 'is_remedial', 'source')
    list_filter = ('is_remedial', 'semester', 'subject', 'module', 'establishments')  # ✅ Correction du champ
    search_fields = ('name', 'source', 'subject__name', 'module__name', 'establishments')  
    list_editable = ('is_remedial',)  
    readonly_fields = ('template_url', 'source')  
    fieldsets = (
        (None, {
            'fields': ('name', 'semester', 'module', 'subject', 'is_remedial', 'source', 'establishments')  # ✅ Correction du champ ici aussi
        }),
        ('Template', {
            'fields': ('template_name', 'template_url'),  
            'classes': ('collapse',),  
        }),
    )

    def get_establishment(self, obj):

        return obj.get_establishments_display()
    get_establishment.short_description = "Establishment"


    def template_url(self, obj):
        """
        Génère une URL cliquable pour le template si disponible.
        """
        url = obj.get_template_url()
        if url:
            return format_html('<a href="{}" target="_blank">Voir le template</a>', url)
        return "URL non disponible"

    template_url.short_description = "Template URL"  


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    """
    Interface admin pour les résultats d'examens.
    - Affichage optimisé avec user, exam, score et date.
    - Filtrage combiné : d'abord par utilisateur, puis par examen.
    - Score en lecture seule.
    """

    list_display = ('user', 'exam', 'score', 'attempt_date')  # Colonnes affichées
    readonly_fields = ('score',)  # Empêche la modification du score

    # 🔍 Ajoute les filtres utilisateur et examen
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),  # Filtrage par utilisateur
        ('exam', admin.RelatedOnlyFieldListFilter),  # Filtrage par examen
    )

    def save_model(self, request, obj, form, change):
        """
        Lors de l'enregistrement, si le score n'est pas défini, le calculer automatiquement.
        """
        if not obj.score:
            obj.score = obj.calculate_score()  # Calcul automatique du score
        super().save_model(request, obj, form, change)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'module', 'semester')  # Ajoute "module" dans l'admin
    list_filter = ('module', 'semester')  # Filtrer par module et semestre
    search_fields = ('name', 'code', 'module__name', 'semester__name')


class ExamFilter(SimpleListFilter):
    title = _("By exam")  # Nom du filtre
    parameter_name = "exam"

    def lookups(self, request, model_admin):
        """
        Extrait la liste des examens en prenant ce qui précède le premier "_" de unique_id.
        """
        exams = set(comment.unique_id.split('_')[0] for comment in model_admin.model.objects.all() if comment.unique_id)
        return [(exam, exam) for exam in sorted(exams)]

    def queryset(self, request, queryset):
        """
        Filtre les commentaires selon l'examen extrait de unique_id.
        """
        if self.value():
            return queryset.filter(unique_id__startswith=self.value())
        return queryset

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Interface admin pour les commentaires :
    - Suppression des colonnes Exam & Question (mais filtrage par Exam conservé).
    - Ajout du nom complet de l'utilisateur et de l'établissement.
    - Affichage de `content` juste après `unique_id`.
    """

    list_display = ('unique_id', 'content', 'full_name', 'establishment', 'created_at')

    # 🔍 Filtrage par utilisateur et par examen (basé sur unique_id)
    list_filter = ('user__profile__establishment', ExamFilter)

    search_fields = ('unique_id', 'content', 'user__username', 'user__first_name', 'user__last_name')

    readonly_fields = ('unique_id', 'created_at')

    def full_name(self, obj):
        """Affiche le nom complet de l'utilisateur."""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    full_name.admin_order_field = 'user__first_name'
    full_name.short_description = "Full Name"

    def establishment(self, obj):
        """Affiche l'établissement de l'utilisateur."""
        return obj.user.profile.establishment if obj.user.profile else "Inconnu"
    establishment.admin_order_field = 'user__profile__establishment'
    establishment.short_description = "Establishment"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface admin pour le modèle Message :
    - Remplace `username` par `full_name`.
    - Filtrage par date et anonymat.
    """

    list_display = ('content', 'is_anonymous', 'full_name', 'created_at')  # ✅ Remplace `username` par `full_name`
    list_filter = ('created_at', 'is_anonymous')  # ✅ Filtrage par date et anonymat
    search_fields = ('content', 'username__first_name', 'username__last_name')  # ✅ Recherche améliorée
    ordering = ('-created_at',)  # ✅ Trier par date (du plus récent au plus ancien)
    list_per_page = 20  # ✅ Afficher 20 messages par page

    def full_name(self, obj):
        """
        Remplace `username` par son nom complet.
        """
        if obj.username:
            return f"{obj.username.first_name} {obj.username.last_name}".strip()
        return "Utilisateur inconnu"
    
    full_name.admin_order_field = 'username__first_name'
    full_name.short_description = "Full Name"  # ✅ Affiche "Full Name" au lieu de "user"



@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')  # Afficher la colonne description
    search_fields = ('name', 'description')  # Permettre la recherche dans la description


@admin.register(UserSemester)
class UserSemesterAdmin(admin.ModelAdmin):
    """
    Interface admin optimisée pour UserSemester :
    - Affichage clair avec `full_name` au lieu de `user`.
    - Filtrage combiné : utilisateur, semestre et établissement.
    - Suppression de `modules` de l'affichage.
    """

    list_display = ('full_name', 'get_semesters', 'get_establishment', 'date_added')  # ✅ Remplace `user` & enlève `modules`
    filter_vertical = ('semesters',)  # ✅ Meilleure gestion des sélections
    search_fields = ('user__first_name', 'user__last_name', 'semesters__name')  # ✅ Recherche avancée

    # 🔍 Filtrage par utilisateur, semestre et établissement
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),  # ✅ Filtrage par utilisateur
        ('semesters', admin.RelatedOnlyFieldListFilter),  # ✅ Filtrage par semestre
        ('user__profile__establishment', admin.ChoicesFieldListFilter),  # ✅ Filtrage par établissement
    )

    def get_semesters(self, obj):
        """
        Affiche tous les semestres liés sous forme de liste.
        """
        return ", ".join([semester.name for semester in obj.semesters.all()])
    get_semesters.short_description = 'Semesters'

    def get_establishment(self, obj):
        """
        Récupère l'établissement de l'utilisateur (FMPC ou UM6).
        """
        return obj.user.profile.establishment if hasattr(obj.user, 'profile') else "Non défini"
    get_establishment.short_description = 'Establishment'  # ✅ Affichage du champ dans l'interface admin

    def full_name(self, obj):
        """
        Remplace `user` par son nom complet pour une meilleure lisibilité.
        """
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    full_name.admin_order_field = 'user__first_name'
    full_name.short_description = "Full Name"  # ✅ Affiche "Full Name" en colonne

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'semester')  # Ajouter description à l'affichage
    search_fields = ('name', 'semester')  # Permet la recherche par nom et code


@admin.register(UncorrectedQuestion)
class UncorrectedQuestionAdmin(admin.ModelAdmin):
    """
    Interface admin optimisée pour les questions non corrigées.
    - Recherche avancée
    - Filtrage combiné Subject -> Exam
    - Attribution automatique du Subject lors de la sauvegarde
    """

    # Colonnes affichées dans la liste admin
    list_display = ('id', 'text', 'exam', 'subject')

    # Recherche avancée
    search_fields = ('id', 'text', 'exam__name', 'subject__name')

    # Filtres : d'abord par Subject, ensuite par Exam (seulement les examens liés au Subject sélectionné)
    list_filter = (
        ('subject', RelatedOnlyFieldListFilter),  
        ('exam', RelatedOnlyFieldListFilter),  
    )  

    # Champs éditables dans le formulaire d'édition
    fields = ('id', 'text', 'exam', 'subject')

    def save_model(self, request, obj, form, change):
        """
        Lors de l'enregistrement d'une question non corrigée :
        - Si un examen est défini, récupérer automatiquement son subject.
        - Assurer que le subject ne soit pas effacé si l'examen est lié à un subject.
        """
        if obj.exam and obj.exam.subject:
            obj.subject = obj.exam.subject  # Associe le subject à partir de l'exam
        super().save_model(request, obj, form, change)

@admin.register(UncorrectedChoice)
class UncorrectedChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'question', 'exam')  # Add 'exam' to display
    search_fields = ('text', 'question__text')  # Allow searching within questions
    list_filter = ('question__exam',)  # Add filtering by exam

    def exam(self, obj):
        """Display the exam associated with the choice."""
        return obj.question.exam.name  # Access the related exam name
    exam.admin_order_field = 'question__exam'  # Enable sorting by exam
    exam.short_description = 'Exam'  # Set the display name in the admin interface

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')  # Affiche le nom et le sujet dans la liste
    search_fields = ('name', 'subject__name')  # Permet la recherche par nom de chapitre ou de sujet
    list_filter = ('subject',)  # Filtre les chapitres par sujet
    fields = ('name', 'description', 'subject')  # Champs affichés dans le formulaire

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'chapter', 'user', 'is_global')  # Afficher l'ID, la question, le chapitre, l'utilisateur et is_global
    list_filter = ('chapter', 'user', 'is_global')  # Ajouter des filtres par chapitre, utilisateur et is_global
    search_fields = ('id', 'question', 'answer', 'chapter__name', 'user__username')  # Recherche sur plusieurs champs
    readonly_fields = ('id',)  # Rendre l'ID non modifiable dans l'administration
    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'chapter', 'user', 'is_global')  # Champs modifiables
        }),
        ('Détails automatiques', {
            'fields': ('id',),  # Champ ID généré automatiquement
            'classes': ('collapse',),  # Optionnel : masquer sous une section repliée
        }),
    )
@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'year', 'is_remedial', 'text_source')  # Ajoute la colonne synthétique
    list_filter = ('subject', 'year', 'is_remedial')  # Permet de filtrer
    search_fields = ('subject__name', 'year')  # Recherche
    ordering = ('year', 'subject')  # Trie par défaut


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Interface Admin pour la gestion des Profils :
    - `full_name` remplace `first_name` & `last_name` pour une meilleure lisibilité.
    - Suppression de la colonne `user`.
    - Suppression de la colonne `staff_status`.
    - Ajout du filtrage par établissement.
    """
    list_display = ('full_name', 'email', 'birth_date', 'establishment')  # ✅ Suppression de `staff_status`
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'establishment')  
    list_filter = ('birth_date', 'establishment')  # ✅ Suppression du filtre `user__is_staff`

    def email(self, obj):
        """Affiche l'email de l'utilisateur."""
        return obj.user.email
    email.admin_order_field = 'user__email'  
    email.short_description = 'Email'

    def full_name(self, obj):
        """Fusionne `first_name` et `last_name` pour une meilleure lisibilité."""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()
    full_name.admin_order_field = 'user__first_name'  
    full_name.short_description = 'Full Name'

    def establishment(self, obj):
        """Affiche l'établissement de l'utilisateur."""
        return obj.establishment
    establishment.admin_order_field = 'establishment'
    establishment.short_description = 'Establishment'