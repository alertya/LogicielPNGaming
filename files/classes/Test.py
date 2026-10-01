import tkinter as tk
from tkinter import ttk

def formulaire():
    root = tk.Tk()
    root.title("Formulaire avec Compétences Spéciales")

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    # Création du premier onglet
    tab1 = tk.Frame(tab_control)
    tab_control.add(tab1, text="Compétences Spéciales")

    CompsSPecial = ['Charpentier', 'Calfat', 'Voilier', 'Chirurgien', 'Pilote', 'Coq', 'Soldat']
    NbComps = ["1", "1", "1", "1", "1", "1", "0"]

    entries = []

    for k in range(len(CompsSPecial)):
        # Création d'une StringVar pour chaque compétence avec valeur par défaut
        var = tk.StringVar(value=NbComps[k])

        # Création d'un label pour le nom de la compétence
        label = tk.Label(tab1, text=CompsSPecial[k])
        label.pack()

        # Création de l'Entry associée à la StringVar
        entry = tk.Entry(tab1, textvariable=var)
        entry.pack()

        # Ajouter la StringVar à la liste entries pour y accéder plus tard
        entries.append(var)

    # Fonction pour récupérer les valeurs et fermer la fenêtre
    def valider():
        for i in range(len(entries)):
            print(f"{CompsSPecial[i]} : {entries[i].get()}")
        root.destroy()

    # Ajouter un bouton pour valider et fermer
    bouton = tk.Button(tab1, text="Valider", command=valider)
    bouton.pack()

    root.mainloop()
# Appeler la fonction pour afficher la fenêtre
formulaire()