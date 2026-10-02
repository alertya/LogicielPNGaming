"""
panneau_generation_equipage.py
--------------------------------
Panneau spécifique à l'onglet "Equipage" -> "Générer".

Formulaire de création d'un équipage : nom, type (liste déroulante issue de
la colonne "Type" de data/ListeProf.csv), effectif total, et répartition
par typologie (Calfat, Coq, Charpentier, Chirurgien, Pilote, Soldat,
Voilier).

Ce panneau ne connaît rien du moteur : il collecte les valeurs saisies et
les transmet via le callback `on_generer(nom, type_equipage, nombre,
effectifs)` fourni par app.py, qui appelle `moteur.generer_equipage(...)`.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List

import theme

# Typologies d'équipage avec une saisie de chiffre dédiée dans le formulaire.
TYPOLOGIES_EQUIPAGE = ["Calfat", "Coq", "Charpentier", "Chirurgien", "Pilote", "Soldat", "Voilier"]


def _vers_entier(texte) -> int:
    try:
        return int(str(texte).strip())
    except (ValueError, TypeError):
        return 0


class PanneauGenerationEquipage(tk.Frame):
    def __init__(
        self, parent, types_equipage: List[str],
        on_generer: Callable[[str, str, int, Dict[str, int]], None],
    ):
        super().__init__(parent, bg=theme.BG_ROOT)
        self.on_generer = on_generer

        # --- en-tête : nom, type, effectif total ------------------------------
        entete = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=14)
        entete.pack(fill="x", pady=(0, 12))

        tk.Label(
            entete, text="Nouvel équipage", bg=theme.BG_PANEL,
            fg=theme.FG_TITLE, font=theme.FONT_SECTION,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(entete, text="Nom de l'équipage", bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT)\
            .grid(row=1, column=0, sticky="w")
        self.var_nom = tk.StringVar()
        tk.Entry(
            entete, textvariable=self.var_nom, width=30,
            bg=theme.BG_INPUT, fg=theme.FG_TEXT, relief="flat", insertbackground=theme.FG_TEXT,
        ).grid(row=2, column=0, sticky="w", padx=(0, 24), pady=(2, 0))

        tk.Label(entete, text="Type d'équipage", bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT)\
            .grid(row=1, column=1, sticky="w")
        self.var_type = tk.StringVar(value=types_equipage[0] if types_equipage else "")
        ttk.Combobox(
            entete, textvariable=self.var_type, values=types_equipage, state="readonly",
            width=24, style="Jeu.TCombobox",
        ).grid(row=2, column=1, sticky="w", padx=(0, 24), pady=(2, 0))

        tk.Label(entete, text="Nombre de personnes", bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT)\
            .grid(row=1, column=2, sticky="w")
        self.var_nombre = tk.StringVar(value="0")
        tk.Spinbox(
            entete, from_=0, to=2000, textvariable=self.var_nombre, width=10, justify="right",
            bg=theme.BG_INPUT, fg=theme.FG_TEXT, buttonbackground=theme.BG_INPUT, relief="flat",
        ).grid(row=2, column=2, sticky="w", pady=(2, 0))

        if not types_equipage:
            tk.Label(
                entete,
                text="⚠ Aucun type trouvé (colonne « Type » de data/ListeProf.csv introuvable ou vide).",
                bg=theme.BG_PANEL, fg=theme.ERROR, font=theme.FONT_TEXT,
            ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(10, 0))

        # --- répartition par typologie -----------------------------------------
        typo_cadre = tk.Frame(self, bg=theme.BG_PANEL, padx=16, pady=14)
        typo_cadre.pack(fill="x", pady=(0, 12))

        tk.Label(
            typo_cadre, text="Répartition par typologie", bg=theme.BG_PANEL,
            fg=theme.FG_TITLE, font=theme.FONT_SECTION,
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        self.vars_typologies: Dict[str, tk.StringVar] = {}
        for i, typo in enumerate(TYPOLOGIES_EQUIPAGE):
            row = 1 + i // 4
            col = i % 4
            cadre = tk.Frame(typo_cadre, bg=theme.BG_PANEL)
            cadre.grid(row=row, column=col, sticky="w", padx=(0, 18), pady=(0, 10))
            tk.Label(cadre, text=typo, bg=theme.BG_PANEL, fg=theme.FG_MUTED, font=theme.FONT_TEXT).pack(anchor="w")
            var = tk.StringVar(value="0")
            tk.Spinbox(
                cadre, from_=0, to=2000, textvariable=var, width=10, justify="right",
                bg=theme.BG_INPUT, fg=theme.FG_TEXT, buttonbackground=theme.BG_INPUT, relief="flat",
            ).pack(anchor="w", pady=(2, 0))
            self.vars_typologies[typo] = var

        # --- bouton de génération ------------------------------------------------
        bas = tk.Frame(self, bg=theme.BG_ROOT, pady=4)
        bas.pack(fill="x")
        tk.Button(
            bas, text="Générer l'équipage", font=theme.FONT_TEXT_BOLD,
            bg=theme.ACCENT, fg="#231a08", relief="flat", cursor="hand2",
            padx=20, pady=7, activebackground=theme.ACCENT_HOVER,
            command=self._generer,
        ).pack(side="left")

    def _generer(self):
        nom = self.var_nom.get().strip()
        if not nom:
            return
        type_equipage = self.var_type.get()
        nombre = _vers_entier(self.var_nombre.get())
        effectifs = {typo: _vers_entier(var.get()) for typo, var in self.vars_typologies.items()}
        self.on_generer(nom, type_equipage, nombre, effectifs)
