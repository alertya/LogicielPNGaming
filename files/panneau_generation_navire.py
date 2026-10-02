"""
panneau_generation_navire.py
-------------------------------
Panneau spécifique à l'onglet "Navire" -> "Générer".

Formulaire de création d'un navire : nom, type (liste déroulante issue de
la colonne "Typologie" de data/RencontreNavire.csv) et région d'origine
(liste déroulante issue de la colonne "Regions" de data/ListeRegions.csv).

Ce panneau ne connaît rien du moteur : il transmet les valeurs saisies via
le callback `on_generer(nom, type_navire, region)` fourni par app.py, qui
appelle `moteur.generer_navire(...)`.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, List

import theme


class PanneauGenerationNavire(tk.Frame):
    def __init__(
        self, parent, types_navire: List[str], regions: List[str],
        on_generer: Callable[[str, str, str], None],
    ):
        super().__init__(parent, bg=theme.BG_ROOT)
        self.on_generer = on_generer

        entete = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=14)
        entete.pack(fill="x", pady=(0, 12))

        tk.Label(
            entete, text="Nouveau navire", bg=theme.BG_PANEL,
            fg=theme.FG_TITLE, font=theme.FONT_SECTION,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(entete, text="Nom du navire", bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT)\
            .grid(row=1, column=0, sticky="w")
        self.var_nom = tk.StringVar()
        tk.Entry(
            entete, textvariable=self.var_nom, width=30,
            bg=theme.BG_INPUT, fg=theme.FG_TEXT, relief="flat", insertbackground=theme.FG_TEXT,
        ).grid(row=2, column=0, sticky="w", padx=(0, 24), pady=(2, 0))

        tk.Label(entete, text="Type de navire", bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT)\
            .grid(row=1, column=1, sticky="w")
        self.var_type = tk.StringVar(value=types_navire[0] if types_navire else "")
        ttk.Combobox(
            entete, textvariable=self.var_type, values=types_navire, state="readonly",
            width=28, style="Jeu.TCombobox",
        ).grid(row=2, column=1, sticky="w", padx=(0, 24), pady=(2, 0))

        tk.Label(entete, text="Région d'origine", bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT)\
            .grid(row=1, column=2, sticky="w")
        self.var_region = tk.StringVar(value=regions[0] if regions else "")
        ttk.Combobox(
            entete, textvariable=self.var_region, values=regions, state="readonly",
            width=28, style="Jeu.TCombobox",
        ).grid(row=2, column=2, sticky="w", pady=(2, 0))

        avertissements = []
        if not types_navire:
            avertissements.append("colonne « Typologie » de data/RencontreNavire.csv introuvable ou vide")
        if not regions:
            avertissements.append("colonne « Regions » de data/ListeRegions.csv introuvable ou vide")
        if avertissements:
            tk.Label(
                entete, text="⚠ " + " ; ".join(avertissements),
                bg=theme.BG_PANEL, fg=theme.ERROR, font=theme.FONT_TEXT,
            ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))

        bas = tk.Frame(self, bg=theme.BG_ROOT, pady=4)
        bas.pack(fill="x")
        tk.Button(
            bas, text="Générer le navire", font=theme.FONT_TEXT_BOLD,
            bg=theme.ACCENT, fg="#231a08", relief="flat", cursor="hand2",
            padx=20, pady=7, activebackground=theme.ACCENT_HOVER,
            command=self._generer,
        ).pack(side="left")

    def _generer(self):
        nom = self.var_nom.get().strip()
        if not nom:
            return
        self.on_generer(nom, self.var_type.get(), self.var_region.get())
