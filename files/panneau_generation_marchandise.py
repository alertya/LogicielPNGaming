import tkinter as tk
from tkinter import ttk, messagebox

import utils
from classes.Marchandise import Marchandise


class PanneauGenerationMarchandise(tk.Toplevel):

    def __init__(self, parent, moteur=None):

        super().__init__(parent)

        self.moteur = moteur

        self.title("Génération de marchandises")
        self.geometry("700x600")

        self.stock = []

        # -----------------------------
        # Nom du fichier
        # -----------------------------

        frame = tk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Nom du stock").pack(anchor="w")

        self.nom_stock = tk.Entry(frame)
        self.nom_stock.pack(fill="x")

        # -----------------------------
        # Recherche
        # -----------------------------

        frame = tk.Frame(self)
        frame.pack(fill="both", padx=10, pady=5)

        tk.Label(frame, text="Marchandise").pack(anchor="w")

        self.recherche = tk.Entry(frame)

        self.recherche.pack(fill="x")

        self.recherche.bind("<KeyRelease>", self.filtrer)

        self.liste = tk.Listbox(frame, height=10)

        self.liste.pack(fill="both", expand=True)

        # -----------------------------
        # Tonnage
        # -----------------------------

        frame = tk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Tonnage").pack(anchor="w")

        self.tonnage = tk.Entry(frame)

        self.tonnage.pack(fill="x")

        tk.Button(
            frame,
            text="Ajouter",
            command=self.ajouter
        ).pack(pady=5)

        # -----------------------------
        # Tableau
        # -----------------------------

        self.tree = ttk.Treeview(
            self,
            columns=("nom", "tonnage"),
            show="headings",
            height=10
        )

        self.tree.heading("nom", text="Marchandise")
        self.tree.heading("tonnage", text="Tonnage")

        self.tree.column("nom", width=400)

        self.tree.column("tonnage", width=100)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(
            self,
            text="Enregistrer",
            command=self.enregistrer
        ).pack(pady=10)

        self.toutes_les_marchandises = self.charger_liste()

        self.filtrer()

    # ======================================================

    def charger_liste(self):

        noms = []

        try:

            if hasattr(utils, "MARCHANDISES"):

                df = utils.MARCHANDISES

                if "Nom" in df.columns:
                    noms = sorted(df["Nom"].unique())

                else:
                    noms = sorted(df.iloc[:, 0].unique())

        except Exception:

            pass

        return noms

    # ======================================================

    def filtrer(self, event=None):

        texte = self.recherche.get().lower()

        self.liste.delete(0, tk.END)

        for nom in self.toutes_les_marchandises:

            if texte in nom.lower():

                self.liste.insert(tk.END, nom)

    # ======================================================

    def ajouter(self):

        selection = self.liste.curselection()

        if not selection:
            messagebox.showwarning(
                "Erreur",
                "Sélectionnez une marchandise."
            )
            return

        nom = self.liste.get(selection[0])

        try:
            tonnage = float(self.tonnage.get().replace(",", "."))

        except:

            messagebox.showwarning(
                "Erreur",
                "Tonnage invalide."
            )
            return

        self.stock.append((nom, tonnage))

        self.tree.insert(
            "",
            tk.END,
            values=(nom, tonnage)
        )

        self.tonnage.delete(0, tk.END)

    # ======================================================

    def enregistrer(self):

        nom_stock = self.nom_stock.get().strip()

        if nom_stock == "":

            messagebox.showwarning(
                "Erreur",
                "Nom du stock obligatoire."
            )

            return

        marchandise = Marchandise(nom_stock)

        for nom, tonnage in self.stock:

            marchandise.AjouterMarchandise(
                nom,
                tonnage
            )

        marchandise.sauvegarder()

        messagebox.showinfo(
            "Succès",
            "Stock enregistré."
        )

        self.destroy()