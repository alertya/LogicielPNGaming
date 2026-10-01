"""
donnees_reference.py
---------------------
Listes de référence et tables de correspondance extraites du fichier
Excel fourni (feuille "DataBaseDeDonnes"). Utilisées pour remplir les
listes déroulantes du formulaire "Générer" (onglet Journal de bord).

Modifie librement ces listes si tes règles évoluent — le reste du code
(panneau_generation.py, moteur_interface.py) s'appuie uniquement sur ces
constantes, jamais sur des valeurs codées en dur ailleurs.
"""

import random

# ---------------------------------------------------------------------------
# Zones maritimes (colonne "Zone" / "ZoneMaritime")
# Chaque zone est associée à un "dé marchand" et un "dé aventurier" qui
# servent de base aux tirages de rencontre (voir moteur_interface.py).
# Une valeur peut être un entier (dénominateur de probabilité fixe) ou une
# notation de dé sous forme de chaîne, ex: "D20" -> à résoudre avec roll_de().
# ---------------------------------------------------------------------------
ZONE_DES = {
    "Mer ou océan": (140, 1000),
    "Au large d'une côte": (84, 100),
    "Sur une route commerciale": (14, 20),
    "Près des côtes": (20, 40),
    "À un mouillage forain": (84, 20),
    "À un comptoir": ("D3", 100),
    "Au port (petit)": (3, 100),
    "Au port (moyen)": ("D5", 100),
    "Au port (grand)": ("D20", 100),
    "Au port (très grand)": ("D100", 100),
}

ZONES_MARITIMES = list(ZONE_DES.keys())

# ---------------------------------------------------------------------------
# Tailles de port d'escale (sous-ensemble de la liste des zones, plus une
# option "pas d'escale" pour une étape en pleine mer)
# ---------------------------------------------------------------------------
TAILLES_PORT = [
    "Aucune (pas d'escale)",
    "Au port (petit)",
    "Au port (moyen)",
    "Au port (grand)",
    "Au port (très grand)",
]

# ---------------------------------------------------------------------------
# Régions (colonne "Region") — utilisées pour choisir la destination de
# chaque étape du trajet.
# ---------------------------------------------------------------------------
REGIONS = [
    "Acadie, baie d'Hudson et terre-neuve",
    "Afrique du Sud-Ouest (Congo au cap de Bonne-Espérance)",
    "Afrique orientale (Mozambique à Kenya)",
    "Amérique du Sud (Côte Atlantique de la Guyane à l'Argentine)",
    "Arabie",
    "Argentine",
    "Bengale",
    "Brésil",
    "Cap Comorin et Ceylan",
    "Chili",
    "Chine, Mer de Chine, Corée et Japon",
    "Côte de Coromandel",
    "Côte de Malabar",
    "Côte est d'Amérique du Nord",
    "Du Guatemala au Panama",
    "Egypte",
    "Europe du nord",
    "Europe du sud",
    "Europe méditerranéenne",
    "Golfe de Guinée",
    "Grandes Antilles",
    "Guatemala, Costa Rica, Panama",
    "Indonésie et Philippines",
    "Madagascar",
    "Maghreb",
    "Méditerranée orientale",
    "Mer Rouge et Éthiopie",
    "Mexique",
    "Nord-ouest de l'Afrique",
    "Nouvelle-Espagne",
    "Nouvelle-Grenade",
    "Nouvelle-Grenade et Venezuela",
    "Océan indien (Île de France, Bourbon)",
    "Océan indien (les Mascareignes)",
    "Pérou",
    "Perse",
    "Petites Antilles",
    "Siam et Tonkin",
    "Surate et péninsule de Gujarat",
]


def roll_de(valeur) -> int:
    """
    Résout une valeur de dé de façon souple :
      - un nombre est renvoyé tel quel (int)
      - une chaîne "D<n>" (ex: "D20") est tirée aléatoirement entre 1 et n
      - toute autre valeur renvoie 0

    Utile si tu veux exploiter DeMarchand/DeAventurier dans tes propres
    règles de rencontre (voir moteur_interface.py pour un exemple simple
    basé sur DeAventurier).
    """
    if isinstance(valeur, (int, float)):
        return int(valeur)
    if isinstance(valeur, str) and valeur.upper().startswith("D"):
        try:
            faces = int(valeur[1:])
            return random.randint(1, faces)
        except ValueError:
            return 0
    return 0
