import tkinter as tk
from tkinter import ttk
import os
import config
from classes.Marchandise import Marchandise
import utils
class FormulaireAction(tk.Toplevel):

    def __init__(self, parent, action, moteur, on_valider):

        super().__init__(parent)

        self.action = action
        self.moteur = moteur
        self.on_valider = on_valider

        self.title(action)
        self.geometry("400x250")

        self.variables = {}

        self.construire()

    def construire(self):
        if self.action == "Vendre":
            # ---------------- Marchandise ----------------
            tk.Label(
                        self,
                        text="Stock à vendre"
                    ).grid(row=0, column=0, padx=10, pady=10)

            self.variables["Vendeur"] = tk.StringVar()

            self.combo_marchandise = ttk.Combobox(
                self,
                textvariable=self.variables["Vendeur"],
                values=self.moteur.get_instances("Marchandises", "Afficher"),
                state="readonly"
            )
            self.combo_marchandise.grid(row=0, column=1, padx=10, pady=10)

            self.combo_marchandise.bind(
                "<<ComboboxSelected>>",
                self.changer_marchandise)

            tk.Label(
                self,
                text="Cargaison à vendre"
            ).grid(row=1, column=0, padx=10, pady=10)

            self.variables["Cargaison"] = tk.StringVar()

            self.combo_cargaison = ttk.Combobox(
                self,
                textvariable=self.variables["Cargaison"],
                values=[],
                state="readonly"
            )

            self.combo_cargaison.grid(row=1, column=1, padx=10, pady=10)
            self.combo_cargaison.bind(
                "<<ComboboxSelected>>",
                self.changer_cargaison
            )
                    # ---------------- Tonnage ----------------
            tk.Label(
                        self,
                        text="Tonnage à vendre"
                    ).grid(row=2, column=0, padx=10, pady=10)

            self.variables["Tonnage"] = tk.IntVar(value=0)

            tk.Spinbox(
                        self,
                        from_=0,
                        to=10000,
                        textvariable=self.variables["Tonnage"]
                    ).grid(row=2, column=1, padx=10, pady=10)
            self.prix_exces = tk.StringVar(value="Excès : -")
            self.prix_normal = tk.StringVar(value="Normal : -")
            self.prix_penurie = tk.StringVar(value="Pénurie : -")

            tk.Label(
                self,
                textvariable=self.prix_exces
            ).grid(row=4, column=0, columnspan=2, sticky="w", padx=10)

            tk.Label(
                self,
                textvariable=self.prix_normal
            ).grid(row=5, column=0, columnspan=2, sticky="w", padx=10)

            tk.Label(
                self,
                textvariable=self.prix_penurie
            ).grid(row=6, column=0, columnspan=2, sticky="w", padx=10)

            # ---------------- Succès ----------------
            tk.Label(
                        self,
                        text="Succès de commerce"
                    ).grid(row=7, column=0, padx=10, pady=10)

            self.variables["Succes"] = tk.IntVar(value=0)

            tk.Spinbox(
                        self,
                        from_=0,
                        to=10,
                        textvariable=self.variables["Succes"]
                    ).grid(row=7, column=1, padx=10, pady=10)


                    # ---------------- Validation ----------------
            tk.Button(
                        self,
                        text="Valider",
                        command=self.valider
                    ).grid(row=8, column=0, columnspan=2, pady=20)
        if self.action == "Acheter":
            # ---------------- Marchandise ----------------
            tk.Label(
                        self,
                        text="Stockage où acheter"
                    ).grid(row=0, column=0, padx=10, pady=10)

            self.variables["Vendeur"] = tk.StringVar()

            self.combo_marchandise = ttk.Combobox(
                self,
                textvariable=self.variables["Vendeur"],
                values=self.moteur.get_instances("Marchandises", "Afficher"),
                state="readonly"
            )
            self.combo_marchandise.grid(row=0, column=1, padx=10, pady=10)

            self.combo_marchandise.bind(
                "<<ComboboxSelected>>",
                self.changer_marchandise)

            tk.Label(
                self,
                text="Cargaison à acheter"
            ).grid(row=1, column=0, padx=10, pady=10)

            self.variables["Cargaison"] = tk.StringVar()

            self.combo_cargaison = ttk.Combobox(
                self,
                textvariable=self.variables["Cargaison"],
                values=[],
                state="readonly"
            )

            self.combo_cargaison.grid(row=1, column=1, padx=10, pady=10)
            self.combo_cargaison.bind(
                "<<ComboboxSelected>>",
                self.changer_cargaison
            )
            # ---------------- Marchandise ----------------
            tk.Label(
                        self,
                        text="Cargaison à entreposer"
                    ).grid(row=2, column=0, padx=10, pady=10)

            self.variables["Acheteur"] = tk.StringVar()

            self.combo_acheteur = ttk.Combobox(
                self,
                textvariable=self.variables["Acheteur"],
                values=self.moteur.get_instances("Marchandises", "Afficher"),
                state="readonly"
            )
            self.combo_acheteur.grid(row=2, column=1, padx=10, pady=10)
            self.prix_exces = tk.StringVar(value="Excès : -")
            self.prix_normal = tk.StringVar(value="Normal : -")
            self.prix_penurie = tk.StringVar(value="Pénurie : -")

            tk.Label(
                self,
                textvariable=self.prix_exces
            ).grid(row=4, column=0, columnspan=2, sticky="w", padx=10)

            tk.Label(
                self,
                textvariable=self.prix_normal
            ).grid(row=5, column=0, columnspan=2, sticky="w", padx=10)

            tk.Label(
                self,
                textvariable=self.prix_penurie
            ).grid(row=6, column=0, columnspan=2, sticky="w", padx=10)
                    # ---------------- Tonnage ----------------
            tk.Label(
                        self,
                        text="Tonnage à acheter"
                    ).grid(row=7, column=0, padx=10, pady=10)

            self.variables["Tonnage"] = tk.IntVar(value=0)

            tk.Spinbox(
                        self,
                        from_=0,
                        to=10000,
                        textvariable=self.variables["Tonnage"]
                    ).grid(row=7, column=1, padx=10, pady=10)

            # ---------------- Succès ----------------
            tk.Label(
                        self,
                        text="Succès de commerce"
                    ).grid(row=8, column=0, padx=10, pady=10)

            self.variables["Succes"] = tk.IntVar(value=0)

            tk.Spinbox(
                        self,
                        from_=0,
                        to=10,
                        textvariable=self.variables["Succes"]
                    ).grid(row=7, column=1, padx=10, pady=10)

                    # ---------------- Validation ----------------
            tk.Button(
                        self,
                        text="Valider",
                        command=self.valider
                    ).grid(row=8, column=0, columnspan=2, pady=20)
        if self.action == "Piller":
            # ---------------- Marchandise ----------------
            tk.Label(
                        self,
                        text="Stockage pillé"
                    ).grid(row=0, column=0, padx=10, pady=10)

            self.variables["Vendeur"] = tk.StringVar()

            self.combo_marchandise = ttk.Combobox(
                self,
                textvariable=self.variables["Vendeur"],
                values=self.moteur.get_instances("Marchandises", "Afficher"),
                state="readonly"
            )
            self.combo_marchandise.grid(row=0, column=1, padx=10, pady=10)

            self.combo_marchandise.bind(
                "<<ComboboxSelected>>",
                self.changer_marchandise)

            tk.Label(
                self,
                text="Cargaison à piller"
            ).grid(row=1, column=0, padx=10, pady=10)

            self.variables["Cargaison"] = tk.StringVar()

            self.combo_cargaison = ttk.Combobox(
                self,
                textvariable=self.variables["Cargaison"],
                values=[],
                state="readonly"
            )

            self.combo_cargaison.grid(row=1, column=1, padx=10, pady=10)
            # ---------------- Marchandise ----------------
            tk.Label(
                        self,
                        text="Cargaison à entreposer"
                    ).grid(row=2, column=0, padx=10, pady=10)

            self.variables["Acheteur"] = tk.StringVar()

            self.combo_acheteur = ttk.Combobox(
                self,
                textvariable=self.variables["Acheteur"],
                values=self.moteur.get_instances("Marchandises", "Afficher"),
                state="readonly"
            )
            self.combo_acheteur.grid(row=2, column=1, padx=10, pady=10)
                    # ---------------- Tonnage ----------------


                    # ---------------- Validation ----------------
            tk.Button(
                        self,
                        text="Valider",
                        command=self.valider
                    ).grid(row=3, column=0, columnspan=2, pady=20)
        if self.action == "Recruter":
            tk.Label(
                self,
                text="Equipage recruteur"
            ).grid(row=0, column=0, padx=10, pady=10)

            self.variables["Equipage_source"] = tk.StringVar()

            combo = ttk.Combobox(
                self,
                textvariable=self.variables["Equipage_source"],
                values=self.moteur.get_instances("Equipage", "Afficher"),
                state="readonly"
            )

            combo.grid(row=0, column=1)

            tk.Label(
                self,
                text="Equipage recruté"
            ).grid(row=1, column=0, padx=10, pady=10)

            self.variables["Equipage_cible"] = tk.StringVar()

            combo = ttk.Combobox(
                self,
                textvariable=self.variables["Equipage_cible"],
                values=self.moteur.get_instances("Equipage", "Afficher"),
                state="readonly"
            )

            combo.grid(row=1, column=1)

            tk.Label(
                self,
                text="Succes de MeneurHomme sous Charisme"
            ).grid(row=2, column=0, padx=10, pady=10)

            self.variables["Nombre"] = tk.IntVar(value=0)

            tk.Spinbox(
                self,
                from_=0,
                to=10,
                textvariable=self.variables["Nombre"]
            ).grid(row=2, column=1)

            tk.Button(
                self,
                text="Valider",
                command=self.valider
            ).grid(row=3, column=0, columnspan=2, pady=20)
        if self.action == "BatailleTerrestre":
            # Titres des colonnes
            tk.Label(
                self,
                text="Équipage 1",
                font=("Arial", 10, "bold")
            ).grid(row=0, column=0, padx=10, pady=10)

            tk.Label(
                self,
                text="Équipage 2",
                font=("Arial", 10, "bold")
            ).grid(row=0, column=1, padx=10, pady=10)

            # ---------------- Equipage 1 ----------------

            self.variables["Equipage1"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Equipage1"],
                values=self.moteur.get_instances("Equipage", "Afficher"),
                state="readonly"
            ).grid(row=1, column=0, padx=10, pady=5)

            self.variables["Competence1"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Competence1"],
                values=[
                    "ArmesBlanches",
                    "Pistolet",
                    "Mousquet",
                    "Commandement"
                ],
                state="readonly"
            ).grid(row=2, column=0, padx=10, pady=5)

            self.variables["Bonus1"] = tk.IntVar(value=0)

            tk.Spinbox(
                self,
                from_=-10,
                to=10,
                textvariable=self.variables["Bonus1"]
            ).grid(row=3, column=0, padx=10, pady=5)

            # ---------------- Equipage 2 ----------------

            self.variables["Equipage2"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Equipage2"],
                values=self.moteur.get_instances("Equipage", "Afficher"),
                state="readonly"
            ).grid(row=1, column=1, padx=10, pady=5)

            self.variables["Competence2"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Competence2"],
                values=[
                    "ArmesBlanches",
                    "Pistolet",
                    "Mousquet",
                    "Commandement"
                ],
                state="readonly"
            ).grid(row=2, column=1, padx=10, pady=5)

            self.variables["Bonus2"] = tk.IntVar(value=0)

            tk.Spinbox(
                self,
                from_=-10,
                to=10,
                textvariable=self.variables["Bonus2"]
            ).grid(row=3, column=1, padx=10, pady=5)

            # ---------------- Validation ----------------

            tk.Button(
                self,
                text="Valider",
                command=self.valider
            ).grid(row=4, column=0, columnspan=2, pady=20)
        if self.action == "RecruterType":
            tk.Label(
                self,
                text="Equipage recruteur"
            ).grid(row=0, column=0, padx=10, pady=10)

            self.variables["Equipage_source"] = tk.StringVar()

            combo = ttk.Combobox(
                self,
                textvariable=self.variables["Equipage_source"],
                values=self.moteur.get_instances("Equipage", "Afficher"),
                state="readonly"
            )

            combo.grid(row=0, column=1)

            tk.Label(
                self,
                text="Type a recruter"
            ).grid(row=1, column=0, padx=10, pady=10)

            self.variables["Type"] = tk.StringVar()

            combo = ttk.Combobox(
                self,
                textvariable=self.variables["Type"],
                values=self.moteur.get_types_equipage(),
                state="readonly"
            )

            combo.grid(row=1, column=1)

            tk.Label(
                self,
                text="Nombre de type a recruter"
            ).grid(row=2, column=0, padx=10, pady=10)

            self.variables["Nombre"] = tk.IntVar(value=0)

            tk.Spinbox(
                self,
                from_=0,
                to=10,
                textvariable=self.variables["Nombre"]
            ).grid(row=2, column=1)

            tk.Button(
                self,
                text="Valider",
                command=self.valider
            ).grid(row=3, column=0, columnspan=2, pady=20)
        if self.action == "CombatNaval":
            # Titres des colonnes
            tk.Label(
                self,
                text="Navire 1",
                font=("Arial", 10, "bold")
            ).grid(row=0, column=0, padx=10, pady=10)

            tk.Label(
                self,
                text="Navire 2",
                font=("Arial", 10, "bold")
            ).grid(row=0, column=1, padx=10, pady=10)

            # ---------------- Equipage 1 ----------------

            self.variables["Navire1"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Navire1"],
                values=self.moteur.get_instances("Navire", "Afficher"),
                state="readonly"
            ).grid(row=1, column=0, padx=10, pady=5)

            self.variables["Munition1"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Munition1"],
                values=[
                    "Mitraille",
                    "Coque",
                    "Voile"
                ],
                state="readonly"
            ).grid(row=2, column=0, padx=10, pady=5)

            self.variables["Bonus1"] = tk.IntVar(value=0)

            tk.Spinbox(
                self,
                from_=-10,
                to=10,
                textvariable=self.variables["Bonus1"]
            ).grid(row=3, column=0, padx=10, pady=5)

            # ---------------- Equipage 2 ----------------

            self.variables["Navire2"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Navire2"],
                values=self.moteur.get_instances("Navire", "Afficher"),
                state="readonly"
            ).grid(row=1, column=1, padx=10, pady=5)

            self.variables["Munition2"] = tk.StringVar()

            ttk.Combobox(
                self,
                textvariable=self.variables["Munition2"],
                values=[
                    "Mitraille",
                    "Coque",
                    "Voile"
                ],
                state="readonly"
            ).grid(row=2, column=1, padx=10, pady=5)

            self.variables["Bonus2"] = tk.IntVar(value=0)

            tk.Spinbox(
                self,
                from_=-10,
                to=10,
                textvariable=self.variables["Bonus2"]
            ).grid(row=3, column=1, padx=10, pady=5)

            # ---------------- Validation ----------------

            tk.Button(
                self,
                text="Valider",
                command=self.valider
            ).grid(row=4, column=0, columnspan=2, pady=20)
        if self.action == "JourSuivant":
            message = self.moteur.JourSuivant(self.instance_actuelle)
            self.statut_var.set(message)
            self.rafraichir_instances()
        if self.action == "LanceCompetence":
            valeurs={}
            dossier_pnj = os.path.join(config.BASE_PATH, "PNJ")

            self.instances_pnj = []

            if os.path.exists(dossier_pnj):
                for fichier in os.listdir(dossier_pnj):
                    if fichier.lower().endswith(".csv"):
                        self.instances_pnj.append(
                            os.path.splitext(fichier)[0]
                        )

            self.instances_pnj.sort()

            # =====================================================
            # PNJ
            # =====================================================

            tk.Label(
                self,
                text="PNJ"
            ).pack(
                anchor="w",
                padx=20,
                pady=(20, 5)
            )

            self.pnj_var = tk.StringVar()
            self.variables['instance']=self.pnj_var
            self.combo_pnj = ttk.Combobox(
                self,
                textvariable=self.pnj_var,
                values=self.instances_pnj,
                state="readonly",
                width=30
            )

            self.combo_pnj.pack(
                anchor="w",
                padx=20,
                pady=5
            )

            if self.instances_pnj:
                self.combo_pnj.current(0)

            # =====================================================
            # Compétence
            # =====================================================

            tk.Label(
                self,
                text="Compétence"
            ).pack(
                anchor="w",
                padx=20,
                pady=(20, 5)
            )

            self.competences = list(utils.COMPETENCES['Competence'])

            self.competence_var = tk.StringVar()
            self.variables['Competence']=self.competence_var
            self.combo_competence = ttk.Combobox(
                self,
                textvariable=self.competence_var,
                values=self.competences,
                state="readonly",
                width=30
            )

            self.combo_competence.pack(
                anchor="w",
                padx=20,
                pady=5
            )

            if self.competences:
                self.combo_competence.current(0)

            # =====================================================
            # Bouton Valider
            # =====================================================

            self.bouton_valider = tk.Button(
                self,
                text="Valider",
                command=self.valider
            )

            self.bouton_valider.pack(
                padx=20,
                pady=20
            )





    def recuperer_valeurs(self):
        return {
            nom: variable.get()
            for nom, variable in self.variables.items()
        }

    def valider(self):
        valeurs = self.recuperer_valeurs()

        self.on_valider(
            self.action,
            valeurs
        )

        self.destroy()

    def changer_marchandise(self, event=None):

        nom = self.variables["Vendeur"].get()

        marchandise = Marchandise.charger_depuis_csv(nom)

        valeurs = [
            c["Cargaison"]
            for c in marchandise.Cargaisons
        ]

        self.combo_cargaison["values"] = valeurs

        if valeurs:
            self.variables["Cargaison"].set(valeurs[0])
            self.changer_cargaison()

    def changer_cargaison(self, event=None):

        nom = self.variables["Cargaison"].get()

        ligne = utils.MARCHANDISES[
            utils.MARCHANDISES["Cargaison"] == nom
            ]


        if ligne.empty:
            print("Aucune ligne trouvée")
            return

        ligne = ligne.iloc[0]


        self.prix_exces.set(f"Excès : {ligne['PrixExces']}")
        self.prix_normal.set(f"Normal : {ligne['PrixNormal']}")
        self.prix_penurie.set(f"Pénurie : {ligne['PrixPenurie']}")