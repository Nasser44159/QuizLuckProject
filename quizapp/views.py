from django.shortcuts import render
from django.http import Http404
import os, re
import random
from django.db import models
from quizapp.utils import get_valid_pagemodules
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User  # Modèle utilisateur par défaut
from .models import QuizScore, Exam, ExamResult, Comment
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from datetime import datetime
from django.shortcuts import render, get_object_or_404
import logging
from django.conf import settings
from quizapp.models import Question, QuestionAttempt, Choice, Subject, UserSemester, Module, Semester, Profile
from django.db.models import Count
from random import sample
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.core.mail import send_mail
from .models import Message
from django.http import HttpResponseForbidden
from quizapp.models import UncorrectedQuestion, UncorrectedChoice, UserResponse
from django.db.models import Max, Subquery, OuterRef
from .models import Module, Chapter, Flashcard
from cryptography.fernet import Fernet
import base64
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password

ENCRYPTION_KEY = base64.urlsafe_b64encode(Fernet.generate_key()).decode()

# Charger la clé Fernet pour le chiffrement des mots de passe
cipher_suite = Fernet(settings.FERNET_SECRET_KEY.encode())

def is_strong_password(password):
    """Vérifie si le mot de passe respecte les règles de sécurité."""
    if len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caractères."
    if not re.search(r"[A-Z]", password):
        return "Le mot de passe doit contenir au moins une majuscule."
    if not re.search(r"\d", password):
        return "Le mot de passe doit contenir au moins un chiffre."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Le mot de passe doit contenir au moins un caractère spécial."
    return None  # ✅ Le mot de passe est valide

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        first_name = request.POST.get("first_name").strip()
        last_name = request.POST.get("last_name").strip()
        birth_date = request.POST.get("birth_date")
        establishment = request.POST.get("establishment")  # ✅ Récupération de l’établissement

        username = generate_unique_username(first_name, last_name)

        form_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "establishment": establishment,  # ✅ Stocker l'établissement dans les données du formulaire
        }

        errors = []

        # Vérification des champs obligatoires
        if not all([email, password, confirm_password, first_name, last_name, birth_date, establishment]):
            errors.append("Tous les champs sont obligatoires.")

        # Vérifier si l'email est déjà utilisé
        if User.objects.filter(email=email).exists():
            errors.append("Cet email est déjà utilisé.")

        # Vérifier si les mots de passe correspondent
        if password != confirm_password:
            errors.append("Les mots de passe ne correspondent pas.")

        # Vérifier la complexité du mot de passe
        if len(password) < 8:
            errors.append("Le mot de passe doit contenir au moins 8 caractères.")
        if not re.search(r"\d", password):
            errors.append("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r"[A-Z]", password):
            errors.append("Le mot de passe doit contenir au moins une majuscule.")
        if not re.search(r"[^a-zA-Z0-9]", password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial.")

        # Afficher toutes les erreurs en une seule fois
        if errors:
            return render(request, "register.html", {"form_data": form_data, "errors": errors})

        # Convertir la date de naissance
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            errors.append("La date de naissance doit être au format JJ-MM-AAAA.")
            return render(request, "register.html", {"form_data": form_data, "errors": errors})

        try:
            # ✅ Création de l'utilisateur
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                first_name=first_name,
                last_name=last_name,
            )

            # ✅ Création du profil utilisateur avec l'établissement choisi
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'birth_date': birth_date, 'establishment': establishment}
            )

            if not created:
                profile.birth_date = birth_date
                profile.establishment = establishment  # ✅ Mise à jour de l’établissement
                profile.save()

            # ✅ Chiffrement du mot de passe
            profile.encrypted_password = cipher_suite.encrypt(password.encode()).decode()
            profile.save()

            messages.success(request, "Votre compte a été créé avec succès. Connectez-vous !")
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Une erreur s'est produite : {str(e)}")
            return render(request, "register.html", {"form_data": form_data, "errors": errors})

    return render(request, "register.html")


def generate_unique_username(first_name, last_name):
    """ 
    Génère un username sous la forme 'Prenom_Nom' en remplaçant tous les espaces par '_'
    et ajoute un suffixe (_1, _2, ...) en cas de doublon.
    """

    # Normaliser le prénom et le nom en remplaçant les espaces par des underscores
    base_username = f"{first_name}_{last_name}"
    base_username = re.sub(r"\s+", "_", base_username)  # Remplace tous les espaces par "_"
    
    username = base_username
    count = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{count}"
        count += 1

    return username

logging.basicConfig(level=logging.DEBUG, force=True)  # 🔥 Active les logs à 100%

# Créer un logger spécifique pour my_login_view
logger = logging.getLogger('my_login_view')

def my_login_view(request):
    print("🚀 Vue `my_login_view` appelée", flush=True)
    logger.debug("🚀 Vue `my_login_view` appelée")

    if request.method == "POST":
        print("📩 Requête POST reçue", flush=True)
        
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"📧 Email reçu: {email}", flush=True)

        # 🔍 Trouver l'utilisateur correspondant à l'email
        try:
            user = User.objects.get(email=email)  # Chercher l'utilisateur via l'email
            username = user.username
            print(f"✅ Utilisateur trouvé: {username}", flush=True)
        except User.DoesNotExist:
            print(f"❌ Aucun utilisateur trouvé avec cet email: {email}", flush=True)
            return JsonResponse({'error': "E-mail introuvable"}, status=400)

        # 🔐 Authentifier avec le username et le password
        print(f"🔍 Tentative d'authentification pour {username}...", flush=True)
        user_authenticated = authenticate(request, username=username, password=password)

        if user_authenticated is not None:
            print(f"✅ Authentification réussie pour {username}", flush=True)
            login(request, user_authenticated)  # 🔥 Connexion Django
            return JsonResponse({'redirect_url': '/'})  # 🔥 Redirige vers la page d'accueil définie par `path('', views.home, name='home')`
        else:
            print("❌ Mot de passe incorrect ou problème d'authentification", flush=True)
            return JsonResponse({'error': "E-mail ou mot de passe incorrect"}, status=400)

    print("🔙 Retour à la page de connexion", flush=True)
    return render(request, 'login.html')


def home(request):
    user_semesters = UserSemester.objects.filter(user=request.user)
    context = {
        'user_semesters': user_semesters
    }
    return render(request, 'pagedacceuil.html', context)


