from cryptography.fernet import Fernet

# Générer une clé Fernet
key = Fernet.generate_key()
print(f"Votre clé Fernet : {key.decode()}")  # Affiche la clé à copier
