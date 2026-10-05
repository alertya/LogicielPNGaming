from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, List
import utils
import config
import theme


class PanneauGenerationPNJ(tk.Frame):

    def __init__(
        self,
        parent,
        zones_commerciales: List[str],
        metiers: List[str],
        types_pnj: List[str],
        on_generer: Callable[[str, str, str, str], None],
    ):
        super().__init__(parent, bg=theme.BG_ROOT)

        self.on_generer = on_generer

        # ============================================================
        # EN-TÊTE
        # ============================================================

        entete = tk.Frame(
            self,
            bg=theme.BG_PANEL,
            padx=16,
            pady=14
        )
        entete.pack(fill="x", pady=(0, 12))

        tk.Label(
            entete,
            text="Nouveau PNJ",
            bg=theme.BG_PANEL,
            fg=theme.FG_TITLE,
            font=theme.FONT_SECTION,
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 10)
        )

        # ------------------------------------------------------------
        # NOM
        # ------------------------------------------------------------

        tk.Label(
            entete,
            text="Nom du PNJ",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT,
        ).grid(
            row=1,
            column=0,
            sticky="w"
        )

        self.var_nom = tk.StringVar()

        tk.Entry(
            entete,
            textvariable=self.var_nom,
            width=30,
            bg=theme.BG_INPUT,
            fg=theme.FG_TEXT,
            relief="flat",
            insertbackground=theme.FG_TEXT,
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(0, 24),
            pady=(2, 0)
        )

        # ------------------------------------------------------------
        # ZONE COMMERCIALE
        # ------------------------------------------------------------

        tk.Label(
            entete,
            text="Zone commerciale",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT,
        ).grid(
            row=1,
            column=1,
            sticky="w"
        )

        self.var_zone = tk.StringVar(
            value=zones_commerciales.iloc[0] if not zones_commerciales.empty else ""
        )

        ttk.Combobox(
            entete,
            textvariable=self.var_zone,
            values=zones_commerciales.tolist(),
            state="readonly",
            width=24,
            style="Jeu.TCombobox",
        ).grid(
            row=2,
            column=1,
            sticky="w",
            pady=(2, 0)
        )

        if not zones_commerciales:
            tk.Label(
                entete,
                text="⚠ Aucune zone commerciale trouvée.",
                bg=theme.BG_PANEL,
                fg=theme.ERROR,
                font=theme.FONT_TEXT,
            ).grid(
                row=3,
                column=0,
                columnspan=2,
                sticky="w",
                pady=(10, 0)
            )

        # ============================================================
        # CARACTÉRISTIQUES DU PNJ
        # ============================================================

        caracteristiques = tk.Frame(
            self,
            bg=theme.BG_PANEL,
            padx=16,
            pady=14
        )
        caracteristiques.pack(
            fill="x",
            pady=(0, 12)
        )

        tk.Label(
            caracteristiques,
            text="Caractéristiques professionnelles",
            bg=theme.BG_PANEL,
            fg=theme.FG_TITLE,
            font=theme.FONT_SECTION,
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 10)
        )

        # ============================================================
        # PARTIE GAUCHE : MÉTIER
        # ============================================================

        gauche = tk.Frame(
            caracteristiques,
            bg=theme.BG_PANEL
        )

        gauche.grid(
            row=1,
            column=0,
            sticky="nw",
            padx=(0, 40)
        )

        tk.Label(
            gauche,
            text="Métier",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT,
        ).pack(
            anchor="w"
        )

        self.var_metier = tk.StringVar(
            value=metiers[0] if metiers else ""
        )

        ttk.Combobox(
            gauche,
            textvariable=self.var_metier,
            values=metiers,
            state="readonly",
            width=30,
            style="Jeu.TCombobox",
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        if not metiers:
            tk.Label(
                gauche,
                text="⚠ Aucun métier trouvé.",
                bg=theme.BG_PANEL,
                fg=theme.ERROR,
                font=theme.FONT_TEXT,
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

        # ============================================================
        # PARTIE DROITE : TYPE
        # ============================================================

        droite = tk.Frame(
            caracteristiques,
            bg=theme.BG_PANEL
        )

        droite.grid(
            row=1,
            column=1,
            sticky="nw"
        )

        tk.Label(
            droite,
            text="Type",
            bg=theme.BG_PANEL,
            fg=theme.FG_MUTED,
            font=theme.FONT_TEXT,
        ).pack(
            anchor="w"
        )

        self.var_type = tk.StringVar(
            value=types_pnj[0] if types_pnj else ""
        )

        ttk.Combobox(
            droite,
            textvariable=self.var_type,
            values=types_pnj,
            state="readonly",
            width=30,
            style="Jeu.TCombobox",
        ).pack(
            anchor="w",
            pady=(2, 0)
        )

        if not types_pnj:
            tk.Label(
                droite,
                text="⚠ Aucun type trouvé.",
                bg=theme.BG_PANEL,
                fg=theme.ERROR,
                font=theme.FONT_TEXT,
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

        # ============================================================
        # BOUTON DE GÉNÉRATION
        # ============================================================

        bas = tk.Frame(
            self,
            bg=theme.BG_ROOT,
            pady=4
        )
        bas.pack(fill="x")

        tk.Button(
            bas,
            text="Générer le PNJ",
            font=theme.FONT_TEXT_BOLD,
            bg=theme.ACCENT,
            fg="#231a08",
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=7,
            activebackground=theme.ACCENT_HOVER,
            command=self._generer,
        ).pack(
            side="left"
        )

    # ================================================================
    # GÉNÉRATION
    # ================================================================

    def _generer(self):

        nom = self.var_nom.get().strip()

        if not nom:
            return

        zone = self.var_zone.get()
        metier = self.var_metier.get()
        type_pnj = self.var_type.get()

        self.on_generer(
            nom,
            zone,
            metier,
            type_pnj,
        )

