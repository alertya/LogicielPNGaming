
import tkinter as tk
from tkinter import ttk


class PanneauGenerationPNJ(tk.Frame):

    def __init__(
        self,
        parent,
        zones_commerciales,
        metiers,
        types_pnj,
        on_generer,
        on_generer_metier=None,
        on_generer_type=None
    ):
        super().__init__(parent)

        self.on_generer = on_generer
        self.on_generer_metier = on_generer_metier
        self.on_generer_type = on_generer_type

        # On conserve les objets originaux
        self.zones_commerciales = list(zones_commerciales)
        self.metiers = list(metiers)
        self.types_pnj = list(types_pnj)

        # =========================================================
        # NOM
        # =========================================================

        cadre_nom = tk.Frame(self)
        cadre_nom.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            cadre_nom,
            text="Nom du PNJ :"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.nom_var = tk.StringVar()

        self.entry_nom = tk.Entry(
            cadre_nom,
            textvariable=self.nom_var
        )

        self.entry_nom.pack(
            side="left",
            fill="x",
            expand=True
        )

        # =========================================================
        # ZONE COMMERCIALE
        # =========================================================

        cadre_zone = tk.Frame(self)
        cadre_zone.pack(
            fill="x",
            padx=20,
            pady=10
        )

        tk.Label(
            cadre_zone,
            text="Zone commerciale :"
        ).pack(
            side="left",
            padx=(0, 10)
        )

        self.zone_var = tk.StringVar()

        self.combo_zone = ttk.Combobox(
            cadre_zone,
            textvariable=self.zone_var,
            values=[
                self._texte_objet(zone)
                for zone in self.zones_commerciales
            ],
            state="readonly",
            width=30
        )

        self.combo_zone.pack(
            side="left",
            fill="x",
            expand=True
        )

        if self.zones_commerciales:
            self.combo_zone.current(0)

        # =========================================================
        # CADRE METIER / TYPE
        # =========================================================

        cadre_profession = tk.Frame(self)

        cadre_profession.pack(
            fill="x",
            padx=20,
            pady=10
        )

        # Deux colonnes de même largeur
        cadre_profession.columnconfigure(0, weight=1)
        cadre_profession.columnconfigure(1, weight=1)

        # =========================================================
        # COLONNE GAUCHE : METIER
        # =========================================================

        cadre_metier = tk.Frame(cadre_profession)

        cadre_metier.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 10)
        )

        tk.Label(
            cadre_metier,
            text="Métier"
        ).pack(
            anchor="w"
        )

        self.metier_var = tk.StringVar()

        self.combo_metier = ttk.Combobox(
            cadre_metier,
            textvariable=self.metier_var,
            values=[
                self._texte_objet(metier)
                for metier in self.metiers
            ],
            state="readonly",
            width=30
        )

        self.combo_metier.pack(
            fill="x",
            pady=(5, 8)
        )

        if self.metiers:
            self.combo_metier.current(0)

        self.bouton_generer_metier = tk.Button(
            cadre_metier,
            text="Générer profession",
            command=self._generer_metier
        )

        self.bouton_generer_metier.pack(
            anchor="w"
        )

        # =========================================================
        # COLONNE DROITE : TYPE
        # =========================================================

        cadre_type = tk.Frame(cadre_profession)

        cadre_type.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 0)
        )

        tk.Label(
            cadre_type,
            text="Type"
        ).pack(
            anchor="w"
        )

        self.type_var = tk.StringVar()

        self.combo_type = ttk.Combobox(
            cadre_type,
            textvariable=self.type_var,
            values=[
                self._texte_objet(type_pnj)
                for type_pnj in self.types_pnj
            ],
            state="readonly",
            width=30
        )

        self.combo_type.pack(
            fill="x",
            pady=(5, 8)
        )

        if self.types_pnj:
            self.combo_type.current(0)

        self.bouton_generer_type = tk.Button(
            cadre_type,
            text="Générer type",
            command=self._generer_type
        )

        self.bouton_generer_type.pack(
            anchor="w"
        )

        # =========================================================
        # BOUTON GENERATION PNJ
        # =========================================================

        cadre_bouton = tk.Frame(self)

        cadre_bouton.pack(
            fill="x",
            padx=20,
            pady=20
        )


        self.bouton_generer.pack()

    # =============================================================
    # TEXTE AFFICHÉ DANS LES COMBOBOX
    # =============================================================

    @staticmethod
    def _texte_objet(objet):

        if isinstance(objet, str):
            return objet

        if hasattr(objet, "Name"):
            return str(objet.Name)

        if hasattr(objet, "Nom"):
            return str(objet.Nom)

        if hasattr(objet, "nom"):
            return str(objet.nom)

        return str(objet)

    # =============================================================
    # RECUPERATION DE L'OBJET SELECTIONNE
    # =============================================================

    def _objet_selectionne(self, combobox, objets):

        index = combobox.current()

        if index < 0:
            return None

        if index >= len(objets):
            return None

        return objets[index]

    # =============================================================
    # GENERER UNE PROFESSION
    # =============================================================

    def _generer_metier(self):

        if self.on_generer_metier is not None:
            self.on_generer_metier(
                self._objet_selectionne(
                    self.combo_metier,
                    self.metiers
                )
            )

    # =============================================================
    # GENERER UN TYPE
    # =============================================================

    def _generer_type(self):

        if self.on_generer_type is not None:
            self.on_generer_type(
                self._objet_selectionne(
                    self.combo_type,
                    self.types_pnj
                )
            )

    # =============================================================
    # GENERATION DU PNJ
    # =============================================================

    def _generer(self):

        nom = self.nom_var.get().strip()

        zone = self._objet_selectionne(
            self.combo_zone,
            self.zones_commerciales
        )

        metier = self._objet_selectionne(
            self.combo_metier,
            self.metiers
        )

        type_pnj = self._objet_selectionne(
            self.combo_type,
            self.types_pnj
        )

        # Vérification
        if not nom:
            return

        if zone is None:
            return

        if metier is None:
            return

        if type_pnj is None:
            return

        # Transmission des OBJETS originaux
        self.on_generer(
            nom,
            zone,
            metier,
            type_pnj
        )

### Dans `app.py`

