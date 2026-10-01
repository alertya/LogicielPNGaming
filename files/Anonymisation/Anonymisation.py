import re
from pathlib import Path
from collections import Counter, defaultdict

from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Font


# ============================================================
# CONFIGURATION
# ============================================================

# Dossier contenant les contrats Word
DOSSIER_ENTREE = Path("documents")
print(DOSSIER_ENTREE)
# Fichier Excel de sortie
FICHIER_SORTIE = Path("noms_propres.xlsx")


# ============================================================
# EXTRACTION DU TEXTE WORD
# ============================================================

def extraire_texte_document(docx_path):
    """
    Extrait le texte des paragraphes et des tableaux d'un fichier DOCX.
    """

    document = Document(docx_path)

    textes = []

    # Paragraphes
    for paragraphe in document.paragraphs:
        if paragraphe.text.strip():
            textes.append(paragraphe.text)

    # Tableaux
    for tableau in document.tables:
        for ligne in tableau.rows:
            for cellule in ligne.cells:
                if cellule.text.strip():
                    textes.append(cellule.text)

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

    mots = list(re.finditer(pattern_mots, texte, flags=re.UNICODE))

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
    Analyse tous les fichiers DOCX du dossier.
    """

    compteur = Counter()

    fichiers_par_nom = defaultdict(set)

    fichiers = list(dossier.glob("*.docx"))

    if not fichiers:
        print("Aucun fichier .docx trouvé dans :", dossier)
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

            print(f"  -> {len(noms)} occurrence(s) détectée(s)")

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
    ws["A1"] = "Nom propre"
    ws["B1"] = "Occurrences"
    ws["C1"] = "Fichiers concernés"

    # Mise en forme des en-têtes
    for cellule in ws[1]:
        cellule.font = Font(bold=True)

    # Tri par nombre d'occurrences décroissant
    noms_tries = sorted(
        compteur.items(),
        key=lambda x: (-x[1], x[0].lower())
    )

    ligne = 2

    for nom, occurrences in noms_tries:

        ws.cell(ligne, 1, nom)
        ws.cell(ligne, 2, occurrences)

        fichiers = sorted(fichiers_par_nom[nom])

        ws.cell(
            ligne,
            3,
            "; ".join(fichiers)
        )

        ligne += 1

    # Largeur des colonnes
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 60

    # Filtre automatique
    ws.auto_filter.ref = f"A1:C{ligne - 1}"

    # Figer la première ligne
    ws.freeze_panes = "A2"

    wb.save(fichier_sortie)

    print("\n======================================")
    print("Analyse terminée")
    print("======================================")
    print(f"Noms uniques : {len(compteur)}")
    print(f"Excel créé : {fichier_sortie.absolute()}")


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    # Vérification du dossier
    if not DOSSIER_ENTREE.exists():
        DOSSIER_ENTREE.mkdir(parents=True)

        print()
        print("Le dossier 'documents' vient d'être créé.")
        print("Place tes fichiers Word .docx dedans,")
        print("puis relance le programme.")
        print()

    else:

        compteur, fichiers_par_nom = analyser_documents(
            DOSSIER_ENTREE
        )

        creer_excel(
            compteur,
            fichiers_par_nom,
            FICHIER_SORTIE
        )