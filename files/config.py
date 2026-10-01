import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
BASE_PATH = os.path.join(BASE_DIR, "data")
print(BASE_PATH)
NAVIRE_PATH = os.path.join(BASE_PATH, "Navire")
RENCONTRE_PATH = os.path.join(BASE_PATH, "Rencontre")
MARCHANDISE_PATH = os.path.join(BASE_PATH, "Marchandise")
EQUIPAGE_PATH = os.path.join(BASE_PATH, "Equipage")
VOYAGE_PATH = os.path.join(BASE_PATH, "Voyage")
PNJ_PATH = os.path.join(BASE_PATH, "PNJ")

def chemin_fichier(dossier, nom_fichier):
    """Retourne le chemin complet d’un fichier dans un sous-dossier data."""
    return os.path.join(BASE_PATH, dossier, nom_fichier)