import tkinter as tk
from tkinter import ttk, messagebox

import utils
from classes.Marchandise import Marchandise


class PanneauGenerationMarchandise(tk.Frame):

    def __init__(self, parent, moteur=None,on_generer=None):

        super().__init__(parent)

        self.moteur = moteur
        self.on_generer = on_generer
        self.Cargaisons = []
        # -----------------------------
        # Nom du fichier
        # -----------------------------

        frame = tk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Nom du stock").pack(anchor="w")

        self.Name = tk.Entry(frame)
        self.Name.pack(fill="x")

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
        self.tree.bind("<Double-1>", self.modifier)
        tk.Button(
            self,
            text="Supprimer",
            command=self.supprimer
        ).pack()
        self.lblTotal = tk.Label(
            self,
            text="Tonnage : 0"
        )

        self.lblTotal.pack()
        self.toutes_les_marchandises = self.charger_liste()
        self.filtrer()

    # ======================================================

    def charger_liste(self):

        noms = []
        marchandise=utils.MARCHANDISES
        cargaisons=marchandise['Cargaison'].dropna().astype(str).unique().tolist()
        cargaisons_trie=sorted(cargaisons)
        return cargaisons_trie

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

        self.Cargaisons.append((nom, tonnage))

        self.tree.insert(
            "",
            tk.END,
            values=(nom, tonnage)
        )
        self.mettre_a_jour_total()
        self.tonnage.delete(0, tk.END)

    # ======================================================

    def enregistrer(self):

        Name = self.Name.get().strip()
        marchandise = Marchandise(
        )
        marchandise.Name=Name
        if Name == "":

            messagebox.showwarning(
                "Erreur",
                "Nom du stock obligatoire."
            )

            return
        for nom, tonnage in self.Cargaisons:

            marchandise.AjoutMarchandise(marchandise,
                nom,
                tonnage
            )

        marchandise.sauvegarder()

        messagebox.showinfo(
            "Succès",
            "Stock enregistré."
        )

        if self.on_generer:
            self.on_generer(self.Name.get(), self.Cargaisons)

    def modifier(self, event):

        item = self.tree.focus()

        if not item:
            return

        index = self.tree.index(item)

        nom, tonnage = self.Cargaisons[index]

        self.recherche.delete(0, tk.END)
        self.recherche.insert(0, nom)

        self.tonnage.delete(0, tk.END)
        self.tonnage.insert(0, str(tonnage))

        self.Cargaisons.pop(index)

        self.tree.delete(item)

        self.filtrer()

    def supprimer(self):

        item = self.tree.focus()

        if not item:
            return

        index = self.tree.index(item)

        self.Cargaisons.pop(index)

        self.tree.delete(item)

        self.mettre_a_jour_total()
    def mettre_a_jour_total(self):

        total = sum(t for _, t in self.Cargaisons)

        self.lblTotal.config(
            text=f"Tonnage : {total:.1f}"
        )

    def rafraichir_tree(self):

        self.tree.delete(*self.tree.get_children())

        for nom, tonnage in self.Cargaisons:
            self.tree.insert(
                "",
                "end",
                values=(nom, tonnage)
            )

        self.mettre_a_jour_total()