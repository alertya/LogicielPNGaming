"""
app.py
------
Interface graphique "jeu vidéo de gestion" :

  - Colonne de gauche : onglets VERTICAUX (Journal de bord, Navire, Equipage,
    Marchandises, Escale, Infirmerie, Reset).
  - Barre du haut : onglets HORIZONTAUX propres à l'onglet vertical courant
    (Afficher / Générer / Recruter / Vendre-Acheter / Actions...).
  - Sous la barre horizontale : une liste déroulante pour choisir l'INSTANCE
    à afficher (un navire, un membre d'équipage, etc.), fournie par le moteur.
  - Zone centrale : affichage automatique des données renvoyées par le moteur.
  - Zone du bas : boutons d'action, également fournis par le moteur.

Ce fichier ne contient AUCUNE logique de jeu : il ne fait qu'appeler les
méthodes de `moteur_interface.MoteurBase`. Pour brancher ton propre moteur de
calcul, il suffit de fournir un objet héritant de MoteurBase à l'App -- voir
main.py.
"""

from __future__ import annotations

import tkinter as tk

from tkinter import ttk
from classes.FormulaireRencontre import FormulaireRencontre
from typing import Dict, List, Optional

import theme

from moteur_interface import MoteurBase

from panneau_generation import PanneauGenerationTrajet

from panneau_generation_equipage import PanneauGenerationEquipage

from panneau_generation_navire import PanneauGenerationNavire

from panneau_generation_pnj import PanneauGenerationPNJ

from formulaire_action import FormulaireAction
# ---------------------------------------------------------------------------
# Structure des onglets, dérivée du fichier Excel fourni.
# Clé   = onglet vertical
# Valeur = liste des onglets horizontaux
# ---------------------------------------------------------------------------
ONGLETS: Dict[str, List[str]] = {
    "Journal de bord": ["Journal", "Générer"],
    "Navire": ["Afficher", "Générer", "Actions"],
    "Equipage": ["Afficher", "Générer", "Recruter", "Actions"],
    "Marchandises": ["Afficher", "Générer", "Actions"],
    "Escale": ["Afficher", "Générer", "Actions"],
    "PNJ": ["Afficher", "Générer", "Actions"],
    "Infirmerie": ["Afficher", "Actions"],
    "Reset": ["Actions"],
}

# Onglets (onglet_vertical, onglet_horizontal) qui utilisent un panneau
# entièrement personnalisé plutôt que le rendu générique dropdown/tableau.
# Le nom pointe vers une méthode de App à appeler pour construire ce panneau.
PANNEAUX_SPECIAUX: Dict[tuple, str] = {
    ("Journal de bord", "Générer"): "_construire_panneau_generation",
    ("Equipage", "Générer"): "_construire_panneau_generation_equipage",
    ("Navire", "Générer"): "_construire_panneau_generation_navire",
    ("PNJ", "Générer"): "_construire_panneau_generation_PNJ",
}


