from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views 
from .views import get_user_semesters, get_exam_chart_data
from django.contrib.auth.views import LoginView, LogoutView
from .views import contact_page, manage_flashcards
from .views import get_attempts
from .views import my_login_view  # 🔥 Assure-toi d'importer ta vue
from django.contrib import admin



if settings.DEBUG:
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



urlpatterns = [

    path('admin/', admin.site.urls),  # Admin principal de Django

    path('update-account/', views.update_account, name='update_account'),

    path('api/manage_flashcards/<int:chapter_id>/', manage_flashcards, name='manage_flashcards'),


    path('submit_response/', views.submit_response, name='submit_response'),

    path('calculate_percentages/<str:question_id>/', views.calculate_percentages, name='calculate_percentages'),
    # Administration et gestion des examens
    path('admin/quizapp/questions_for_exam/<int:exam_id>/', views.questions_for_exam, name='questions_for_exam'),
    path('api/get_attempts/', views.get_attempts, name='get_attempts'),

    # Résultats
    path('resultats/', views.resultats, name='resultats'),
    path('revision/', views.revision, name='revision'),
    path('api/flashcards/<int:chapter_id>/', views.get_flashcards, name='get_flashcards'),


    # Quiz et soumission
    path('soumettre-quiz/', views.soumettre_quiz, name='soumettre_quiz'),
    path('api/modules/<str:semester_name>/<str:module_name>/details/', views.module_details, name='module_details'),
    path('api/exams/<str:source>/chart/', views.get_exam_chart_data, name='exam_chart_data'),
    path('api/semester/<str:semester_name>/average/', views.get_semester_average_data, name='semester_average_data'),


    # Inscription et connexion
    path("register/", views.register, name="register"),  # URL pour l'inscription
    path('login/', my_login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Page d'accueil
    path('', views.home, name='home'),
    path('contact_page/', contact_page, name='contact_page'),
    path('track_attempts/', views.track_attempts, name='track_attempts'),

    # API et données dynamiques
    path('api/get_user_semesters/', get_user_semesters, name='get_user_semesters'),
    path('api/get_accessible_modules/', views.get_accessible_modules, name='get_accessible_modules'),



    # Challenges
    path('start_challenge/', views.start_challenge, name='start_challenge'),
    path('challenge/', views.challenge, name='challenge'),
    path('time_challenge/', views.time_challenge, name='time_challenge'),  # Mode Rapidité

    # Gestion des commentaires
    path('get_comments/<str:question_id>/', views.get_comments, name='get_comments'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    # Gestion des modules, favoris et fichiers dynamiques
    path('<str:semester>/<str:favorite_name>/', views.render_favorite, name='render_favorite'),
    path('<str:semester>/', views.dynamic_view, name='dynamic_view'),
    path('<str:semester>/<str:module>/', views.dynamic_view, name='dynamic_view'),
    path('<str:semester>/<str:module>/<str:file_name>/', views.dynamic_view, name='dynamic_view'),




]




