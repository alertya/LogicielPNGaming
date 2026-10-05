import os
import ast
import random
import numpy as np
import pandas as pd
import utils
import config

class PNJ:

    def __init__(self, Name, Profession=None, Type=None):

        self.Name = Name
        self.Type = Type
        self.Profession = Profession
        self.Localisation="Europe du Nord"
        # ------------------------------------------------------------
        # Recherche du profil professionnel
        # ------------------------------------------------------------

        Pond = utils.PROFESSIONS
        Pond2 = utils.LISTE_METIER_PROF

        Ponds = Pond[Pond["Type"] == Type]

        if Ponds.empty:
            Ponds = Pond2[Pond2["TypeProfession"] == Type]

        if Ponds.empty:
            raise ValueError(
                f"Aucun profil professionnel trouvé pour le type : {Type}"
            )

        donnees = Ponds.iloc[0].to_dict()

        # ------------------------------------------------------------
        # Génération des compétences
        # ------------------------------------------------------------

        for column in Pond.columns[1:71]:

            if column not in ["Salaire", "Employeur"]:

                donnees[column] = utils.Compute(
                    Ponds[column].iloc[0]
                )

        # ------------------------------------------------------------
        # Armes blanches
        # ------------------------------------------------------------

        donnees["ArmesBlanches"] = max(
            donnees["Dague"],
            donnees["Hache"],
            donnees["Sabre"]
        )

        # ------------------------------------------------------------
        # Ajout des données professionnelles au PNJ
        # ------------------------------------------------------------

        for attribut, valeur in donnees.items():
            setattr(self, attribut, valeur)

        # ------------------------------------------------------------
        # Attributs propres au PNJ
        # ------------------------------------------------------------

        self.Nom = Name
        self.Maladie = ""
        self.Moral = 2

        self.Attitude = int(
            np.random.normal(50, 5)
        )

        self.Groupe = ""
        self.Role = ""
        self.Pirate = 1
        self.KillCount = 0
        self.LastSuccess = 0
        self.Famine = 0

        self.PVMax = random.randint(5, 8)
        self.PV = self.PVMax

        self.Traits = []
        self.Save()



    # ================================================================
    # SAUVEGARDE
    # ================================================================

    def Save(self):

        dossier = config.BASE_PATH + "/PNJ"

        os.makedirs(
            dossier,
            exist_ok=True
        )

        fichier = dossier + "/" + self.Name + ".csv"

        TempDF = pd.DataFrame([
            vars(self)
        ])

        TempDF.to_csv(
            fichier,
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )

        return fichier

    # ================================================================
    # CHARGEMENT DEPUIS UN CSV
    # ================================================================

    @classmethod
    def charger_depuis_csv(cls, Name):
        fichier = os.path.join(config.BASE_PATH, "PNJ", f"{Name}.csv")
        TempDF = pd.read_csv(
            fichier,
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        if TempDF.empty:
            raise ValueError(
                f"Le fichier PNJ est vide : {fichier}"
            )

        donnees = TempDF.iloc[0].to_dict()

        # ------------------------------------------------------------
        # Conversion des colonnes numériques
        # ------------------------------------------------------------

        for cle, valeur in donnees.items():

            if pd.isna(valeur):
                donnees[cle] = None

        # ------------------------------------------------------------
        # Création de l'objet sans relancer la génération aléatoire
        # ------------------------------------------------------------

        pnj = cls.__new__(cls)

        # On restaure directement tous les attributs
        for attribut, valeur in donnees.items():
            setattr(pnj, attribut, valeur)

        # ------------------------------------------------------------
        # Restauration des listes
        # ------------------------------------------------------------

        if isinstance(pnj.Traits, str):

            try:
                pnj.Traits = ast.literal_eval(pnj.Traits)

            except (ValueError, SyntaxError):
                pnj.Traits = []

        return pnj


    def Affichage(self):

        return {
            "Nom": self.Name,
            "Profession": self.Profession,
            "Type": self.Type,
            "Localisation": self.Localisation,
            "Traits": self.Traits,
        }




