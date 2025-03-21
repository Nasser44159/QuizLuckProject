from django.contrib.auth.models import User
from quizapp.models import Profile

class FMPCRouter:
    """
    Routeur Django qui sépare les bases `default` et `FMPC` :
    - Toutes les tables sont présentes dans `default` et `FMPC`.
    - `User` et `Profile` existent **uniquement dans `default`**.
    - Les relations entre les bases sont bloquées pour éviter les erreurs SQL.
    """

    def db_for_read(self, model, **hints):
        """Détermine la base pour les lectures."""
        if model._meta.app_label == 'quizapp':  
            return 'FMPC'  # Lecture des données `quizapp` depuis FMPC
        if model == User or model == Profile:
            return 'default'  # `User` et `Profile` restent uniquement dans `default`
        return 'default'  # Tout le reste va dans `default`

    def db_for_write(self, model, **hints):
        """Détermine la base pour les écritures."""
        if model._meta.app_label == 'quizapp':  
            return 'FMPC'  # Écriture des données `quizapp` dans FMPC
        if model == User or model == Profile:
            return 'default'  # `User` et `Profile` restent dans `default`
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Autorise les relations uniquement entre objets de la même base."""
        if obj1._state.db == obj2._state.db:
            return True  # Relation autorisée si les objets sont dans la même base
        return False  # Bloquer les relations entre `default` et `FMPC` (évite les erreurs SQL)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Assure que les migrations vont dans la bonne base."""
        if app_label == 'quizapp':
            return db == 'FMPC'  # `quizapp` est migré uniquement dans FMPC
        if app_label == 'auth':
            return db == 'default'  # `User` et `Profile` restent dans `default`
        return db == 'default'