# Listes valides pour validation
VALID_SEMESTERS = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']
VALID_MODULES = ['Anatomie_1', 'Biochimie_et_chimie', 'Biologie_et_Genetique', 'Biophysique',
                 'Sante_publique_et_Biostatistique', 'Methodo_et_termino', 
                 'Anatomie_II', 'Histologie-Embryologie', 'Sciences-Humaines', 
                 'Anatomie_Pathologique_generale', 
                 'Maladies_Infectieuses_and_Parasytologie_et_Mycologie', 'Radiologie', 
                 'Pathologie_cardiovasculaire', 'Pathologie_de_l_appareil_digestif', 
                 'Pathologie_respiratoire', 'Cancerologie_Hematologie', 
                 'Glandes_endocrines_peau', 'Maladie_du_Systeme_Nerveux']

logger = logging.getLogger(__name__)

def page_view(request, semester, template_name):
     # Ajoutez un message de log au niveau DEBUG

    if semester not in VALID_SEMESTERS or template_name not in VALID_MODULES:
        raise Http404("Page not found")  # Retourne une 404 si les paramètres sont invalides
    try:
        return render(request, f'{semester}/{template_name}.html')  # Charge dynamiquement le template
    except:
        raise Http404("Page not found")


# Générer VALID_PAGEMODULE dynamiquement
templates_dir = os.path.join('quizapp', 'templates')  # Adaptez selon votre structure
VALID_PAGEMODULE = get_valid_pagemodules(templates_dir)

def render_favorite(request, semester, favorite_name):

    # Construire le chemin complet pour le fichier Favori dans le dossier du semestre
    templates_dir = os.path.join('quizapp', 'templates', semester)
    file_path = os.path.join(templates_dir, f"{favorite_name}.html")

    if not os.path.exists(file_path):
        raise Http404(f"Le fichier {favorite_name}.html n'existe pas dans {semester}.")

    # Construire le chemin du template pour Django
    template_path = f'{semester}/{favorite_name}.html'

    try:
        return render(request, template_path)
    except Exception as e:
        print(f"Erreur lors du rendu : {e}")
        raise Http404("Le fichier demandé est introuvable.")



    
from django.http import Http404
from django.shortcuts import render
from .models import UserSemester, Module

