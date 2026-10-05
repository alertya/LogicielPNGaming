
import re
from pathlib import Path
from collections import Counter, defaultdict

import fitz  # PyMuPDF

from openpyxl import Workbook
from openpyxl.styles import Font


# ============================================================
# CONFIGURATION
# ============================================================

# Dossier contenant les PDF
DOSSIER_ENTREE = 'C:\Users\aleti\OneDrive\Documents\AnonymisationDocument\documents'

print(DOSSIER_ENTREE)

# Fichier Excel de sortie
FICHIER_SORTIE = Path("noms_propres.xlsx")


# ============================================================
# EXTRACTION DU TEXTE PDF
# ============================================================

def extraire_texte_document(pdf_path):
    """
    Extrait le texte de toutes les pages d'un fichier PDF.
    """

    textes = []

    document = fitz.open(pdf_path)

    for page in document:
        texte = page.get_text()

        if texte.strip():
            textes.append(texte)

    document.close()

    return "\n".join(textes)


# ============================================================
# DETECTION DES NOMS PROPRES
# ============================================================

def trouver_noms_propres(texte):
    """
    Recherche les mots commençant par une majuscule,
    mais uniquement lorsqu'ils ne sont pas situés au début
    d'une phrase ou d'un paragraphe.

    Exemple :

        "Le bâtiment de Paris est concerné."

    -> Paris sera détecté.

        "Paris est une ville."

    -> Paris ne sera PAS détecté car il est en début de phrase.
    """

    resultats = []

    # On découpe le texte en mots tout en conservant
    # la position de chaque mot.
    pattern_mots = r"\b[\wÀ-ÖØ-öø-ÿ'-]+\b"

    mots = list(
        re.finditer(
            pattern_mots,
            texte,
            flags=re.UNICODE
        )
    )

    for match in mots:

        mot = match.group()

        # ----------------------------------------------------
        # Le mot doit commencer par une majuscule
        # ----------------------------------------------------

        if not mot[0].isupper():
            continue

        # On ignore les mots d'une seule lettre
        if len(mot) < 2:
            continue

        # ----------------------------------------------------
        # Recherche de ce qui précède le mot
        # ----------------------------------------------------

        debut_mot = match.start()

        texte_avant = texte[:debut_mot]

        # On supprime les espaces immédiatement avant le mot
        texte_avant = texte_avant.rstrip()

        # ----------------------------------------------------
        # Déterminer si le mot est en début de phrase
        # ----------------------------------------------------

        debut_phrase = False

        if not texte_avant:
            debut_phrase = True

        else:
            dernier_caractere = texte_avant[-1]

            # Début après un retour à la ligne
            if dernier_caractere == "\n":
                debut_phrase = True

            # Ponctuation indiquant généralement un début
            # de phrase
            elif dernier_caractere in ".?!":
                debut_phrase = True

        if debut_phrase:
            continue

        # ----------------------------------------------------
        # Nettoyage du mot
        # ----------------------------------------------------

        mot = mot.strip("'-")

        if mot:
            resultats.append(mot)

    return resultats


# ============================================================
# TRAITEMENT DES DOCUMENTS
# ============================================================

def analyser_documents(dossier):
    """
    Analyse tous les fichiers PDF du dossier.
    """

    compteur = Counter()

    fichiers_par_nom = defaultdict(set)

    fichiers = list(dossier.glob("*.pdf"))

    if not fichiers:
        print("Aucun fichier .pdf trouvé dans :", dossier)
        return compteur, fichiers_par_nom

    print(f"{len(fichiers)} document(s) trouvé(s).\n")

    for fichier in fichiers:

        print(f"Analyse : {fichier.name}")

        try:

            texte = extraire_texte_document(fichier)

            noms = trouver_noms_propres(texte)

            compteur.update(noms)

            for nom in set(noms):
                fichiers_par_nom[nom].add(fichier.name)

            print(
                f"  -> {len(noms)} occurrence(s) détectée(s)"
            )

        except Exception as e:

            print(f"  ERREUR : {e}")

    return compteur, fichiers_par_nom


# ============================================================
# CREATION DU FICHIER EXCEL
# ============================================================

def creer_excel(compteur, fichiers_par_nom, fichier_sortie):
    """
    Crée un fichier Excel avec :
        - Nom propre
        - Nombre d'occurrences
        - Fichiers dans lesquels il apparaît
    """

    wb = Workbook()

    ws = wb.active
    ws.title = "Noms propres"

    # En-têtes
```
