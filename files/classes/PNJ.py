import os
import ast
import random
import numpy as np
import pandas as pd
import utils
import config

class PNJ:

    def __init__(self, Name, Zone,Profession=None, Type=None):

        self.Name = Name
        self.Type = Type
        self.Profession = Profession
        self.Localisation=Zone
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
        self.ScorePNJ()
        self.AttribuerRole()
        self.AjoutTrait()
        self.Save()



    # ================================================================
    # SAUVEGARDE
    # ================================================================

    def Save(self):

        fichier = os.path.join(config.BASE_PATH, "PNJ", f"{self.Name}.csv")




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
        if not os.path.exists(fichier):
            print(f"Le fichier {fichier} n'existe pas.")
            return None
        TempDF = pd.read_csv(
            fichier,
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        if TempDF.empty:
            return None

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
            "Traits": self._format_traits(),
        }


    def get_actions(self):
        return ['LanceCompetence','RecruteMatelot','TrouverMarchand']

    def AjoutTrait(self):
        df = utils.COMPETENCES


            # Initialisation de la liste de traits
        if not hasattr(self, "Traits"):
                self.Traits = []

        for _, ligne in df.iterrows():
            competence = ligne["Competence"]
            trait = ligne["Trait"]
                # Vérifie que le membre possède cette compétence
            if hasattr(self, competence):
                if getattr(self, competence) > 1:
                    if trait not in self.Traits:
                        self.Traits.append(trait)
    def LanceCompetence(self,Competence):
        Comp = getattr(self, Competence)
        return utils.Test(Comp, 0)
    def executer_action(self, action, instance,valeurs=None):

        if action=="RecruteMatelot":
            return self.RecruteMatelot(valeurs['TaillePort'],valeurs['Succes'],valeurs['Equipage'],valeurs['Type'])
        if action=='TrouverMarchand':
            pnj=PNJ.charger_depuis_csv(instance)
            return pnj.TrouverMarchand(valeurs["Nom"],valeurs['Zone'])
        if action == "LanceCompetence":
            pnj = PNJ.charger_depuis_csv(instance)
            Result=pnj.LanceCompetence(valeurs['Competence'])

            pnj.Save()

            return f"{pnj.Name} a effectue un test de {valeurs['Competence']} et a obtenu {Result} succes"

        return "Action inconnue."

    def get_actions(self):
        return ["LanceCompetence"]

    def _format_traits(self):

        if not self.Traits:
            return ""

        lignes = []

        for i in range(0, len(self.Traits), 4):
            lignes.append(", ".join(self.Traits[i:i + 4]))

        return "\n".join(lignes)

    def ScorePNJ(self):
        """Calcule le score moyen du PNJ."""

        exclusions = {
            "Name", "Profession", "Type", "Localisation",
            "Traits", "Score", "PV", "PVMax"
        }

        scores = []

        for attribut, valeur in vars(self).items():
            if attribut not in exclusions and isinstance(valeur, (int, float)):
                scores.append(valeur)

        self.Score = sum(scores) / len(scores) if scores else 0

        return self

    def AttribuerRole(self):

        roles = utils.ROLES

        self.Role = ""

        for _, row in roles.iterrows():

            competence = row["Competence"]
            seuil = row["Seuil"]
            role = row["Role"]

            if getattr(self, competence, 0) >= seuil:
                self.Role = role
                break

        return self

    def TrouverMarchand(self,Name,Localisation):
        Liste=["RicheMarchand","PetitMarchand"]
        ##On choisiit au hasard si c'est un petit ou riche marchand
        choix = random.choice(Liste)
        pnj=PNJ(Name,Localisation,Type=None,Profession=choix)
        SuccesCommerce=utils.Test(pnj.Commerce)
        pnj.Fortune=self.CalculFortune(SuccesCommerce,0,0)
        pnj.Save()
        return f"Vous avez trouver {Name} en {Localisation} avec une capacité d'achat de {pnj.Fortune}"
    def RecruteMatelot(self,Tailleport,SuccesRecrute,Equipage,Type):
        equipage=Equipage.charger_depuis_csv(Equipage)
        ###Si la taille du port est de 1 c'est 1d60 hommes disponibles, si c'est deux 2d60 et 3 3d60
        ###Attention ces valeurs sont pour des matelots trouvés en taverne
        NbHommes=random.randint(1,60)
        if Tailleport>1:
            NbHommes += random.randint(1, 60)
        if Tailleport>2:
            NbHommes += random.randint(1, 60)

        NbHommesRecrute=int(NbHommes*SuccesRecrute/10)
        equipage.Recrute(NbHommesRecrute,Type,)
        return f"Vous avez recrute {NbHommesRecrute} {Type} a l'équipage {Equipage}"
    def CalculFortune(self,SuccesCommerce,NbCanons=0,Tonnage=0):
        Bonus=random.randint(1,100)
        Bonus+=SuccesCommerce
        Bonus+=NbCanons
        Bonus+=Tonnage/10
        Bonus += random.randint(1, 100)
        ValeurRancon=utils.VALEUR_RANCON
        Fortune=ValeurRancon[ValeurRancon['Text']>=Bonus].iloc[0]

        return Fortune