@login_required
def get_user_semesters(request):
    """
    Vue pour récupérer les semestres accessibles à l'utilisateur authentifié.
    Si aucun semestre n'est attribué, le serveur envoie un message spécifique.
    """
    try:
        user_semester = UserSemester.objects.filter(user=request.user).first()

        if not user_semester:
            return JsonResponse({
                'accessible_semesters': [],
                'message': "Vous n'êtes toujours pas abonné ! Qu'est-ce que vous attendez ?!"
            }, status=200)  # ✅ Liste vide + message avec HTTP 200

        semesters = user_semester.semesters.all()
        semester_names = [semester.name for semester in semesters]

        return JsonResponse({
            'accessible_semesters': semester_names,
            'message': None  # Aucune alerte si l'utilisateur a des semestres
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': 'Une erreur est survenue lors de la récupération des semestres.'}, status=500)

    
@login_required
def get_accessible_modules(request):
    """
    Vue pour récupérer les modules accessibles avec leurs descriptions.
    """
    try:
        # Récupérer les semestres de l'utilisateur
        user_semesters = UserSemester.objects.filter(user=request.user)

        # Si aucun semestre n'est attribué, retourner une liste vide
        if not user_semesters.exists():
            return JsonResponse({'accessible_modules': []}, status=200)  # ✅ Renvoie une liste vide au lieu d'une erreur

        modules_by_semester = []

        for user_semester in user_semesters:
            for semester in user_semester.semesters.all():
                # Récupérer les modules et descriptions
                modules = Module.objects.filter(semester=semester)
                semester_data = {
                    'semester_name': semester.name,
                    'semester_description': semester.description,
                    'modules': [
                        {
                            'module_name': module.name,
                            'description': module.description
                        } for module in modules
                    ]
                }
                modules_by_semester.append(semester_data)

        return JsonResponse({'accessible_modules': modules_by_semester}, status=200)

    except Exception as e:
        return JsonResponse({'error': 'Une erreur est survenue lors de la récupération des modules.'}, status=500)

    
@login_required
def update_account(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user = request.user
            profile = Profile.objects.get(user=user)

            username = data.get('username')
            dob = data.get('dob')
            password = data.get('password')

            # Vérifier si l'utilisateur a changé son mot de passe il y a moins de 2 semaines
            if password:
                if profile.last_password_change and (now() - profile.last_password_change) < timedelta(weeks=2):
                    next_change_date = profile.last_password_change + timedelta(weeks=2)
                    return JsonResponse({
                        'error': 'Vous ne pouvez changer votre mot de passe qu’une fois toutes les 2 semaines.',
                        'next_change_allowed': next_change_date.strftime('%d/%m/%Y %H:%M')
                    }, status=400)

                # Mettre à jour le mot de passe
                user.password = make_password(password)
                profile.encrypted_password = cipher_suite.encrypt(password.encode()).decode()
                profile.last_password_change = now()  # Mettre à jour la date du dernier changement

            if username:
                user.username = username
            if dob:
                profile.birth_date = dob

            user.save()
            profile.save()

            return JsonResponse({'success': True, 'message': 'Compte mis à jour avec succès.'})

        except Exception as e:
            return JsonResponse({'error': f'Erreur : {str(e)}'}, status=400)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def dynamic_view(request, semester, module=None, file_name=None):
    user_semesters = UserSemester.objects.filter(user=request.user)

    # Semestres et modules autorisés
    authorized_semesters = {s.name for us in user_semesters for s in us.semesters.all()}
    authorized_modules = {m.name for us in user_semesters for m in us.modules.all()}

    # Ajout de prints pour debug
    print("Utilisateur connecté :", request.user.username)
    print("Semestre demandé :", semester)
    print("Modules autorisés :", authorized_modules)
    print("Semestres autorisés avant modification :", authorized_semesters)

    # Remplacer S1 par SEMESTRE 1 pour les comparaisons
    formatted_semester = semester.upper().replace("S", "SEMESTRE ")
    authorized_semesters = {s.lower() for s in authorized_semesters}

    print("Semestre demandé après formatage :", formatted_semester)
    print("Semestres autorisés après modification :", authorized_semesters)

    # Vérification des permissions pour le semestre
    if formatted_semester.lower() not in authorized_semesters:
        print("Erreur : Semestre non autorisé.")
        raise Http404("Semestre non autorisé.")

    # Vérification des permissions pour le module
    if module and module not in authorized_modules:
        print("Erreur : Module non autorisé.")
        raise Http404("Module non autorisé.")

    # Initialisation de la variable pour tous les cas
    semesters_with_modules = {}

    # Si pas de module ni de fichier, afficher les modules disponibles
    if not module and not file_name:
        for us in user_semesters:
            for s in us.semesters.all():
                # Filtrer les modules autorisés pour ce semestre
                authorized_modules_for_semester = us.modules.filter(semesters=s, name__in=authorized_modules)
                semesters_with_modules[s.name] = authorized_modules_for_semester

        print("Modules disponibles par semestre (autorisés uniquement) :", semesters_with_modules)
        return render(request, 'modules_available.html', {'semesters_with_modules': semesters_with_modules})

    # Transformer SEMESTRE X en S1 pour trouver les fichiers
    file_path_semester = formatted_semester.replace("SEMESTRE ", "S")

    # Gestion des fichiers et modules
    template_path = None
    if file_name and module:
        template_path = f'{file_path_semester}/{module}/{file_name}.html'
    elif module:
        template_path = f'{file_path_semester}/{module}.html'
    else:
        print("Erreur : Module ou fichier non spécifié.")
        raise Http404("Module ou fichier non spécifié.")

    # Rendu du template
    try:
        print("Chemin du template à rendre :", template_path)
        return render(request, template_path, {'semesters_with_modules': semesters_with_modules})
    except Exception as e:
        print(f"Erreur de rendu : {e}")
        raise Http404("Le fichier demandé est introuvable.")





def load_correct_answers(exam_name):
    # Utiliser STATICFILES_DIRS pour accéder au répertoire statique pendant le développement
    static_dir = os.path.join(settings.BASE_DIR, 'quizapp', 'static', 'data')
    json_path = os.path.join(static_dir, f'{exam_name}_correct_answers.json')

    # Vérifiez si le fichier existe
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Fichier JSON introuvable : {json_path}")

    print(f"Chargement du fichier JSON : {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)



@login_required
def module_details(request, semester, module_description):
    try:

        # Recherche du module par sa description
        module_instance = Module.objects.get(description=module_description, semester__name=semester)
        exams = Exam.objects.filter(module=module_instance).values('name', 'score')
        exams_list = list(exams)

        return JsonResponse({'exams': exams_list}, status=200)
    except Module.DoesNotExist:
        return JsonResponse({'error': f"Module '{module_description}' introuvable pour le semestre '{semester}'."}, status=404)
    except Exception as e:
        return JsonResponse({'error': f"Erreur interne : {str(e)}"}, status=500)
    
@csrf_exempt
def soumettre_quiz(request):
    if request.method == 'POST':
        try:
            print("Requête POST reçue.")
            data = json.loads(request.body)
            print(f"Données reçues : {data}")

            # Récupérer le nom de l'examen
            exam_name = data.get('exam_name')
            if not exam_name:
                print("Erreur : Nom de l'examen manquant dans la requête.")
                return JsonResponse({'status': 'error', 'message': "Nom de l'examen manquant."}, status=400)
            print(f"Nom de l'examen : {exam_name}")

            # Charger les réponses correctes depuis le fichier JSON
            try:
                correct_answers = load_correct_answers(exam_name)
                print(f"Réponses correctes chargées pour l'examen : {exam_name}")
            except FileNotFoundError as e:
                print(f"Erreur : Fichier JSON des réponses correctes introuvable pour l'examen {exam_name} - {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=404)

            # Récupérer les réponses utilisateur
            user_answers = data.get('userAnswers', {})
            print(f"Réponses utilisateur : {user_answers}")

            total_questions = len(correct_answers)
            print(f"Nombre total de questions dans l'examen : {total_questions}")

            total_questions_answered = 0
            correct_count = 0

            # Comparer les réponses utilisateur avec les réponses correctes
            for question_id, correct_answer in correct_answers.items():
                print(f"Question ID : {question_id}, Réponse correcte : {correct_answer}")
                user_answer = user_answers.get(question_id, {}).get("selected", [])
                print(f"Réponse utilisateur pour la question {question_id} : {user_answer}")

                if user_answer:
                    total_questions_answered += 1
                    if set(user_answer) == set(correct_answer):
                        correct_count += 1
                        print(f"Réponse correcte pour la question {question_id}.")
                    else:
                        print(f"Réponse incorrecte pour la question {question_id}.")
                else:
                    print(f"Aucune réponse donnée pour la question {question_id}.")

            print(f"Nombre total de questions répondues : {total_questions_answered}")
            print(f"Nombre total de réponses correctes : {correct_count}")

            # Calculer le score
            score = (correct_count / total_questions) * 20 if total_questions_answered > 0 else 0
            print(f"Score calculé : {score}")

            # Enregistrer le résultat
            user = request.user
            print(f"Utilisateur : {user.username}")

            try:
                exam = Exam.objects.get(name=exam_name)
                print(f"Examen trouvé dans la base : {exam.name}")
            except Exam.DoesNotExist:
                print(f"Erreur : L'examen {exam_name} n'existe pas dans la base.")
                return JsonResponse({'status': 'error', 'message': f"L'examen {exam_name} n'existe pas."}, status=404)

            ExamResult.objects.create(user=user, exam=exam, score=score)
            print(f"Résultat enregistré pour l'utilisateur {user.username} et l'examen {exam_name}.")

            return JsonResponse({'status': 'success', 'score': score, 'message': 'Score enregistré avec succès.'})

        except Exception as e:
            print(f"Erreur serveur inattendue : {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    print("Méthode non autorisée. Seules les requêtes POST sont acceptées.")
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)





@login_required
def resultats(request):
    user = request.user

    # Récupérer les résultats d'examens de l'utilisateur
    exam_results = ExamResult.objects.filter(user=user).order_by("exam__name", "attempt_date")

    # Récupérer les semestres accessibles pour l'utilisateur
    user_semesters = UserSemester.objects.filter(user=user)
    if not user_semesters.exists():
        return render(request, 'resultats.html', {'error': 'Aucun semestre accessible'})

    semester_data = []
    for user_semester in user_semesters:
        for semester in user_semester.semesters.all():
            modules = Module.objects.filter(semester=semester)
            modules_data = []
            for module in modules:
                # Filtrer les examens avec au moins une tentative
                exams = Exam.objects.filter(module=module, examresult__user=user).distinct()

                # Construction des données des examens
                exams_data = [
                    {
                        'exam_name': exam.source,  # Utiliser la source de l'examen
                        'score': ExamResult.objects.filter(exam=exam, user=user).latest('attempt_date').score,
                        'date': ExamResult.objects.filter(exam=exam, user=user).latest('attempt_date').attempt_date.strftime('%Y-%m-%d'),
                    }
                    for exam in exams
                ]

                modules_data.append({
                    'module_name': module.description,
                    'exams': exams_data
                })
            semester_data.append({
                'semester_name': semester.name,
                'modules': modules_data
            })

    # Organiser les résultats par source d'examen
    results_by_exam = {}
    for result in exam_results:
        exam_source = result.exam.source
        if exam_source not in results_by_exam:
            results_by_exam[exam_source] = []
        results_by_exam[exam_source].append(result)

    return render(request, "resultats.html", {
        "user": user,
        "results_by_exam": results_by_exam,
        "semester_data": semester_data,
    })

@login_required
def get_exam_chart_data(request, source):
    try:
        # Log pour la source demandée
        print(f"Requête reçue pour récupérer les données pour l'examen : {source}")

        # Rechercher l'examen correspondant
        exam = Exam.objects.get(source=source)
        print(f"Examen trouvé : {exam}")

        # Récupérer les résultats liés à cet examen et à l'utilisateur
        results = ExamResult.objects.filter(exam=exam, user=request.user).order_by('attempt_date')
        print(f"Résultats trouvés : {results}")

        # Construire les données pour le graphique
        data = {
            'labels': [result.attempt_date.strftime('%Y-%m-%d') for result in results],
            'scores': [result.score for result in results],
        }

        return JsonResponse(data)

    except Exam.DoesNotExist:
        print(f"Examen introuvable pour la source : {source}")
        return JsonResponse({'error': 'Examen introuvable'}, status=404)
    except Exception as e:
        print(f"Erreur lors du traitement de la requête : {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def get_semester_average_data(request, semester_name):
    try:
        # Trouver le semestre
        semester = get_object_or_404(Semester, name=semester_name)
        modules = Module.objects.filter(semester=semester)

        module_averages = []
        total_score = 0
        total_modules = 0

        for module in modules:
            # Calculer la moyenne des examens pour chaque module
            exams = Exam.objects.filter(module=module)
            scores = [
                ExamResult.objects.filter(exam=exam, user=request.user).latest('attempt_date').score
                for exam in exams if ExamResult.objects.filter(exam=exam, user=request.user).exists()
            ]

            if scores:
                module_average = sum(scores) / len(scores)
                module_averages.append({'module_name': module.description, 'average': round(module_average, 2)})
                total_score += module_average
                total_modules += 1
            else:
                # Aucun examen tenté pour ce module
                module_averages.append({'module_name': module.description, 'average': 0})

        # Calculer la moyenne globale du semestre
        semester_average = round(total_score / total_modules, 2) if total_modules > 0 else 0

        return JsonResponse({
            'module_averages': module_averages,
            'semester_average': semester_average
        })

    except Semester.DoesNotExist:
        return JsonResponse({'error': f"Semestre '{semester_name}' introuvable."}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def track_attempts(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_choice_ids = data.get('full_choice_ids', [])
            question_name = data.get('question_name', "")

            # Extraire l'ID de la question à partir d'un choix (on enlève la partie lettre)
            question_id = '_'.join(full_choice_ids[0].split('_')[:-1])

            # Récupérer la question correspondante
            question = Question.objects.get(id=question_id)
            print(f"ID de la question extrait : {question_id}")


            # Récupérer les choix corrects associés à la question
            correct_choices = list(Choice.objects.filter(question=question, is_correct=True).values_list('id', flat=True))
            print(f"Choix corrects pour la question {question_id} : {correct_choices}")

            # Comparer les choix de l'utilisateur aux choix corrects
            is_correct = set(full_choice_ids) == set(correct_choices)
            print(f"Résultat de la comparaison : {is_correct}")

            # Enregistrer la tentative
            QuestionAttempt.objects.create(
                user=request.user,
                question=question,
                is_correct=is_correct
            )

            # Garder uniquement les 30 dernières tentatives pour cette question et cet utilisateur
            attempts = QuestionAttempt.objects.filter(user=request.user, question=question).order_by('-id')
            if attempts.count() > 30:
                # Supprimer les plus anciennes tentatives
                to_delete_ids = [attempt.id for attempt in attempts[30:]]
                QuestionAttempt.objects.filter(id__in=to_delete_ids).delete()

 # Calcul des statistiques
            total_attempts = attempts.count()
            failures = attempts.filter(is_correct=False).count()
            failure_rate = failures / total_attempts if total_attempts > 0 else 0
            consecutive_failures = 0

            # Parcourir les tentatives récentes pour calculer les échecs consécutifs
            for attempt in attempts:
                if attempt.is_correct:
                    break
                consecutive_failures += 1

            # Calcul du taux de succès
            failures = attempts.filter(is_correct=False).count()
            success_rate = (total_attempts - failures) / total_attempts if total_attempts > 0 else 0

            # Gestion des alertes
            alert = None
            if consecutive_failures >= 3:
                alert = {
                    'type': 'consecutive_failures',
                    'message': f"⚠️ Vous avez échoué {consecutive_failures} fois de suite à cette question. Revoir le cours est conseillé.",
                    'color': '#ffcccb'
                }


            # Si l'utilisateur réussit, réinitialiser les échecs consécutifs
            if is_correct:
                consecutive_failures = 0
                alert = None

            return JsonResponse({
                'is_correct': is_correct,
                'total_attempts': total_attempts,
                'failures': failures,
                'failure_rate': failure_rate,
                'alert': alert
            })

        except Question.DoesNotExist:
            print(f"Erreur : La question '{question_id}' n'existe pas.")
            return JsonResponse({'error': f"La question '{question_id}' n'existe pas."}, status=404)
        except Exception as e:
            print(f"Erreur inattendue : {str(e)}")

    return JsonResponse({'error': 'Pas de donnees.'}, status=405)

def questions_for_exam(request, exam_id):
    questions = Question.objects.filter(exam_id=exam_id).values('id', 'text')
    alerts = []

    for question in questions:
        # Récupérer les dernières tentatives pour chaque question
        attempts = QuestionAttempt.objects.filter(
            user=request.user, question_id=question['id']
        ).order_by('-timestamp')[:30]

        consecutive_failures = 0
        for attempt in attempts:
            if not attempt.is_correct:
                consecutive_failures += 1
            else:
                break

        if consecutive_failures >= 3:
            alerts.append({
                'question_id': question['id'],
                'message': f"⚠️ Vous avez échoué {consecutive_failures} fois de suite à cette question. Revoir le cours est conseillé.",
                'color': '#ffcccb'
            })

    return JsonResponse({
        'questions': list(questions),
        'alerts': alerts,
    })

logging.basicConfig(level=logging.DEBUG)

@login_required
def start_challenge(request):
    if request.method == "POST":

        # Récupérer les matières sélectionnées
        selected_subjects = request.POST.getlist('subjects')

        if not selected_subjects:
            return HttpResponse("Erreur : Vous devez sélectionner une matière.", status=400)

        # Récupérer le nombre de questions
        try:
            num_questions = int(request.POST.get('num_questions', 0))
            if num_questions < 1 or num_questions > 10:
                return HttpResponse("Erreur : Le nombre de questions doit être compris entre 1 et 10.", status=400)
        except ValueError:
            return HttpResponse("Erreur : Le nombre de questions est invalide.", status=400)

        # Récupérer le mode
        selected_mode = request.POST.get('mode', 'sans_faute')

        # Enregistrer les données dans la session
        request.session['selected_subjects'] = selected_subjects
        request.session['num_questions'] = num_questions
        request.session['mode'] = selected_mode

        # Redirection en fonction du mode
        if selected_mode == 'rapidite':
            return redirect('time_challenge')  # Vue pour le mode Rapidité
        elif selected_mode == 'sans_faute':
            return redirect('challenge')  # Vue pour le mode Sans Faute

        # Si le mode est invalide
        return HttpResponse("Erreur : Mode sélectionné invalide.", status=400)

    # Si la méthode est GET, afficher le formulaire

    # Récupérer les semestres auxquels l'utilisateur a accès
    user_semesters = UserSemester.objects.filter(user=request.user).first()
    if not user_semesters:
        return render(request, 'start_challenge.html', {'subjects': []})

    # Récupérer les matières des semestres autorisés
    allowed_semesters = user_semesters.semesters.all()
    subjects = Subject.objects.filter(semester__in=allowed_semesters)


    return render(request, 'start_challenge.html', {'subjects': subjects})


def challenge(request):
    if request.method == "GET":

        # Récupérer les matières sélectionnées dans la session
        selected_subjects = request.session.get('selected_subjects', [])
        num_questions_per_subject = request.session.get('num_questions', 10)

        print(f"Matières sélectionnées : {selected_subjects}")
        print(f"Nombre de questions par matière : {num_questions_per_subject}")

        if not selected_subjects or num_questions_per_subject < 1:
            return render(request, 'challenge.html', {
                'error': "Aucune matière ou nombre de questions valide trouvé. Veuillez recommencer."
            })

        try:
            # Récupérer les matières sélectionnées depuis la base de données
            subjects = Subject.objects.filter(id__in=selected_subjects)
            print(f"Matières sélectionnées (codes) : {[subject.code for subject in subjects]}")

            # Préparer les questions pour chaque matière
            questions = []
            for subject in subjects:
                print(f"Traitement de la matière : {subject.code}")

                if subject.code == "AD":  # Maladies digestives : exclure les questions dont l'ID commence par ADC
                    print("Matière détectée : Maladies digestives")
                    subject_questions = Question.objects.filter(
                        id__startswith=subject.code
                    ).exclude(id__startswith="ADC").order_by('?')[:num_questions_per_subject]

                elif subject.code == "CL":  # Cardiologie : exclure les questions dont l'ID commence par CLC
                    print("Matière détectée : Cardiologie")
                    subject_questions = Question.objects.filter(
                        id__startswith=subject.code
                    ).exclude(id__startswith="CLC").order_by('?')[:num_questions_per_subject]

                else:  # Matières standards
                    print(f"Matière standard détectée : {subject.code}")
                    subject_questions = Question.objects.filter(
                        id__startswith=subject.code
                    ).order_by('?')[:num_questions_per_subject]

                # Logs pour le débogage des questions
                print(f"Questions trouvées pour {subject.code} avant exclusion : {Question.objects.filter(id__startswith=subject.code).count()}")
                print(f"Questions trouvées pour {subject.code} après exclusion : {subject_questions.count()}")

                if not subject_questions.exists():
                    print(f"Aucune question trouvée pour la matière {subject.code} avec les filtres.")
                    continue

                questions.extend(subject_questions)

            print(f"Total de questions générées : {len(questions)}")
            if not questions:
                return render(request, 'challenge.html', {
                    'error': "Aucune question disponible pour les matières sélectionnées."
                })

            # Préparer les données des questions pour le frontend
            questions_data = []
            for question in questions:
                choices = question.choices.all()
                correct_choices = question.choices.filter(is_correct=True).values_list('id', flat=True)

                # Log pour afficher les propositions correctes

                # Déterminer la source en utilisant la colonne `source` de l'examen
                source = question.exam.source if question.exam and question.exam.source else "Source inconnue"

                questions_data.append({
                    'id': question.id,
                    'text': question.text,
                    'choices': [{'id': choice.id, 'text': choice.text} for choice in choices],
                    'correct_choices': list(correct_choices),
                    'source': source,  # Utilisation de la source de l'examen
                })

            # Déterminer la première question pour l'affichage
            first_question = questions_data[0]

            return render(request, 'challenge.html', {
                'first_question': first_question,
                'questions': questions_data,
            })

        except Exception as e:
            return render(request, 'challenge.html', {
                'error': "Une erreur s'est produite lors de la génération des questions."
            })

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)



def time_challenge(request):
    if request.method == "GET":

        # Récupérer les données de la session
        selected_subjects = request.session.get('selected_subjects', [])
        num_questions_per_subject = request.session.get('num_questions', 10)

        print(f"Matières sélectionnées : {selected_subjects}")
        print(f"Nombre de questions par matière : {num_questions_per_subject}")

        if not selected_subjects or num_questions_per_subject < 1:
            return render(request, 'time_challenge.html', {
                'error': "Aucune matière ou nombre de questions valide trouvé. Veuillez recommencer."
            })

        try:
            # Récupérer les matières sélectionnées depuis la base de données
            subjects = Subject.objects.filter(id__in=selected_subjects)
            print(f"Matières sélectionnées (codes) : {[subject.code for subject in subjects]}")
            questions = []

            # Charger les questions pour chaque matière
            for subject in subjects:
                print(f"Traitement de la matière : {subject.code}")

                if subject.code == "AD":  # Maladies digestives : exclure les questions dont l'ID commence par ADC
                    print("Matière détectée : Maladies digestives")
                    subject_questions = Question.objects.filter(
                        id__startswith=subject.code
                    ).exclude(id__startswith="ADC").order_by('?')[:num_questions_per_subject]

                elif subject.code == "CL":  # Cardiologie : exclure les questions dont l'ID commence par CLC
                    print("Matière détectée : Cardiologie")
                    subject_questions = Question.objects.filter(
                        id__startswith=subject.code
                    ).exclude(id__startswith="CLC").order_by('?')[:num_questions_per_subject]

                else:  # Matières standards
                    print(f"Matière standard détectée : {subject.code}")
                    subject_questions = Question.objects.filter(
                        id__startswith=subject.code
                    ).order_by('?')[:num_questions_per_subject]

                # Logs pour déboguer
                print(f"Questions trouvées pour {subject.code} avant exclusion : {Question.objects.filter(id__startswith=subject.code).count()}")
                print(f"Questions trouvées pour {subject.code} après exclusion : {subject_questions.count()}")

                if not subject_questions.exists():
                    print(f"Aucune question trouvée pour la matière {subject.code} avec les filtres.")
                    continue

                questions.extend(subject_questions)

            if not questions:
                return render(request, 'time_challenge.html', {
                    'error': "Aucune question trouvée pour les matières sélectionnées."
                })

            # Préparer les données des questions pour le frontend
            questions_data = []
            for question in questions:
                choices = question.choices.all()
                correct_choices = question.choices.filter(is_correct=True).values_list('id', flat=True)

                # Déterminer la source en utilisant la colonne `source` de l'examen
                source = question.exam.source if question.exam and question.exam.source else "Source inconnue"

                questions_data.append({
                    'id': question.id,
                    'text': question.text,
                    'choices': [{'id': choice.id, 'text': choice.text} for choice in choices],
                    'correct_choices': list(correct_choices),
                    'source': source,  # Utilisation de la source de l'examen
                })

            return render(request, 'time_challenge.html', {
                'questions': questions_data,
            })

        except Exception as e:
            return render(request, 'time_challenge.html', {
                'error': "Une erreur s'est produite lors de la génération des questions."
            })

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)


@login_required
def check_comment(request, question_id):
    user = request.user
    exists = Comment.objects.filter(question_id=question_id, user=user).exists()
    return JsonResponse({'exists': exists})



@csrf_exempt
def get_comments(request, question_id):
    """Retrieve comments for a specific question."""
    if request.method == 'GET':
        try:
            # Vérifiez d'abord dans le modèle `Question`
            question = Question.objects.filter(id=question_id).first()

            # Si non trouvé, vérifiez dans `UncorrectedQuestion`
            if not question:
                question = UncorrectedQuestion.objects.filter(id=question_id).first()

            # Si toujours non trouvé, lever une erreur 404
            if not question:
                return JsonResponse({'error': f'Question with ID {question_id} not found.'}, status=404)

            # Récupérer les commentaires associés
            comments = question.comments.all() if hasattr(question, 'comments') else []

            # Ajouter un champ `is_owner` pour chaque commentaire
            comments_data = [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'timestamp': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_owner': comment.user == request.user  # Vérifie si l'utilisateur connecté est le propriétaire
                }
                for comment in comments
            ]

            return JsonResponse({'comments': comments_data})

        except Exception as e:
            return JsonResponse({'error': 'Unable to fetch comments.'}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


from django.utils.timezone import localtime

@csrf_exempt
def add_comment(request):
    """Add a comment to a question."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_question_id = data.get('question_id')
            content = data.get('content')
            user = request.user  # Current user

            # Extraire uniquement le numéro après "question-"
            if raw_question_id.startswith('question-'):
                question_id = raw_question_id.split('-')[1]  # Récupère le numéro
            else:
                question_id = raw_question_id

            # Récupérer la question associée
            question = get_object_or_404(Question, id=question_id)

            # Vérifier si l'utilisateur a déjà commenté cette question
            if Comment.objects.filter(question=question, user=user).exists():
                return JsonResponse({'error': 'Vous avez déjà commenté cette question.'}, status=400)

            # Créer un nouveau commentaire
            comment = Comment.objects.create(
                question=question,
                user=user,
                content=content,
            )

            return JsonResponse({
                'message': 'Commentaire ajouté avec succès.',
                'comment': {
                    'id': comment.id,
                    'unique_id': comment.unique_id,
                    'user': user.username,
                    'content': comment.content,
                    'timestamp': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                },
            })
        except Exception as e:
            return JsonResponse({'error': 'Impossible d’ajouter le commentaire.'}, status=500)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)



@csrf_exempt
def delete_comment(request, comment_id):
    """Delete a specific comment."""
    if request.method == 'DELETE':
        try:
            comment = get_object_or_404(Comment, id=comment_id)

            # Check if the user owns the comment
            if comment.user != request.user:
                return JsonResponse({'error': 'Vous ne pouvez pas supprimer ce commentaire.'}, status=403)

            comment.delete()
            return JsonResponse({'message': 'Commentaire supprimé avec succès.'})
        except Exception as e:
            return JsonResponse({'error': 'Unable to delete comment.'}, status=500)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)

@csrf_exempt
def contact_page(request):
    if request.method == 'POST':
        try:

            # Récupération des données envoyées via AJAX (requête JSON)
            data = json.loads(request.body)

            message_content = data.get('message', '')
            mode = data.get('mode', 'anonymous')

            # Validation du message
            if not message_content.strip():
                return JsonResponse({'status': 'error', 'message': 'Le message est vide.'}, status=400)


            # Vérification des doublons : Un même message envoyé dans les 5 dernières secondes
            recent_duplicate = Message.objects.filter(
                content=message_content,
                username=request.user if request.user.is_authenticated else None,
                created_at__gte=now() - timedelta(seconds=5)
            ).exists()

            if recent_duplicate:
                return JsonResponse({'status': 'error', 'message': 'Message déjà envoyé récemment.'}, status=400)

            # Création et sauvegarde du message
            message = Message(content=message_content)
            if mode == 'username' and request.user.is_authenticated:
                message.is_anonymous = False
                message.username = request.user

            message.save()

            # Log pour confirmer l'enregistrement en base de données

            # Envoi de l'email à l'administrateur
            try:
                send_mail(
                    'Nouveau message soumis',
                    f'Contenu: {message_content}\nMode: {"Anonyme" if message.is_anonymous else request.user.username}',
                    'nasser.sentissi2@gmail.com',
                    ['nasser.sentissi2@gmail.com'],
                    fail_silently=False,
                )
            except Exception as email_error:
                logger.error(f"Erreur lors de l'envoi de l'email : {str(email_error)}")

            # Réponse JSON en cas de succès
            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Les données envoyées ne sont pas valides.'}, status=400)

        except Exception as e:
            # Log des erreurs en cas de problème
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # GET Request : Récupération du nom d'utilisateur si connecté
    username = request.user.username if request.user.is_authenticated else None
    return render(request, 'contact.html', {'username': username})

    
@csrf_exempt
def get_attempts(request):
    """
    Vue pour récupérer les statistiques des tentatives des questions envoyées.
    """
    if request.method == 'POST':  # On s'attend à une requête POST contenant les IDs des questions
        try:
            # Charger les données JSON envoyées par JavaScript
            data = json.loads(request.body)
            question_ids = data.get('question_ids', [])  # Récupérer les IDs des questions

            # Vérifier si des IDs ont été reçus
            if not question_ids:
                return JsonResponse({'error': 'Aucun ID de question reçu.'}, status=400)


            # Initialiser un dictionnaire pour stocker les statistiques
            stats = {}

            # Parcourir chaque question ID pour calculer les statistiques
            for question_id in question_ids:
                try:
                    # Récupérer la question correspondante
                    question = Question.objects.get(id=question_id)

                    # Récupérer les tentatives associées à l'utilisateur et à la question
                    attempts = QuestionAttempt.objects.filter(user=request.user, question=question)
                    total_attempts = attempts.count()
                    failures = attempts.filter(is_correct=False).count()
                    failure_rate = (failures / total_attempts) * 100 if total_attempts > 0 else 0

                    # Ajouter les statistiques dans le dictionnaire
                    stats[question_id] = {
                        'total_attempts': total_attempts,
                        'failures': failures,
                        'failure_rate': round(failure_rate, 2)
                    }


                except Question.DoesNotExist:
                    # Si une question n'existe pas, on log l'erreur mais on continue
                    stats[question_id] = {'error': 'Question non trouvée'}

            # Retourner les statistiques en JSON
            return JsonResponse(stats)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Erreur serveur.'}, status=500)

    # Si la méthode n'est pas POST, retourner une erreur
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)

@login_required
def your_sidebar_view(request):
    """
    Vue pour afficher les semestres et modules accessibles dans la barre latérale.
    """
    try:
        
        # Récupérer les semestres associés à l'utilisateur
        user_semesters = UserSemester.objects.filter(user=request.user)

        if not user_semesters:
            return render(request, 'pagedacceuil.html', {'data': {}})

        semesters_with_modules = {}
        for us in user_semesters:
            for semester in us.semesters.all():
                
                # Récupérer les modules associés à ce semestre
                modules = us.modules.filter(semesters=semester)
                
                # Ajouter les modules avec descriptions dans le dictionnaire
                semesters_with_modules[semester.name] = modules.values('description')



        # Renvoyer les données vers le template
        return render(request, 'pagedacceuil.html', {'data': semesters_with_modules})

    except Exception as e:
        return render(request, 'pagedacceuil.html', {'data': {}, 'error': str(e)})

@login_required
def submit_response(request):
    if request.method == "POST":
        # Extraction des données de la requête POST
        data = request.POST
        question_id = data.get("question_id")
        selected_choices = data.getlist("choices[]")

        # Debugging
        print(f"Réponse soumise : question_id={question_id}, selected_choices={selected_choices}")

        # Vérification des données reçues
        if not question_id or not selected_choices:
            print("Données invalides : question_id ou selected_choices manquants.")
            return JsonResponse({"error": "Données invalides"}, status=400)

        try:
            # Récupérer la question correspondante
            question = UncorrectedQuestion.objects.get(id=question_id)
            print(f"Question trouvée : {question.id}")
        except UncorrectedQuestion.DoesNotExist:
            print(f"Question introuvable : {question_id}")
            return JsonResponse({"error": "Question introuvable"}, status=404)

        # Supprimer les anciennes réponses de l'utilisateur pour cette question
        UserResponse.objects.filter(user=request.user, question=question).delete()
        print(f"Anciennes réponses supprimées pour l'utilisateur {request.user.username} sur la question {question_id}")

        # Ajouter les nouvelles réponses
        for choice_id in selected_choices:
            try:
                # Récupérer le choix correspondant
                choice = UncorrectedChoice.objects.get(id=choice_id, question=question)
                # Créer une nouvelle réponse
                UserResponse.objects.create(user=request.user, choice=choice, question=question)
                print(f"Nouvelle réponse ajoutée : {choice.text} (ID : {choice.id})")
            except UncorrectedChoice.DoesNotExist:
                print(f"Choix introuvable : {choice_id}")
                continue

        print("Toutes les réponses ont été enregistrées avec succès.")
        return JsonResponse({"message": "Réponses enregistrées avec succès."})

    # Si la requête n'est pas POST
    print("Requête invalide : méthode HTTP non supportée.")
    return JsonResponse({"error": "Requête invalide"}, status=400)


@csrf_exempt
def calculate_percentages(request, question_id):
    print(f"[DEBUG] Début du calcul des pourcentages pour la question : {question_id}")

    # Étape 1 : Récupérer la question
    question = get_object_or_404(UncorrectedQuestion, id=question_id)
    print(f"[DEBUG] Question trouvée : {question.id} - {question.text}")

    # Étape 2 : Récupérer les choix liés à la question
    choices = UncorrectedChoice.objects.filter(question=question)
    print(f"[DEBUG] Nombre de choix disponibles pour la question : {choices.count()}")
    for choice in choices:
        print(f"[DEBUG] Choix : {choice.id} - Texte : {choice.text}")

    # Étape 3 : Récupérer les dernières réponses soumises par utilisateur
    latest_responses = (
        UserResponse.objects.filter(question=question)
        .order_by('user', '-timestamp')  # Trier par utilisateur et timestamp (le plus récent en premier)
        .distinct('user')  # Conserver uniquement la dernière réponse par utilisateur
    )
    print(f"[DEBUG] Nombre total de réponses uniques récupérées : {latest_responses.count()}")
    for response in latest_responses:
        print(f"[DEBUG] Réponse : Utilisateur={response.user.username} - Choix={response.choice.id}")

    # Étape 4 : Calculer le total d'utilisateurs ayant répondu
    total_users = latest_responses.values('user').distinct().count()
    print(f"[DEBUG] Nombre total d'utilisateurs ayant répondu : {total_users}")

    # Étape 5 : Calcul des pourcentages
    percentages = {}
    if total_users == 0:
        print("[DEBUG] Aucune réponse trouvée. Les pourcentages sont initialisés à 0.")
        percentages = {choice.id: 0 for choice in choices}
    else:
        print("[DEBUG] Début du calcul des pourcentages pour chaque choix.")
        for choice in choices:
            # Compter combien de fois chaque choix a été sélectionné dans les dernières réponses
            choice_count = latest_responses.filter(choice=choice).count()
            percentage = round((choice_count / total_users) * 100, 2)
            percentages[choice.id] = percentage
            print(f"[DEBUG] Choix : {choice.id} - Nombre de réponses : {choice_count} - Pourcentage : {percentage}%")

    # Étape 6 : Retourner les pourcentages sous forme de JSON
    print(f"[DEBUG] Pourcentages calculés pour la question {question_id} : {percentages}")
    return JsonResponse({
        "question_id": question.id,
        "percentages": percentages
    })


@login_required
def revision(request):
    """
    Vue pour réviser les chapitres associés aux sujets accessibles.
    """
    try:
        # Récupérer les semestres attribués à l'utilisateur
        user_semesters = UserSemester.objects.filter(user=request.user)
        
        if not user_semesters:
            return render(request, 'revision.html', {
                'error': "Vous n'avez accès à aucun semestre.",
                'subjects': []
            })

        # Récupérer les modules accessibles via les semestres
        accessible_modules = Module.objects.filter(semester__in=[
            semester.id for user_semester in user_semesters for semester in user_semester.semesters.all()
        ])

        # Récupérer les sujets associés aux modules accessibles
        subjects = Subject.objects.filter(module__in=accessible_modules).distinct()

        # Récupérer les chapitres associés aux sujets accessibles
        subjects_with_chapters = []
        for subject in subjects:
            chapters = Chapter.objects.filter(subject=subject)
            subjects_with_chapters.append({
                'subject': subject,
                'chapters': chapters
            })

        # Passer les données au template
        return render(request, 'revision.html', {
            'subjects_with_chapters': subjects_with_chapters,  # Passer les sujets et chapitres au template
        })

    except Exception as e:
        return render(request, 'revision.html', {
            'error': "Une erreur est survenue lors de la récupération des chapitres.",
            'subjects_with_chapters': []
        })


def get_flashcards(request, chapter_id):
    try:
        chapter = Chapter.objects.get(id=chapter_id)
        flashcards = Flashcard.objects.filter(chapter=chapter).values('question', 'answer')
        return JsonResponse({'flashcards': list(flashcards)})
    except Chapter.DoesNotExist:
        return JsonResponse({'error': 'Chapitre introuvable'}, status=404)
    
@login_required
@csrf_exempt

def get_next_flashcard_id(user, chapter):
    try:
        # Vérifiez que user est bien un utilisateur
        print(f"Utilisateur reçu : {user}, type : {type(user)}")

        # Récupérer toutes les flashcards pour cet utilisateur et ce chapitre
        flashcards = Flashcard.objects.filter(user=user, chapter=chapter)
        print(f"Flashcards récupérées : {[f.id for f in flashcards]}")

        # Trouver le numéro maximum parmi les IDs existants
        max_num = 0
        for flashcard in flashcards:
            if '_' in flashcard.id:
                parts = flashcard.id.rsplit('_', 1)  # Sépare la dernière partie de l'ID
                if len(parts) == 2 and parts[1].isdigit():  # Vérifie si c'est un numéro
                    max_num = max(max_num, int(parts[1]))

        # Incrémenter le numéro maximum pour générer un nouvel ID
        new_id = f"{user.username}_{chapter.name}_{max_num + 1}"
        print(f"Nouvel ID généré : {new_id}")
        return new_id

    except Exception as e:
        print(f"Erreur dans get_next_flashcard_id : {str(e)}")
        raise

@login_required
@csrf_exempt
def manage_flashcards(request, chapter_id):
    """
    Gérer les flashcards pour un utilisateur : CRUD (Create, Read, Update).
    """
    try:
        print(f"Requête reçue : {request.method} pour le chapitre ID {chapter_id}")

        # Récupérer le chapitre
        chapter = get_object_or_404(Chapter, id=chapter_id)
        print(f"Chapitre récupéré : {chapter.name}")

        # Vérifier l'utilisateur connecté
        print(f"Utilisateur actuel : {request.user}, type : {type(request.user)}")
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Utilisateur non authentifié.'}, status=401)

        if request.method == "GET":
            # Récupérer les flashcards globales et celles de l'utilisateur
            flashcards = Flashcard.objects.filter(
                chapter=chapter
            ).filter(
                models.Q(is_global=True) | models.Q(user=request.user)
            ).order_by('id')
            print(f"Flashcards récupérées : {flashcards}")

            flashcards_data = [
                {
                    'id': flashcard.id,
                    'question': flashcard.question,
                    'answer': flashcard.answer,
                    'is_global': flashcard.is_global
                }
                for flashcard in flashcards
            ]
            return JsonResponse({'flashcards': flashcards_data}, status=200)

        elif request.method == "POST":
            # Ajouter une nouvelle flashcard
            data = json.loads(request.body)
            print("Données reçues :", data)

            question = data.get('question', '').strip()
            answer = data.get('answer', '').strip()
            username = data.get('user', '').strip()  # Récupérer le nom d'utilisateur
            print(f"Utilisateur transmis dans les données : {username}")

            if not question or not answer or not username:
                print("Erreur : Données incomplètes.")
                return JsonResponse({'error': 'La question, la réponse, et l’utilisateur sont obligatoires.'}, status=400)

            # Récupérer l'objet utilisateur
            user = User.objects.filter(username=username).first()
            print(f"Utilisateur trouvé : {user}, type : {type(user)}")
            if not user:
                print(f"Erreur : Utilisateur '{username}' introuvable.")
                return JsonResponse({'error': f"Utilisateur '{username}' introuvable."}, status=404)

            # Générer un nouvel ID unique
            new_id = f"{user.username}_{chapter.name}_{Flashcard.objects.filter(user=user, chapter=chapter).count() + 1}"
            print(f"Nouvel ID généré : {new_id}")

            # Créer une flashcard pour l'utilisateur
            flashcard = Flashcard(
                id=new_id,
                question=question,
                answer=answer,
                chapter=chapter,
                user=user  # Assigner l'objet utilisateur ici
            )
            flashcard.save()
            print(f"Flashcard créée : {flashcard}")

            return JsonResponse({
                'message': 'Flashcard ajoutée avec succès.',
                'flashcard': {
                    'id': flashcard.id,
                    'question': flashcard.question,
                    'answer': flashcard.answer,
                }
            }, status=201)

        elif request.method == "PUT":
            data = json.loads(request.body)
            print(f"Données reçues pour PUT : {data}")

            flashcard_id = data.get('id')
            if not flashcard_id:
                print("Erreur : Un ID valide est requis.")
                return JsonResponse({'error': 'Un ID valide est requis.'}, status=400)

            flashcard = get_object_or_404(Flashcard, id=flashcard_id, user=request.user)
            print(f"Flashcard trouvée pour modification : {flashcard}")

            flashcard.question = data.get('question', flashcard.question).strip()
            flashcard.answer = data.get('answer', flashcard.answer).strip()
            flashcard.save()
            print(f"Flashcard modifiée : {flashcard}")

            return JsonResponse({
                'message': 'Flashcard modifiée avec succès.',
                'flashcard': {
                    'id': flashcard.id,
                    'question': flashcard.question,
                    'answer': flashcard.answer,
                }
            }, status=200)

        else:
            print("Erreur : Méthode non autorisée.")
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)

    except Exception as e:
        print(f"Erreur inattendue : {str(e)}")
        return JsonResponse({'error': f'Une erreur est survenue : {str(e)}'}, status=500)

