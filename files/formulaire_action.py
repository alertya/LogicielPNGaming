import tkinter as tk
from tkinter import ttk


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
                        text="Marchandise à vendre"
                    ).grid(row=0, column=0, padx=10, pady=10)

            self.variables["Marchandise"] = tk.StringVar()

            ttk.Combobox(
                        self,
                        textvariable=self.variables["Marchandise"],
                        values=self.moteur.get_instances("Marchandises", "Afficher"),
                        state="readonly"
                    ).grid(row=0, column=1, padx=10, pady=10)

                    # ---------------- Tonnage ----------------
            tk.Label(
                        self,
                        text="Tonnage à vendre"
                    ).grid(row=1, column=0, padx=10, pady=10)

            self.variables["Tonnage"] = tk.IntVar(value=0)

            tk.Spinbox(
                        self,
                        from_=0,
                        to=10000,
                        textvariable=self.variables["Tonnage"]
                    ).grid(row=1, column=1, padx=10, pady=10)

            # ---------------- Succès ----------------
            tk.Label(
                        self,
                        text="Succès de commerce"
                    ).grid(row=2, column=0, padx=10, pady=10)

            self.variables["Succes"] = tk.IntVar(value=0)

            tk.Spinbox(
                        self,
                        from_=0,
                        to=10,
                        textvariable=self.variables["Succes"]
                    ).grid(row=2, column=1, padx=10, pady=10)

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