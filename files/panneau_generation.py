"""
panneau_generation.py
----------------------
Panneau spécifique à l'onglet "Journal de bord" -> "Générer".

Contrairement aux autres onglets (qui utilisent le rendu générique de
app.py : liste déroulante d'instance + tableau/fiche + boutons d'action),
celui-ci a besoin d'un vrai formulaire à nombre variable de champs (une
"étape" par région traversée, ajoutable/supprimable dynamiquement). Il est
donc construit à part, mais reste entièrement piloté par les listes de
`donnees_reference.py` : aucune valeur de jeu n'est codée en dur ici.

Ce panneau ne connaît rien du moteur : il collecte simplement les valeurs
saisies et les transmet via le callback `on_creer(navire, annee, etapes)`
fourni par app.py, qui se charge d'appeler `moteur.creer_trajet(...)`.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional

import theme
import donnees_reference as ref


def _vers_nombre(texte: str):
    """Convertit une saisie utilisateur en int (ou float si un point est présent)."""
    texte = (texte or "").strip().replace(",", ".")
    try:
        if "." in texte:
            return float(texte)
        return int(texte)
    except ValueError:
        return 0


class LigneEtape(tk.Frame):
    """Un mini-formulaire représentant une étape (une région) du trajet."""

    def __init__(self, parent, numero: int, on_supprimer: Callable[["LigneEtape"], None]):
        super().__init__(
            parent, bg=theme.BG_PANEL, padx=16, pady=12,
            highlightbackground=theme.BORDER, highlightthickness=1,
        )
        self.on_supprimer = on_supprimer

        # --- en-tête (numéro d'étape + bouton retirer) ----------------------
        entete = tk.Frame(self, bg=theme.BG_PANEL)
        entete.pack(fill="x")
        self.label_titre = tk.Label(
            entete, text=f"Étape {numero}", bg=theme.BG_PANEL,
            fg=theme.FG_TITLE, font=theme.FONT_SECTION,
        )
        self.label_titre.pack(side="left")
        tk.Button(
            entete, text="✕ Retirer cette étape", font=theme.FONT_TEXT,
            bg=theme.BG_PANEL, fg=theme.ERROR, relief="flat", cursor="hand2",
            command=lambda: self.on_supprimer(self),
        ).pack(side="right")

        # --- variables --------------------------------------------------------
        self.var_region = tk.StringVar(value=ref.REGIONS[0])
        self.var_zone = tk.StringVar(value=ref.ZONES_MARITIMES[0])
        self.var_taille_port = tk.StringVar(value=ref.TAILLES_PORT[0])
        self.var_distance = tk.StringVar(value="0")
        self.var_chance_aventurier = tk.StringVar(value="0")
        self.var_chance_marchand = tk.StringVar(value="0")
        self.var_vigie = tk.StringVar(value="0")
        self.var_recrutement = tk.StringVar(value="0")
        self.var_commerce = tk.StringVar(value="0")
        self.var_reparation = tk.StringVar(value="0")
        self.var_des_texte = tk.StringVar(value="")

        grille = tk.Frame(self, bg=theme.BG_PANEL)
        grille.pack(fill="x", pady=(10, 0))

        self._champ_combo(grille, 0, 0, "Région", self.var_region, ref.REGIONS, width=38)
        self._champ_combo(
            grille, 0, 1, "Zone maritime", self.var_zone, ref.ZONES_MARITIMES,
            width=22, on_select=self._maj_des,
        )
        self._champ_combo(grille, 0, 2, "Taille du port d'escale", self.var_taille_port, ref.TAILLES_PORT, width=22)

        self._champ_nombre(grille, 1, 0, "Distance (milles nautiques)", self.var_distance, jusqu_a=20000)
        self._champ_nombre(grille, 1, 1, "Chance de rencontre (aventurier)", self.var_chance_aventurier, jusqu_a=1000)
        self._champ_nombre(grille, 1, 1, "Chance de rencontre (marchand)", self.var_chance_marchand, jusqu_a=1000)
        self._champ_nombre(grille, 1, 2, "Compétence de vigie", self.var_vigie, jusqu_a=20)

        self._champ_nombre(grille, 2, 0, "Escale — recrutement possible", self.var_recrutement, jusqu_a=1)
        self._champ_nombre(grille, 2, 1, "Escale — commerce possible", self.var_commerce, jusqu_a=1)
        self._champ_nombre(grille, 2, 2, "Escale — réparation possible", self.var_reparation, jusqu_a=1)

        tk.Label(
            self, textvariable=self.var_des_texte, bg=theme.BG_PANEL,
            fg=theme.FG_MUTED, font=theme.FONT_TEXT,
        ).pack(anchor="w", pady=(10, 0))

        self._maj_des()

    # ------------------------------------------------------------------ #
    def _champ_combo(self, parent, row, col, label, var, valeurs, width, on_select=None):
        cadre = tk.Frame(parent, bg=theme.BG_PANEL)
        cadre.grid(row=row, column=col, sticky="w", padx=(0, 18), pady=(0, 10))
        tk.Label(cadre, text=label, bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT).pack(anchor="w")
        combo = ttk.Combobox(
            cadre, textvariable=var, values=valeurs, state="readonly",
            width=width, style="Jeu.TCombobox",
        )
        combo.pack(anchor="w", pady=(2, 0))
        if on_select:
            combo.bind("<<ComboboxSelected>>", lambda e: on_select())

    def _champ_nombre(self, parent, row, col, label, var, jusqu_a):
        cadre = tk.Frame(parent, bg=theme.BG_PANEL)
        cadre.grid(row=row, column=col, sticky="w", padx=(0, 18), pady=(0, 10))
        tk.Label(cadre, text=label, bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT).pack(anchor="w")
        tk.Spinbox(
            cadre, from_=0, to=jusqu_a, textvariable=var, width=14,
            justify="right", bg=theme.BG_INPUT, fg=theme.FG_TEXT,
            buttonbackground=theme.BG_INPUT, relief="flat",
        ).pack(anchor="w", pady=(2, 0))

    def _maj_des(self):
        de_marchand, de_aventurier = ref.ZONE_DES.get(self.var_zone.get(), ("—", "—"))
        self.var_des_texte.set(f"Dé marchand : {de_marchand}    |    Dé aventurier : {de_aventurier}")

    # ------------------------------------------------------------------ #
    def renumeroter(self, numero: int):
        self.label_titre.configure(text=f"Étape {numero}")

    def valeurs(self) -> Dict:
        de_marchand, de_aventurier = ref.ZONE_DES.get(self.var_zone.get(), (None, None))
        return {
            "Region": self.var_region.get(),
            "ZoneMaritime": self.var_zone.get(),
            "TaillePortEscale": self.var_taille_port.get(),
            "Distance": _vers_nombre(self.var_distance.get()),
            "ChanceRencontreAventurier": _vers_nombre(self.var_chance_aventurier.get()),
            "ChanceRencontreMarchand": _vers_nombre(self.var_chance_marchand.get()),
            "CompetenceVigie": _vers_nombre(self.var_vigie.get()),
            "EscaleRecrutement": _vers_nombre(self.var_recrutement.get()),
            "EscaleCommerce": _vers_nombre(self.var_commerce.get()),
            "EscaleReparation": _vers_nombre(self.var_reparation.get()),
            "DeMarchand": de_marchand,
            "DeAventurier": de_aventurier,
        }


class PanneauGenerationTrajet(tk.Frame):
    """
    Panneau complet : navire + année historique + liste d'étapes
    (ajout/suppression dynamique) + bouton de création du trajet.
    """

    def __init__(
        self, parent, navires: List[str],
        on_creer: Callable[[str, str, int, List[Dict]], None],
    ):
        super().__init__(parent, bg=theme.BG_ROOT)
        self.on_creer = on_creer
        self.lignes: List[LigneEtape] = []

        # --- en-tête : navire + année ----------------------------------------
        entete = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=14)
        entete.pack(fill="x", pady=(0, 12))

        tk.Label(
            entete, text="Nouveau trajet maritime", bg=theme.BG_PANEL,
            fg=theme.FG_TITLE, font=theme.FONT_SECTION,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        tk.Label(
            entete,
            text="Nom du trajet",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT,
        ).grid(row=1, column=0, sticky="w")

        self.var_nom_trajet = tk.StringVar()

        tk.Entry(
            entete,
            textvariable=self.var_nom_trajet,
            width=30,
        ).grid(row=2, column=0, sticky="w", padx=(0, 30), pady=(2, 0))
        tk.Label(
            entete,
            text="Navire",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT
        ).grid(row=3, column=0, sticky="w")

        self.var_navire = tk.StringVar(value=navires[0] if navires else "")

        ttk.Combobox(
            entete,
            textvariable=self.var_navire,
            values=navires,
            state="readonly",
            width=28,
            style="Jeu.TCombobox",
        ).grid(row=4, column=0, sticky="w", padx=(0, 30), pady=(2, 0))

        tk.Label(
            entete,
            text="Année historique du voyage",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT,
        ).grid(row=3, column=1, sticky="w")

        self.var_annee = tk.StringVar(value="1715")

        tk.Spinbox(
            entete,
            from_=1600,
            to=1800,
            textvariable=self.var_annee,
            width=10,
            justify="right",
            bg=theme.BG_INPUT,
            fg=theme.FG_TEXT,
            buttonbackground=theme.BG_INPUT,
            relief="flat",
        ).grid(row=4, column=1, sticky="w", pady=(2, 0))

        if not navires:
            tk.Label(
                entete, text="Aucun navire disponible (moteur.get_navires() a renvoyé une liste vide).",
                bg=theme.BG_PANEL, fg=theme.ERROR, font=theme.FONT_TEXT,
            ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

        # --- zone des étapes ---------------------------------------------------
        self.zone_etapes = tk.Frame(self, bg=theme.BG_ROOT)
        self.zone_etapes.pack(fill="both", expand=True)

        # --- barre d'actions du formulaire --------------------------------------
        bas = tk.Frame(self, bg=theme.BG_ROOT, pady=12)
        bas.pack(fill="x")
        tk.Button(
            bas, text="Ajouter une étape", font=theme.FONT_TEXT_BOLD,
            bg=theme.BG_INPUT, fg=theme.FG_TEXT, relief="flat", cursor="hand2",
            padx=14, pady=7, command=self.ajouter_etape,
        ).pack(side="left")
        tk.Button(
            bas, text="Créer le trajet", font=theme.FONT_TEXT_BOLD,
            bg=theme.ACCENT, fg="#231a08", relief="flat", cursor="hand2",
            padx=20, pady=7, activebackground=theme.ACCENT_HOVER,
            command=self._creer,
        ).pack(side="left", padx=10)

        self.ajouter_etape()  # une première étape par défaut, pour ne pas partir d'un formulaire vide

    def ajouter_etape(self):
        ligne = LigneEtape(self.zone_etapes, len(self.lignes) + 1, self._retirer_etape)
        ligne.pack(fill="x", pady=6)
        self.lignes.append(ligne)

    def _retirer_etape(self, ligne: LigneEtape):
        if len(self.lignes) <= 1:
            return  # on garde toujours au moins une étape dans le formulaire
        ligne.destroy()
        self.lignes.remove(ligne)
        for i, l in enumerate(self.lignes, start=1):
            l.renumeroter(i)

    def _creer(self):
        nom_trajet = self.var_nom_trajet.get().strip()
        navire = self.var_navire.get()

        if not nom_trajet:
            return

        if not navire:
            return

        annee = _vers_nombre(self.var_annee.get())
        etapes = [ligne.valeurs() for ligne in self.lignes]

        self.on_creer(
            nom_trajet,
            navire,
            annee,
            etapes
        )
