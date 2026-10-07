import tkinter as tk
from tkinter import messagebox

class FormulaireRencontre(tk.Toplevel):

    def __init__(self, parent, moteur, voyage,navire, on_fin=None,instance=None):
        super().__init__(parent)

        self.title("Rencontre en mer")
        self.instance=instance
        self.moteur = moteur
        self.on_fin = on_fin
        self.voyage=voyage
        self.navire=navire
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
            command=lambda: self._executer("PavillonNoir")
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
            action,{"navire_rencontre":self.navire}
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
            "PavillonNoir",
            "Canonner",
            "Fuir"
        ]