import os
import sys
import time
import html
import subprocess
from pathlib import Path
from email import policy
from email.parser import BytesParser

import extract_msg
from weasyprint import HTML


# ============================================================
# CONFIGURATION
# ============================================================

DOSSIER = Path(r"C:\Users\aleti\OneDrive\Documents\AvocatBis")

# Sous-dossier dans lequel seront placés les PDF convertis
DOSSIER_PDF = DOSSIER / "PDF_convertis"

# Temps d'attente entre deux impressions
DELAI_IMPRESSION = 3

# Extensions traitées
EXTENSIONS = {".pdf", ".eml", ".msg",".png",".jpeg"}


# ============================================================
# OUTILS
# ============================================================

def nettoyer_nom(nom):
    """Supprime les caractères interdits dans un nom de fichier Windows."""
    caracteres_interdits = '<>:"/\\|?*'

    for caractere in caracteres_interdits:
        nom = nom.replace(caractere, "_")

    return nom.strip()


def html_document(titre, contenu):
    """Construit un document HTML imprimable."""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">

<style>
    @page {{
        size: A4;
        margin: 20mm;
    }}

    body {{
        font-family: Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #000;
    }}

    h1 {{
        font-size: 16pt;
        border-bottom: 1px solid #000;
        padding-bottom: 8px;
    }}

    .metadata {{
        margin-bottom: 20px;
        padding: 10px;
        background: #f2f2f2;
    }}

    .metadata strong {{
        display: inline-block;
        min-width: 80px;
    }}

    .message {{
        white-space: pre-wrap;
        word-wrap: break-word;
    }}

    img {{
        max-width: 100%;
    }}

    a {{
        color: #000;
        text-decoration: underline;
    }}
</style>

<title>{html.escape(titre)}</title>
</head>

<body>

<h1>{html.escape(titre)}</h1>

{contenu}

