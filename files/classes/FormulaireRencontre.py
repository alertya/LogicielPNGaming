import tkinter as tk
from tkinter import messagebox
from classes.Voyage import Voyage
from classes.Navire import Navire

class FormulaireRencontre(tk.Toplevel):

    def __init__(self, parent, moteur, voyage,navire, on_fin=None,instance=None,navire_rencontre=None):
        super().__init__(parent)

        self.title("Rencontre en mer")
        self.instance=instance
        self.moteur = moteur
        self.on_fin = on_fin
        self.voyage = Voyage.charger_depuis_csv(voyage)
        self.navire = navire
        self.navire_rencontre = navire_rencontre
        tk.Label(
            self,
            text="Vous rencontrez un navire. Que souhaitez-vous faire ?"
        ).pack(pady=10)

        tk.Button(
            self,
            text="Commercer",
            command=lambda: self._executer("Commercer")
        ).pack(fill="x", padx=20, pady=5)

        tk.Button(
            self,
            text="Poursuivre",
            command=lambda: self._executer("Poursuivre")
        ).pack(fill="x", padx=20, pady=5)

        tk.Button(
            self,
            text="Hisser le pavillon noir",
            command=lambda: self._executer("HisserPavillonNoir")
        ).pack(fill="x", padx=20, pady=5)

        tk.Button(
            self,
            text="Canonner",
            command=lambda: self._executer("Canonner")
        ).pack(fill="x", padx=20, pady=5)

    def _executer(self, action):
        self.moteur.executer_action(
            "Journal de bord",
            "Journal",
            self.voyage,
            self.navire
        )

        if self.on_fin:
            self.on_fin()

        self.destroy()

    def _choisir(self, action):
        self.on_choix(action)
        self.destroy()



    def get_actions(self):
        return [
            "JourSuivant",
            "Commercer",
            "Poursuivre",
            "HisserPavillonNoir",
            "HisserPavillonRouge"
            "Canonner",
            "Fuir"
        ]

    def _executer(self, action):

        # Nom du navire actuellement rencontré

        # Identification de la catégorie
        if self.voyage.NavireRencontreMarchand:
            type_rencontre = "Marchand"
            self.voyage.NavireRencontre=self.voyage.NavireRencontreMarchand

        if self.voyage.NavireRencontreAventurier:
            type_rencontre = "Aventurier"
            self.voyage.NavireRencontre = self.voyage.NavireRencontreAventurier


        else:
            messagebox.showerror(
                "Erreur",
                f"Navire rencontré non identifié : {self.voyage.NavireRencontre}"
            )
            return

        # Transmission au moteur
        valeurs = {
            "NavireRencontre": self.voyage.NavireRencontre,
            "TypeRencontre": type_rencontre
        }

        resultat = self.moteur.executer_action(
            "Journal de bord",
            "Actions",
            self.voyage,
            action,
            valeurs
        )

        # Affichage du résultat
        if action == "Commercer":
            messagebox.showinfo("Commerce", str(resultat))

        elif action == "HisserPavillonRouge":
            messagebox.showinfo("Pavillon rouge", str(resultat))

        elif action == "HisserPavillonNoir":
            messagebox.showinfo("Pavillon noir", str(resultat))

        elif action == "Poursuivre":
            messagebox.showinfo("Navigation", str(resultat))