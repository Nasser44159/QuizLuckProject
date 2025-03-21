import os
import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuizLuck.settings')
django.setup()

import pandas as pd
from django.db import connection

# Requête pour récupérer les questions et leurs choix pour Bioph2023
query = """
SELECT 
    q.id AS question_id, 
    q.text AS question_text, 
    c.text AS choice_text, 
    c.is_correct AS is_correct,
    qc.title AS qcm_title
FROM quizapp_question q
JOIN quizapp_choice c ON q.id = c.question_id
JOIN quizapp_qcm qc ON q.qcm_id = qc.id
WHERE qc.title = 'Bioph2023'
"""

# Exécution de la requête
with connection.cursor() as cursor:
    cursor.execute(query)
    rows = cursor.fetchall()

# Convertir en DataFrame pour visualisation
columns = ['Question ID', 'Question Text', 'Choice Text', 'Is Correct', 'QCM Title']
bioph2023_df = pd.DataFrame(rows, columns=columns)

# Désactiver la troncature
pd.set_option('display.max_rows', None)  # Affiche toutes les lignes
pd.set_option('display.max_colwidth', None)  # Affiche tout le contenu des colonnes

# Afficher les données
print(bioph2023_df)

bioph2023_df.to_csv("bioph2023_questions.csv", index=False, encoding="utf-8")
print("Données exportées dans bioph2023_questions.csv")