class App(tk.Tk):
    def __init__(self, moteur: MoteurBase):
        super().__init__()
        self.moteur = moteur

        self.title("Compagnie des Mers — Gestion")
        self.geometry("1100x680")
        self.minsize(880, 560)
        self.configure(bg=theme.BG_ROOT)

        self.onglet_actuel: str = next(iter(ONGLETS))
        self.sous_onglet_actuel: Optional[str] = None
        self.instance_actuelle: Optional[str] = None

        self._boutons_verticaux: Dict[str, tk.Button] = {}
        self._boutons_horizontaux: Dict[str, tk.Button] = {}

        self._construire_layout()
        self.selectionner_onglet(self.onglet_actuel)

    # ------------------------------------------------------------------ #
    # Construction du squelette de la fenêtre
    # ------------------------------------------------------------------ #
    def _construire_layout(self):
        # --- Colonne de gauche : onglets verticaux -------------------------
        self.sidebar = tk.Frame(self, bg=theme.BG_SIDEBAR, width=theme.SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        titre = tk.Label(
            self.sidebar, text="⚓ Compagnie", bg=theme.BG_SIDEBAR,
            fg=theme.FG_TITLE, font=theme.FONT_TITLE, pady=18,
        )
        titre.pack(fill="x")

        for nom in ONGLETS:
            btn = tk.Button(
                self.sidebar, text=nom, anchor="w", padx=18, pady=10,
                font=theme.FONT_TAB_V, relief="flat", bd=0, cursor="hand2",
                bg=theme.TAB_IDLE_BG, fg=theme.TAB_IDLE_FG,
                activebackground=theme.TAB_SELECTED_BG,
                activeforeground=theme.TAB_SELECTED_FG,
                command=lambda n=nom: self.selectionner_onglet(n),
            )
            btn.pack(fill="x")
            self._boutons_verticaux[nom] = btn

        # --- Colonne de droite : tout le reste -------------------------------
        self.zone_droite = tk.Frame(self, bg=theme.BG_ROOT)
        self.zone_droite.pack(side="left", fill="both", expand=True)

        # Barre d'onglets horizontaux
        self.topbar = tk.Frame(self.zone_droite, bg=theme.BG_TOPBAR, height=theme.TOPBAR_HEIGHT)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        # Barre de sélection d'instance (dropdown)
        self.instance_bar = tk.Frame(self.zone_droite, bg=theme.BG_ROOT, height=theme.INSTANCE_BAR_HEIGHT)
        self.instance_bar.pack(fill="x")
        self.instance_bar.pack_propagate(False)

        tk.Label(
            self.instance_bar, text="Instance :", bg=theme.BG_ROOT,
            fg=theme.FG_MUTED, font=theme.FONT_TEXT_BOLD,
        ).pack(side="left", padx=(16, 8))

        self._style_combobox()
        self.combo_instance = ttk.Combobox(
            self.instance_bar, state="readonly", font=theme.FONT_TEXT,
            style="Jeu.TCombobox", width=32,
        )
        self.combo_instance.pack(side="left", pady=8)
        self.combo_instance.bind("<<ComboboxSelected>>", self._on_instance_change)

        tk.Button(
            self.instance_bar, text="⟳ Rafraîchir", font=theme.FONT_TEXT,
            bg=theme.BG_INPUT, fg=theme.FG_TEXT, relief="flat", cursor="hand2",
            activebackground=theme.ACCENT, padx=10,
            command=self.rafraichir_instances,
        ).pack(side="left", padx=10)

        # Zone de contenu (scrollable)
        self._construire_zone_contenu()

        # Barre d'actions (boutons dynamiques en bas)
        self.action_bar = tk.Frame(self.zone_droite, bg=theme.BG_PANEL)
        self.action_bar.pack(fill="x", side="bottom")

        # Barre de statut (messages de retour du moteur)
        self.statut_var = tk.StringVar(value="Prêt.")
        self.statut = tk.Label(
            self.zone_droite, textvariable=self.statut_var, anchor="w",
            bg=theme.BG_ROOT, fg=theme.FG_MUTED, font=theme.FONT_TEXT, padx=16, pady=4,
        )
        self.statut.pack(fill="x", side="bottom")

    def _style_combobox(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Jeu.TCombobox",
            fieldbackground=theme.BG_INPUT,
            background=theme.BG_INPUT,
            foreground=theme.FG_TEXT,
            arrowcolor=theme.ACCENT,
            bordercolor=theme.BORDER,
        )

    def _construire_zone_contenu(self):
        conteneur = tk.Frame(self.zone_droite, bg=theme.BG_ROOT)
        conteneur.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(conteneur, bg=theme.BG_ROOT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(conteneur, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=16, pady=12)
        scrollbar.pack(side="right", fill="y")

        self.panneau_contenu = tk.Frame(self.canvas, bg=theme.BG_ROOT)
        self._fenetre_id = self.canvas.create_window((0, 0), window=self.panneau_contenu, anchor="nw")

        self.panneau_contenu.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfig(self._fenetre_id, width=e.width)
        )

    # ------------------------------------------------------------------ #
    # Navigation entre onglets
    # ------------------------------------------------------------------ #
    def selectionner_onglet(self, nom: str):
        self.onglet_actuel = nom
        for n, btn in self._boutons_verticaux.items():
            selectionne = n == nom
            btn.configure(
                bg=theme.TAB_SELECTED_BG if selectionne else theme.TAB_IDLE_BG,
                fg=theme.TAB_SELECTED_FG if selectionne else theme.TAB_IDLE_FG,
            )

        self._construire_onglets_horizontaux()
        sous_onglets = ONGLETS[nom]
        premier_sous_onglet = sous_onglets[0] if sous_onglets else None
        self.selectionner_sous_onglet(premier_sous_onglet)

    def _construire_onglets_horizontaux(self):
        for w in self.topbar.winfo_children():
            w.destroy()
        self._boutons_horizontaux.clear()

        sous_onglets = ONGLETS[self.onglet_actuel]
        if not sous_onglets:
            tk.Label(
                self.topbar, text=self.onglet_actuel, bg=theme.BG_TOPBAR,
                fg=theme.FG_TITLE, font=theme.FONT_SECTION, padx=16,
            ).pack(side="left", fill="y")
            return

        for nom in sous_onglets:
            btn = tk.Button(
                self.topbar, text=nom, font=theme.FONT_TAB_H, relief="flat",
                bd=0, cursor="hand2", padx=16, bg=theme.BG_TOPBAR, fg=theme.TAB_IDLE_FG,
                activebackground=theme.TAB_SELECTED_BG, activeforeground=theme.TAB_SELECTED_FG,
                command=lambda n=nom: self.selectionner_sous_onglet(n),
            )
            btn.pack(side="left", fill="y")
            self._boutons_horizontaux[nom] = btn

    def selectionner_sous_onglet(self, nom: Optional[str]):
        self.sous_onglet_actuel = nom
        for n, btn in self._boutons_horizontaux.items():
            selectionne = n == nom
            btn.configure(
                bg=theme.TAB_SELECTED_BG if selectionne else theme.BG_TOPBAR,
                fg=theme.TAB_SELECTED_FG if selectionne else theme.TAB_IDLE_FG,
            )
        self.rafraichir_instances()

    # ------------------------------------------------------------------ #
    # Gestion de la liste déroulante d'instances
    # ------------------------------------------------------------------ #
    def rafraichir_instances(self):
        cle = (self.onglet_actuel, self.sous_onglet_actuel)
        if cle in PANNEAUX_SPECIAUX:
            self.instance_bar.pack_forget()
            self.action_bar.pack_forget()
            getattr(self, PANNEAUX_SPECIAUX[cle])()
            return

        instances = self.moteur.get_instances(self.onglet_actuel, self.sous_onglet_actuel) or []
        self.combo_instance["values"] = instances

        if instances:
            self.instance_bar.pack(fill="x")
            if self.instance_actuelle not in instances:
                self.instance_actuelle = instances[0]
            self.combo_instance.set(self.instance_actuelle)
        else:
            self.instance_actuelle = None
            self.combo_instance.set("")
            # Onglet sans instance (ex: Journal de bord, Reset) : on masque la barre
            self.instance_bar.pack_forget()

        self.rafraichir_contenu()

    def _on_instance_change(self, _event=None):
        self.instance_actuelle = self.combo_instance.get()
        self.rafraichir_contenu()

    # ------------------------------------------------------------------ #
    # Rendu du contenu + des actions, à partir des données du moteur
    # ------------------------------------------------------------------ #
    def rafraichir_contenu(self):
        for w in self.panneau_contenu.winfo_children():
            w.destroy()

        if self.sous_onglet_actuel == "Afficher":
            donnees = self.moteur.get_affichage(
                self.onglet_actuel,
                self.instance_actuelle
            )
        else:
            donnees = self.moteur.get_donnees(
                self.onglet_actuel,
                self.sous_onglet_actuel,
                self.instance_actuelle
            )
        self._afficher_donnees(donnees)
        self._construire_barre_actions()

    def _afficher_donnees(self, donnees):
        parent = self.panneau_contenu

        if donnees is None:
            self._label_info(parent, "Aucune donnée à afficher.")
            return

        if isinstance(donnees, str):
            self._afficher_texte(parent, [donnees])
            return

        if isinstance(donnees, list) and (len(donnees) == 0 or isinstance(donnees[0], str)):
            self._afficher_texte(parent, donnees)
            return

        if isinstance(donnees, dict):

            # Nouveau format d'affichage
            if all(isinstance(v, dict) and "type" in v for v in donnees.values()):
                self._afficher_blocs(parent, donnees)
            else:
                # Ancien format
                self._afficher_fiche(parent, donnees)
            return

        if isinstance(donnees, list) and isinstance(donnees[0], dict):
            self._afficher_tableau(parent, donnees)
            return

        # Type non reconnu : affichage brut de secours
        self._label_info(parent, str(donnees))

    def _label_info(self, parent, texte):
        tk.Label(
            parent, text=texte, bg=theme.BG_ROOT, fg=theme.FG_MUTED,
            font=theme.FONT_TEXT, justify="left", anchor="w",
        ).pack(fill="x", padx=4, pady=20)

    def _afficher_texte(self, parent, lignes: List[str]):
        cadre = tk.Frame(parent, bg=theme.BG_PANEL, padx=16, pady=14)
        cadre.pack(fill="x", pady=4)
        if not lignes:
            self._label_info(cadre, "(vide)")
            return
        for ligne in lignes:
            tk.Label(
                cadre, text=f"•  {ligne}", bg=theme.BG_PANEL, fg=theme.FG_TEXT,
                font=theme.FONT_TEXT, justify="left", anchor="w", wraplength=760,
            ).pack(fill="x", pady=3)

    def _afficher_fiche(self, parent, donnees: Dict):
        cadre = tk.Frame(parent, bg=theme.BG_PANEL, padx=16, pady=14)
        cadre.pack(fill="x", pady=4)
        if not donnees:
            self._label_info(cadre, "(aucune donnée)")
            return
        for i, (cle, valeur) in enumerate(donnees.items()):
            ligne = tk.Frame(cadre, bg=theme.BG_PANEL)
            ligne.pack(fill="x", pady=4)
            tk.Label(
                ligne, text=str(cle), bg=theme.BG_PANEL, fg=theme.FG_MUTED,
                font=theme.FONT_TEXT_BOLD, width=22, anchor="w",
            ).pack(side="left")
            tk.Label(
                ligne, text=str(valeur), bg=theme.BG_PANEL, fg=theme.FG_TEXT,
                font=theme.FONT_TEXT, anchor="w",
            ).pack(side="left")
        if (self.onglet_actuel == "Journal de bord"
                and self.sous_onglet_actuel == "Journal"):
            tk.Button(
                cadre,
                text="Jour suivant",
                command=self._jour_suivant,
                bg=theme.ACCENT,
                fg="black"
            ).pack(pady=10)

    def _afficher_tableau(self, parent, lignes, colonnes=None):
        print("AFFICHER TABLEAU",
              self.onglet_actuel,
              self.sous_onglet_actuel)
        if not lignes:
            return
        print(self.onglet_actuel)
        print(self.sous_onglet_actuel)
        if colonnes is None:
            colonnes = list(lignes[0].keys())

        cadre = tk.Frame(parent, bg=theme.BG_PANEL, padx=12, pady=12)
        cadre.pack(fill="both", expand=True, pady=4)

        table = ttk.Treeview(
            cadre,
            columns=colonnes,
            show="headings",
            height=min(12, len(lignes))
        )

        for col in colonnes:
            table.heading(col, text=col)
            table.column(col, width=140, anchor="center")

        for ligne in lignes:
            if isinstance(ligne, dict):
                valeurs = [ligne.get(c, "") for c in colonnes]
            else:
                # Cas où ligne est un tuple ou une liste
                valeurs = ligne

            table.insert("", "end", values=valeurs)

        table.pack(fill="both", expand=True)
        # Bouton spécifique au Journal de bord
        if (self.onglet_actuel == "Journal de bord"
                and self.sous_onglet_actuel == "Journal"):
            tk.Button(
                cadre,
                text="Jour suivant",
                command=self._jour_suivant,
                bg=theme.ACCENT,
                fg="black"
            ).pack(pady=10)

    def _construire_barre_actions(self):
        for w in self.action_bar.winfo_children():
            w.destroy()

        actions = self.moteur.get_actions(
            self.onglet_actuel, self.sous_onglet_actuel, self.instance_actuelle
        ) or []
        if not actions:
            self.action_bar.pack_forget()
            return

        self.action_bar.pack(fill="x", side="bottom", before=self.statut)
        conteneur = tk.Frame(self.action_bar, bg=theme.BG_PANEL, pady=10, padx=16)
        conteneur.pack(fill="x")

        for nom_action in actions:
            tk.Button(
                conteneur, text=nom_action, font=theme.FONT_TEXT_BOLD,
                bg=theme.ACCENT, fg="#231a08", relief="flat", padx=18, pady=6,
                activebackground=theme.ACCENT_HOVER, cursor="hand2",
                command=lambda a=nom_action: self._executer_action(a),
            ).pack(side="left", padx=(0, 10))

    def _executer_action(self, action):

        if action in (
                "Vendre", "Acheter", "Piller", "Recruter",
                "Generer", "BatailleTerrestre", "RecruterType",
                "CombatNaval", "Reparer", "Poursuivre","Commercer","Fuir","Poursuivre","Canonner","PavillonNoir","LanceCompetence"
        ):
            FormulaireAction(
                self,
                action=action,
                moteur=self.moteur,
                on_valider=self._valider_formulaire
            )
            return

        resultat = self.moteur.executer_action(
            self.onglet_actuel,
            self.sous_onglet_actuel,
            self.instance_actuelle,
            action
        )
        print(action)
        print(type(resultat))
        print(resultat)
        if action == "JourSuivant" and isinstance(resultat, dict):
            self.afficher_texte(resultat["journal"])
            print("Action:JourSuivant")
            if resultat.get("rencontre"):
                print("Execution")
                FormulaireRencontre(
                    self,
                    moteur=self.moteur,
                    instance=self.instance_actuelle
                )

            if resultat["navire_rencontre"] is not None:
                print("ExecutionResultat")
                FormulaireRencontre(
                    self,
                    moteur=self.moteur,
                    navire=resultat["navire_rencontre"].Name
                )

        if isinstance(resultat, dict):
            self.statut_var.set(resultat["journal"])
        else:
            self.statut_var.set(resultat)
        self.rafraichir_instances()

    # ------------------------------------------------------------------ #
    # Panneau spécial : Journal de bord -> Générer
    # ------------------------------------------------------------------ #
    def _construire_panneau_generation(self):
        for w in self.panneau_contenu.winfo_children():
            w.destroy()

        navires = self.moteur.get_navires()
        panneau = PanneauGenerationTrajet(self.panneau_contenu, navires, on_creer=self._creer_trajet)
        panneau.pack(fill="both", expand=True)

    def _creer_trajet(self, nom_trajet: str, navire: str, annee: int, etapes: List[Dict]):
        message = self.moteur.creer_trajet(
            nom_trajet,
            navire,
            annee,
            etapes
        )

        self.statut_var.set(message or "Trajet créé.")

        # On bascule sur le journal du navire concerné
        self.instance_actuelle = navire
        self.selectionner_sous_onglet("Journal")

    # ------------------------------------------------------------------ #
    # Panneau spécial : Equipage -> Générer
    # ------------------------------------------------------------------ #
    def _construire_panneau_generation_equipage(self):
        for w in self.panneau_contenu.winfo_children():
            w.destroy()

        types_equipage = self.moteur.get_types_equipage()
        panneau = PanneauGenerationEquipage(self.panneau_contenu, types_equipage, on_generer=self._generer_equipage)
        panneau.pack(fill="both", expand=True)

    def _generer_equipage(self, nom: str, type_equipage: str, nombre: int, effectifs: Dict[str, int]):
        message = self.moteur.generer_equipage(nom, type_equipage, nombre, effectifs)
        self.statut_var.set(message or "Équipage généré.")
        # On bascule sur "Afficher" pour montrer immédiatement l'équipage généré.
        self.instance_actuelle = nom
        self.selectionner_sous_onglet("Afficher")

    # ------------------------------------------------------------------ #
    # Panneau spécial : PNJ -> Générer
    # ------------------------------------------------------------------ #
    def _construire_panneau_generation_PNJ(self):
        for w in self.panneau_contenu.winfo_children():
            w.destroy()

        # Récupération des données depuis le moteur
        zones_commerciales = self.moteur.get_zones_commerciales()
        metiers = self.moteur.get_metiers()
        types_pnj = self.moteur.get_types_pnj()

        panneau = PanneauGenerationPNJ(
            self.panneau_contenu,
            zones_commerciales=zones_commerciales,
            metiers=metiers,
            types_pnj=types_pnj,
            on_generer=self._generer_pnj
        )

        panneau.pack(
            fill="both",
            expand=True
        )

    def _generer_pnj(self, nom: str, zone, metier: str, type_pnj: str):

        message = self.moteur.generer_pnj(
            nom,
            zone,
            metier,
            type_pnj
        )

        self.statut_var.set(
            message or "PNJ généré."
        )

        # On bascule sur "Afficher"
        self.instance_actuelle = nom
        self.selectionner_sous_onglet("Afficher")


    # ------------------------------------------------------------------ #
    # Panneau spécial : Navire -> Générer
    # ------------------------------------------------------------------ #
    def _construire_panneau_generation_navire(self):
        for w in self.panneau_contenu.winfo_children():
            w.destroy()

        types_navire = self.moteur.get_types_navire()
        regions = self.moteur.get_regions_navire()
        panneau = PanneauGenerationNavire(self.panneau_contenu, types_navire, regions, on_generer=self._generer_navire)
        panneau.pack(fill="both", expand=True)

    def _generer_navire(self, nom: str, type_navire: str, region: str):
        message = self.moteur.generer_navire(nom, type_navire, region)
        self.statut_var.set(message or "Navire généré.")
        # On bascule sur "Afficher" pour montrer immédiatement le navire généré.
        self.instance_actuelle = nom
        self.selectionner_sous_onglet("Afficher")

    def _valider_formulaire(self, action, valeurs):

        message = self.moteur.executer_action(
            self.onglet_actuel,
            self.sous_onglet_actuel,
            self.instance_actuelle,
            action,
            valeurs
        )

        self.statut_var.set(message)
        self.rafraichir_instances()

    def _bataille_terrestre(self, nomAllie: str, nomAdverse: str, CompAllie: str,CompAdverse: str, BonusAllie: int,BonusAdverse:int):
        message = self.moteur.BatailleTerrestre(nomAllie, nomAdverse, CompAllie, CompAdverse,BonusAllie,BonusAdverse)
        self.statut_var.set(message or "Équipage généré.")
        # On bascule sur "Afficher" pour montrer immédiatement l'équipage généré.
        self.selectionner_sous_onglet("Actions")
    def _Recrute(self, Nb, Type, Bonus):

        Pond = pd.read_csv(
            BASE_PATH + "/ListeProf.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        Ponds = Pond[Pond["Type"] == Type]

        Temp = ""

        for _ in range(Nb):

            donnees = Ponds.iloc[0].to_dict()

            # Génération des compétences
            for k in Ponds.columns[1:71]:

                if k not in ["Salaire", "Employeur"]:
                    donnees[k] = utils.Compute(Ponds[k].iloc[0])

            # Armes blanches
            donnees["ArmesBlanches"] = max(
                donnees["Dague"],
                donnees["Hache"],
                donnees["Sabre"]
            )

            # Attributs propres au membre
            donnees["Nom"] = ""
            donnees["Maladie"] = ""
            donnees["Moral"] = 2
            donnees["Groupe"] = ""
            donnees["Pirate"] = 1
            donnees["Score"] = 0
            donnees["Role"] = ""
            donnees["Famine"] = 0
            donnees["KillCount"] = 0
            donnees["LastSuccess"] = 0

            donnees["Attitude"] = int(
                np.random.normal(50, 5)
            )

            # Création du membre
            membre = type("Membre", (), {})()

            for attribut, valeur in donnees.items():
                setattr(membre, attribut, valeur)
            # Initialisation des PV
            membre.PVMax = random.randint(5, 8)
            membre.PV = membre.PVMax
            # Calculs individuels
            self.ScoreMembre(membre)
            self.AttributeGroupeMembre(membre)

            self.Membres.append(membre)
            self.AjoutTrait()
        self.ValeurCombat = self.CalculCombatEquipage()

        return Temp
    def _CombatNaval(self,navire1, munition1,bonus1, navire2, munition2,bonus2):

        texte = ""

        degat1, recharge1 = self.DegatsNavire(
            navire1,
            navire2,
            munition1,bonus1
        )

        degat2, recharge2 = self.DegatsNavire(
            navire2,
            navire1,
            munition2,bonus2
        )

        texte += (
            f"{navire1.Name} a besoin de {recharge1} tours "
            "pour recharger sa prochaine batterie.\n"
        )

        texte += (
            f"{navire2.Name} a besoin de {recharge2} tours "
            "pour recharger sa prochaine batterie.\n"
        )

        print(f"{navire1.Name} a besoin de {recharge1} tours pour recharger.")
        print(f"{navire2.Name} a besoin de {recharge2} tours pour recharger.")

        # Le navire 1 subit les dégâts du navire 2
        if navire1.Equipage.Nombre > 0:

            perte1, temp = self.PerteNavire(
                navire1,
                degat2,
                munition2
            )

            texte += temp + "\n"

            texte += navire1.Equipage.Attitude(
                -perte1 / navire1.Equipage.Nombre * 50
            )[1]

        else:

            texte += f"{navire1.Name} a été décimé.\n"

        # Le navire 2 subit les dégâts du navire 1
        if navire2.Equipage.Nombre > 0:

            perte2, temp = self.PerteNavire(
                navire2,
                degat1,
                munition1
            )

            texte += temp + "\n"

            texte += navire2.Equipage.Attitude(
                -perte2 / navire2.Equipage.Nombre * 50
            )[1]

        else:

            texte += f"{navire2.Name} a été décimé.\n"

        print(f"{navire1.Name} a perdu {perte1} hommes")
        print(f"{navire2.Name} a perdu {perte2} hommes")

        return texte

    def _Reparer(self):
        ReparationCoque=self.StructureCoque/self.StructureCoqueMax
        ReparationVoile=self.StructureVoile/self.StructureVoileMax
        CoutReparation=self.CoutSansCanon*(ReparationVoile+ReparationCoque)/2
        self.StructureVoile=self.StructureVoileMax
        self.StructureCoque=self.StructureCoqueMax
        CompCharpentier=utils.Compute(1)
        TempsEnJourReparation=utils.TestValeurNonNumerique(CompCharpentier,0)[0]
        return CoutReparation,TempsEnJourReparation

    def _afficher_blocs(self, parent, blocs):

        for titre, bloc in blocs.items():

            cadre = tk.LabelFrame(
                parent,
                text=titre,
                padx=10,
                pady=10
            )
            cadre.pack(fill="x", padx=10, pady=10)

            if bloc["type"] == "tableau":
                self._afficher_tableau(
                    cadre,
                    bloc["donnees"]
                )

            elif bloc["type"] == "formulaire":
                self._afficher_fiche(
                    cadre,
                    bloc["donnees"]
                )

    def _jour_suivant(self):


        resultat = self.moteur.executer_action(
                "Journal de bord",
                "Journal",
                self.instance_actuelle,
                "JourSuivant"
            )

        print(resultat)
        print(type(resultat))

        if resultat.get("navire_rencontre"):
            FormulaireRencontre(
                self,
                moteur=self.moteur,
                voyage=self.instance_actuelle,
                navire=resultat["navire_rencontre"]
            )
    def _ouvrir_rencontre(self):
        FormulaireRencontre(
            self,
            moteur=self.moteur,
            voyage=self.instance_actuelle,
            navire=resultat["navire_rencontre"]
        )
    def _action_rencontre(self, action):

        message = self.moteur.executer_action(
            self.onglet_actuel,
            self.sous_onglet_actuel,
            self.instance_actuelle,
            action
        )

        self.statut_var.set(message)
        self.rafraichir_contenu()