</body>
</html>
"""


# ============================================================
# CONVERSION EML
# ============================================================

def convertir_eml(fichier, pdf_destination):

    with open(fichier, "rb") as f:
        message = BytesParser(policy=policy.default).parse(f)

    sujet = message.get("subject", "")
    expediteur = message.get("from", "")
    destinataire = message.get("to", "")
    date = message.get("date", "")

    # Recherche du contenu HTML
    corps_html = None
    corps_texte = None

    if message.is_multipart():

        for partie in message.walk():

            if partie.get_content_disposition() == "attachment":
                continue

            type_contenu = partie.get_content_type()

            if type_contenu == "text/html" and corps_html is None:
                try:
                    corps_html = partie.get_content()
                except Exception:
                    pass

            elif type_contenu == "text/plain" and corps_texte is None:
                try:
                    corps_texte = partie.get_content()
                except Exception:
                    pass

    else:

        if message.get_content_type() == "text/html":
            corps_html = message.get_content()
        else:
            corps_texte = message.get_content()

    if corps_html:
        contenu = corps_html
    elif corps_texte:
        contenu = f"""
        <div class="message">
        {html.escape(corps_texte)}
        </div>
        """
    else:
        contenu = "<p>[Corps du message vide]</p>"

    metadata = f"""
    <div class="metadata">
        <div><strong>De :</strong> {html.escape(str(expediteur))}</div>
        <div><strong>À :</strong> {html.escape(str(destinataire))}</div>
        <div><strong>Date :</strong> {html.escape(str(date))}</div>
        <div><strong>Objet :</strong> {html.escape(str(sujet))}</div>
    </div>
    """

    document = html_document(
        sujet or fichier.stem,
        metadata + contenu
    )

    HTML(string=document).write_pdf(pdf_destination)


# ============================================================
# CONVERSION MSG
# ============================================================

def convertir_msg(fichier, pdf_destination):

    message = extract_msg.Message(str(fichier))

    sujet = message.subject or ""
    expediteur = message.sender or ""
    destinataire = message.to or ""
    date = message.date or ""

    # Le package extract-msg peut fournir le corps HTML
    corps_html = None

    try:
        corps_html = message.htmlBody
    except Exception:
        corps_html = None

    if corps_html:

        if isinstance(corps_html, bytes):
            corps_html = corps_html.decode(
                "utf-8",
                errors="replace"
            )

        contenu = corps_html

    else:

        corps_texte = message.body or ""

        contenu = f"""
        <div class="message">
        {html.escape(corps_texte)}
        </div>
        """

    metadata = f"""
    <div class="metadata">
        <div><strong>De :</strong> {html.escape(str(expediteur))}</div>
        <div><strong>À :</strong> {html.escape(str(destinataire))}</div>
        <div><strong>Date :</strong> {html.escape(str(date))}</div>
        <div><strong>Objet :</strong> {html.escape(str(sujet))}</div>
    </div>
    """

    document = html_document(
        sujet or fichier.stem,
        metadata + contenu
    )

    HTML(string=document).write_pdf(pdf_destination)

    try:
        message.close()
    except Exception:
        pass


# ============================================================
# CONVERSION
# ============================================================

def convertir_fichier(fichier):

    extension = fichier.suffix.lower()

    nom_pdf = nettoyer_nom(fichier.stem) + ".pdf"
    destination = DOSSIER_PDF / nom_pdf

    # Évite d'écraser un PDF existant
    compteur = 1

    while destination.exists():

        destination = (
            DOSSIER_PDF
            / f"{nettoyer_nom(fichier.stem)}_{compteur}.pdf"
        )

        compteur += 1

    print(f"Conversion : {fichier.name}")

    if extension == ".eml":

        convertir_eml(
            fichier,
            destination
        )

    elif extension == ".msg":

        convertir_msg(
            fichier,
            destination
        )

    return destination


# ============================================================
# IMPRESSION
# ============================================================

def imprimer_pdf(fichier):

    print(f"Impression : {fichier.name}")

    try:

        # Imprimante par défaut de Windows
        os.startfile(
            str(fichier),
            "print"
        )

        time.sleep(DELAI_IMPRESSION)

        return True

    except Exception as e:

        print(
            f"ERREUR impression {fichier.name} : {e}"
        )

        return False


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print("TRAITEMENT DES PIECES")
    print("=" * 60)

    if not DOSSIER.exists():

        print(
            f"\nERREUR : dossier introuvable :\n{DOSSIER}"
        )

        input("\nAppuyez sur Entrée pour quitter...")
        return

    # Création du dossier PDF
    DOSSIER_PDF.mkdir(
        exist_ok=True
    )

    journal = DOSSIER / "journal_impression.txt"

    lignes_journal = []

    # --------------------------------------------------------
    # Recherche des fichiers
    # --------------------------------------------------------

    fichiers = []

    for fichier in DOSSIER.iterdir():

        if not fichier.is_file():
            continue

        if fichier.name == journal.name:
            continue

        if fichier.suffix.lower() in EXTENSIONS:

            fichiers.append(fichier)

    fichiers.sort(
        key=lambda x: x.name.lower()
    )

    print(
        f"\n{len(fichiers)} fichier(s) trouvé(s).\n"
    )

    pdf_a_imprimer = []

    # --------------------------------------------------------
    # Conversion
    # --------------------------------------------------------

    for fichier in fichiers:

        extension = fichier.suffix.lower()

        try:

            if extension == ".pdf":

                # PDF original
                pdf_a_imprimer.append(
                    fichier
                )

                lignes_journal.append(
                    f"[PDF ORIGINAL] {fichier.name}"
                )

            else:

                pdf = convertir_fichier(
                    fichier
                )

                pdf_a_imprimer.append(
                    pdf
                )

                lignes_journal.append(
                    f"[CONVERTI] {fichier.name} -> {pdf.name}"
                )

        except Exception as e:

            message = (
                f"[ERREUR CONVERSION] "
                f"{fichier.name} : {e}"
            )

            print(message)
            lignes_journal.append(message)

    # --------------------------------------------------------
    # Tri des PDF
    # --------------------------------------------------------

    pdf_a_imprimer.sort(
        key=lambda x: x.name.lower()
    )

    print(
        f"\n{len(pdf_a_imprimer)} PDF prêt(s) "
        f"pour impression.\n"
    )

    # --------------------------------------------------------
    # Impression
    # --------------------------------------------------------

    for pdf in pdf_a_imprimer:

        succes = imprimer_pdf(pdf)

        if succes:

            lignes_journal.append(
                f"[IMPRIME] {pdf.name}"
            )

        else:

            lignes_journal.append(
                f"[ECHEC IMPRESSION] {pdf.name}"
            )

    # --------------------------------------------------------
    # Journal
    # --------------------------------------------------------

    with open(
        journal,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "JOURNAL D'IMPRESSION\n"
        )

        f.write(
            "=" * 60 + "\n\n"
        )

        for ligne in lignes_journal:

            f.write(
                ligne + "\n"
            )

    print("\n" + "=" * 60)
    print("TRAITEMENT TERMINÉ")
    print("=" * 60)

    print(
        f"\nJournal : {journal}"
    )

    print(
        f"PDF convertis : {DOSSIER_PDF}"
    )

    input(
        "\nAppuyez sur Entrée pour fermer..."
    )


if __name__ == "__main__":
    main()