# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:05:00 2023

@author: USER
"""

import math
import os
import random
import csv
import numpy as np
import pandas as pd
from typing import Dict, List
from .Equipage import Equipage
from .Marchandise import Marchandise
import utils
import config

##### Variables & Constantes voyage
NbJour = 6
CompetenceVigie = 2

Nb = 182
Nbsss = 2
Superficie = 106460000 / 2
NbDaysOfCyclone = 59
NbDaysOfTempest = 27
Surface = np.pi * 750 * 750

SeuilMa = 4
DeMa = 20
SeuilAv = 4
DeAv = 40

Munitions = ['Boulets', 'Rames', 'Mitraille']
Proba = round(Superficie / Surface * 182 / 59)

BASE_PATH = "."  # À adapter selon l'emplacement de vos fichiers CSV


class Navire:
    from typing import Dict, List

    def __init__(self, Type="Sloop", Name="Test",Region="Brésil",charger=False):
                # -------------------------
                # Paramètres requis à la création
                # -------------------------
                self.type_navire: str = Type  # Représente 'Bateau' ou 'CategorieNavire' du CSV
                self.Name: str = Name  # Représente 'Nom' dans le CSV

                # -------------------------
                # Rencontre & Origine
                # -------------------------
                self.de_depart: int = 0
                self.regions_depart: str = Region

                self.Compagnie: str = ""

                # -------------------------
                # Identification & Catégorie
                # -------------------------
                self.separation: str = ""
                self.CategorieNavire: int = 0
                self.pirate: bool = False  # Géré en booléen (True pour 'O', False pour 'N')
                self.Nationalite="E"

                # -------------------------
                # Dimensions & Structure
                # -------------------------
                self.Longueur: int = 0
                self.NbMats: int = 0
                self.Hauturier: str = ""
                self.StructureCoque: float = 0.0
                self.StructureVoile: float = 0.0

                # -------------------------
                # Équipage & Compétences
                # -------------------------
                self.EquipMin: int = 0
                self.EquipMax: int = 0
                self.EquipageNom: str = ""

                self.combat: int = 0
                self.manoeuvre: int = 0
                self.pointage: int = 0
                self.recharge: int = 0
                self.ruse: int = 0
                self.valeur_combat: float = 0.0

                # -------------------------
                # Navigation & Allures
                # -------------------------
                self.allure: str = ""
                self.VitesseMoyenne: float = 0.0
                self.Pres: float = 0.0
                self.Largue: float = 0.0
                self.GrandLargue: float = 0.0
                self.VentArriere: float = 0.0

                # -------------------------
                # Combat & Armement
                # -------------------------
                self.NbCanons: int = 0
                self.homme_combat: int = 0
                self.ValeurCanonnade: float = 0.0

                # -------------------------
                # Économie & Cargaison
                # -------------------------
                self.TonnageMin: int = 0
                self.TonnageMax: int = 0

                self.remplissage: int = 0
                self.poids_total_marchandise: float = 0.0
                #Prxi d'achat
                self.CoutSansCanon:float=0.0
                self.CoutCommerce:float=0.0
                self.CoutCourse:float=0.0
                self.CoutGuerre:float=0.0
                # Gestion des conteneurs dynamiques (Dictionnaires et Listes)
                self.cargaison: Dict[str, float] = {}
                self.munitions: Dict[str, int] = {}
                self.journal: List[str] = []
                df=utils.RENCONTRE_NAVIRE
                df=df[df['Nom']==Type]
                # On récupère la première ligne correspondante sous forme de dictionnaire
                ligne_data = df.iloc[0].to_dict()
                # 2. Parcours de toutes les colonnes pour mettre à jour l'objet
                for colonne, valeur in ligne_data.items():

                # 3. Vérification de l'existence de l'attribut dans la classe avant modification
                    if hasattr(self, colonne):
                        setattr(self, colonne, valeur)
                self.Tonnage:int=self.CalculTonnage()
                self.TonnageMarchandise=random.randint(4,10)/10*self.Tonnage
                self.NombreEquipage: int = self.CalculEquipage()
                self.StructureCoqueMax: float = self.StructureCoque
                self.StructureVoileMax: float = self.StructureVoile
                if charger==False:
                    self.EquipageNom=self.Name+"_Equipage"
                    self.Marchandise = Marchandise()
                    Cargaison =self.Marchandise.GenerateMarchandise(Region)
                    self.Marchandise.AjoutMarchandise(self.Marchandise,Cargaison["Cargaison"],self.TonnageMarchandise)
                    self.Marchandise.Tonnage=self.TonnageMarchandise
                    self.Marchandise.Name = self.Name + "_Marchandises"
                    self.Marchandise.sauvegarder(self.Name+"_Marchandises")
                    self.Equipage=Equipage(self.NombreEquipage,"Matelot",self.EquipageNom)
                self.ValeurCombat=self.CalculScoreCombat()
                self.sauvegarder()

    def Affichage(self):

        return {
            "Identification": {
                "type": "formulaire",
                "donnees": {
                    "Nom": self.Name,
                    "Type": self.type_navire,
                    "Compagnie": self.Compagnie,
                    "Région": self.regions_depart,
                    "Pirate": self.pirate,
                }
            },

            "Navigation": {
                "type": "formulaire",
                "donnees": {
                    "Longueur": self.Longueur,
                    "Mâts": self.NbMats,
                    "Allure": self.allure,
                    "Vitesse": self.VitesseMoyenne,
                    "Près": self.Pres,
                    "Largue": self.Largue,
                    "Grand largue": self.GrandLargue,
                    "Vent arrière": self.VentArriere,
                }
            },

            "Combat": {
                "type": "formulaire",
                "donnees": {
                    "Canons": self.NbCanons,
                    "Combat": self.combat,
                    "Manœuvre": self.manoeuvre,
                    "Pointage": self.pointage,
                    "Recharge": self.recharge,
                    "Ruse": self.ruse,
                    "Valeur combat": self.valeur_combat,
                    "Canonnade": self.ValeurCanonnade,
                }
            },

            "Équipage": {
                "type": "formulaire",
                "donnees": {
                    "Équipage": self.EquipageNom,
                    "Minimum": self.EquipMin,
                    "Maximum": self.EquipMax,
                    "Présents": self.NombreEquipage,
                }
            },

            "Économie": {
                "type": "formulaire",
                "donnees": {
                    "Cargaison": self.Name+"_Marchandise",
                    "Tonnage": self.Tonnage,
                    "Marchandises": self.TonnageMarchandise,
                    "Coque": f"{self.StructureCoque}/{self.StructureCoqueMax}",
                    "Voiles": f"{self.StructureVoile}/{self.StructureVoileMax}",
                    "Coût commerce": self.CoutCommerce,
                    "Coût guerre": self.CoutGuerre,
                }
            }
        }



            # Bouchons pour éviter les plantages si ces méthodes sont déclarées plus bas dans votre fichier
    def OrigineNavire(self, region):
                self.region=region

    def CalculTonnage(self):
        return random.randint(int(self.TonnageMin), int(self.TonnageMax))

    def CalculEquipage(self):
        return random.randint(int(self.EquipMin), int(self.EquipMax))

    def CheckNavire(self, navire):
        garde_cote = False

        types_autorises = {
            "Brick",
            "Brigantin",
            "Corvette",
            "Cotre",
            "Deux-ponts trois-mâts barque",
            "Deux-ponts trois-mâts carré",
            "Flibot",
            "Flûte",
            "Frégate trois-mâts barque",
            "Frégate trois-mâts carré",
            "Gabare",
            "Galiote (Brick PSx1.5)",
            "Goélette balaou",
            "Goélette brick",
            "Goélette franche",
            "Goélette de guerre",
            "Schooner",
            "Houari (Goélette franche avec modif)",
            "Ketch (Brigantin avec modif)",
            "Langard (Brigantin)",
            "Négrier (Brick ou Marchand avec modif)",
            "Paquebot (Goélette balaou)",
            "pingre (Flûte)",
            "patach (Goélette franche)",
            "pilote (Goélette franche, montre la route à suivre au port)",
            "pinnasse (Goélette franche)",
            "plut (Brigantin, Néerlandais)",
            "prame (Deux-ponts trois-mâts barque avec modif)",
            "ramberge (Sloop, rivière, anglais)",
            "Senau (Brick avec modif)",
            "Sloop",
            "trois-mâts goélette",
            "trois-ponts",
            "yacht (Sloop)"
        }

        if navire.Type == "Garde côte (relancer jusqu’à trouver sloop, goélette, brigantin, brick, chebec, etc)":
            while True:
                navire = Navire.generer_aleatoire()

                if navire.Type in types_autorises:
                    garde_cote = True
                    break

        return navire, garde_cote

    def GeneEquipage(self):
                comp = {'combat': 4, 'manoeuvre': 5, 'pointage': 3, 'recharge': 4, 'ruse': 2, 'valeur_combat': 12.5}
                return "Compétences d'équipage générées avec succès !", comp

    def sauvegarder(self):

        ligne = {}

        for cle, valeur in self.__dict__.items():
            ligne[cle] = valeur
        self.ValeurCombat = self.CalculScoreCombat()
        df = pd.DataFrame([ligne])

        df.to_csv(
            os.path.join(config.BASE_PATH, "Navire", f"{self.Name}.csv"),
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )


    @classmethod
    def charger_depuis_csv(cls, nom_fichier: str):
        print("CHARGEMENT NAVIRE :", nom_fichier)

        chemin_fichier = os.path.join(
            config.BASE_PATH,
            "Navire",
            f"{nom_fichier}.csv"
        )

        if not os.path.exists(chemin_fichier):
            print(f"Le fichier {chemin_fichier} n'existe pas.")
            return None

        with open(chemin_fichier, mode="r", newline="", encoding="cp1252") as f:
            reader = csv.DictReader(f, delimiter=";")
            lignes = list(reader)

        if not lignes:
            return None

        donnees = lignes[-1]

        # Création d'un navire "vide"
        navire = cls(charger=True)

        # Le nom du navire devient le nom du fichier
        navire.Name = nom_fichier

        # Chargement des attributs

        for cle, valeur in donnees.items():

            if cle in ("Equipage", "Marchandise"):
                continue

            if not hasattr(navire, cle):
                continue

            if valeur == "":
                 continue

            type_origine = type(getattr(navire, cle))

            try:
                if type_origine is bool:
                        setattr(navire, cle, valeur.lower() in ("true", "1", "o", "yes"))

                elif type_origine is int:
                        setattr(navire, cle, int(valeur))

                elif type_origine is float:
                        setattr(navire, cle, float(valeur.replace(",", ".")))

                elif type_origine in (list, dict):
                    pass

                else:
                    setattr(navire, cle, valeur)

            except ValueError:
                print(f"Erreur de conversion : {cle} = {valeur}")

        return navire

    @staticmethod
    def CalculType(zone, annee):
        de = random.randint(1, 100)

        df = utils.GENE_NAVIRE

        df = df[df['DeBateau'] >= de]
        df = df[df['Zone'] == zone]

        if df.empty:
            return None

        return df['Bateau'].iloc[0]

    def CalculCompagnie(self, zone, annee):
        de = random.randint(1, 100)

        df = utils.COMPAGNIE_COMMERCIALE

        df = df[df["Zone"] == zone]
        df = df[df["PeriodMax"] > annee]
        df = df[df["Intervalle"] <= de]

        if df.empty:
            return None

        ligne = df.iloc[-1]

        compagnie = f"{ligne['Acteur']} ({ligne['Nationalite']})"

        return ligne['Acteur'],ligne['Nationalite']
    @staticmethod
    def ConvertZone(region):
        df = utils.LISTE_REGIONS
        df=df[df['RegionsCommerciale']==region]
        return df['RegionsCommerciale'].iloc[0],df['RegionsCompagnie'].iloc[0],df['RegionsRencontre'].iloc[0]

    def ProbaRencontre(self,zone, annee):
        df = utils.COMPAGNIE_COMMERCIALE

        df = df[df["Zone"] == zone]
        df = df[df["PeriodMax"] > annee]

        if df.empty:
            return None

        proba= df.iloc[-1]


        return proba

    def DeterRencontre(self,region,de,annee,nom):
        ZoneCommerce,ZoneCompagnie,ZoneRencontre=self.ConvertZone(region)
        res=self.ProbaRencontre(ZoneRencontre,annee)
        if de<res:
            Compagnie,Nationalite=self.CalculCompagnie(ZoneCompagnie,annee)
            Type=self.CalculType(ZoneRencontre,annee)
            NavireRencontre=Navire(Type,nom,region)
            NavireRencontre.Compagnie=Compagnie
            NavireRencontre.Nationalite = Nationalite
            NavireRencontre.Name=NavireRencontre.NomNavire(Nationalite)
            return NavireRencontre
        else:
            return None
    def Reparer(self,navire):
        navire=self.charger_depuis_csv(navire)
        ReparationCoque=navire.StructureCoque/navire.StructureCoqueMax
        ReparationVoile=navire.StructureVoile/navire.StructureVoileMax
        CoutReparation=navire.CoutSansCanon*(ReparationVoile+ReparationCoque)/2
        navire.StructureVoile=navire.StructureVoileMax
        navire.StructureCoque=navire.StructureCoqueMax
        CompCharpentier=utils.Compute(1)
        TempsEnJourReparation=utils.TestValeurNonNumerique(CompCharpentier,0)[0]
        return CoutReparation,TempsEnJourReparation
    def get_actions(self):
        return ["Poursuivre", "CombatNaval", "Reparer"]
    def executer_action(self, action,instance,valeurs=None):

        if action == "Poursuivre":
            return f"Fonction pas encore implemente"

        elif action == "CombatNaval":
            return self.CombatNaval(valeurs['Navire1'],valeurs['Munition1'],valeurs['Bonus1'],valeurs['Navire2'],valeurs['Munition2'],valeurs['Bonus2'])
            self.sauvegarder()
        elif action == "Reparer":

            Cout,TempsJour =self.Reparer(instance)
            return f"Reparation  effectuée pour un cout de {Cout} et il faut {TempsJour} jours d'escale."


    def DegatsNavire(self,navire_attaquant, navire_attaque, type_munition,bonus):
        bonus_tir = navire_attaque.CategorieNavire - 3
        print("Equipage avant ResultatCompetence :", navire_attaquant.Equipage)
        print("Type :", type(navire_attaquant.Equipage))
        print(navire_attaquant.Equipage)
        print(type(navire_attaquant.Equipage))
        print(navire_attaquant.Equipage.ResultatCompetence("Pointage",bonus)[1])
        succes_tir = utils.Test(navire_attaquant.Equipage.ResultatCompetence("Pointage",bonus)[1],bonus)
        succes_tir += succes_tir * bonus_tir / 5
        succes_tir = utils.ConvertFloatToInt(succes_tir)

        localisation = random.randint(1, 6)

        if type_munition != "Mitraille":

            if navire_attaque.NbMats == 3 or type_munition == "Coque":

                if localisation < 2:
                    succes_tir += 2

                if localisation > 5:
                    succes_tir += 1

            elif navire_attaque.NbMats == 2:

                if localisation < 4:
                    succes_tir += 2

                if localisation > 3:
                    succes_tir += 1

        succes_recharge = utils.Test(navire_attaquant.Equipage.ResultatCompetence("Recharge",bonus)[1],bonus)
        recharge = utils.ConvertFloatToInt(7 - succes_recharge)

        degats = 0.9925 * np.exp(
            0.2298 * (navire_attaquant.ValeurCanonnade - 3.9721 + 2 * succes_tir)
        )

        degats = utils.ConvertFloatToInt(degats)
        navire_attaque.sauvegarder()
        navire_attaquant.sauvegarder()
        return degats, recharge

    def PerteNavire(self,navire, pertes, type_munition):

        pertes = int(pertes)
        texte = ""

        if type_munition == "Voile":

            navire.StructureVoile = max(
                0,
                navire.StructureVoile - pertes
            )

            navire.Equipage.Tues(pertes)
            navire.NombreEquipage = max(0, navire.NombreEquipage - pertes)

            texte += f"{navire.Name} a perdu {pertes} hommes et des voiles.\n"

        elif type_munition == "Coque":

            navire.StructureCoque = max(
                0,
                navire.StructureCoque - pertes
            )

            navire.Equipage.Tues(pertes)
            navire.NombreEquipage = max(0, navire.NombreEquipage - pertes)

            texte += f"{navire.Name} a perdu {pertes} hommes et des points de coque.\n"

        elif type_munition == "Mitraille":

            navire.Equipage.Tues(pertes)
            navire.NombreEquipage = max(0, navire.NombreEquipage - pertes)

            texte += f"{navire.Name} a perdu {pertes} hommes.\n"

        if navire.StructureCoque <= 0:
            texte += f"{navire.Name} a coulé.\n"

        if navire.StructureVoile <= 0:
            texte += f"{navire.Name} a dématé.\n"

        navire.sauvegarder()

        return pertes, texte

    def CombatNaval(self,navire1, munition1,bonus1, navire2, munition2,bonus2):


        texte = ""
        navire1=self.charger_depuis_csv(navire1)
        navire2=self.charger_depuis_csv(navire2)
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
        if navire1.Equipage.NombreMembres()> 0:

            perte1, temp = self.PerteNavire(
                navire1,
                degat2,
                munition2
            )

            texte += temp + "\n"

            texte += navire1.Equipage.Attitude(
                -perte1 / navire1.Equipage.NombreMembres() * 50
            )[1]

        else:

            texte += f"{navire1.Name} a été décimé.\n"

        # Le navire 2 subit les dégâts du navire 1
        if navire2.Equipage.NombreMembres() > 0:

            perte2, temp = self.PerteNavire(
                navire2,
                degat1,
                munition1
            )

            texte += temp + "\n"

            texte += navire2.Equipage.Attitude(
                -perte2 / navire2.Equipage.NombreMembres() * 50
            )[1]

        else:

            texte += f"{navire2.Name} a été décimé.\n"
        navire1.sauvegarder()
        navire2.sauvegarder()
        texte +=f"{navire1.Name} a perdu {perte1} hommes"
        texte +=f"{navire2.Name} a perdu {perte2} hommes"

        return texte

    def actions_rencontre(self):
        return [
            "Commercer",
            "Poursuivre",
            "Hisser le pavillon noir",
            "Canonner",
            "Fuir"
        ]

    def ReconnaissanceNavire(self, NavireRencontre, CompVigie):

        ligne = {
            "Name": NavireRencontre.Name
        }

        caracteristiques = {
            "CategorieNavire": NavireRencontre.CategorieNavire,
            "Longueur": NavireRencontre.Longueur,
            "NbMats": NavireRencontre.NbMats,
            "Tonnage": NavireRencontre.Tonnage,
            "NbCanons": NavireRencontre.NbCanons,
        }

        for nom, valeur in caracteristiques.items():
            succes = utils.Test(CompVigie, 0)
            ligne[nom] = utils.MoyenneGauss(valeur, valeur / 2, succes)

        df = pd.DataFrame([ligne])

        fichier = os.path.join(
            config.BASE_PATH,
            "Navire",
            f"{NavireRencontre.Name}_Reconnu.csv"
        )

        df.to_csv(
            fichier,
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )
    def CalculScoreCombat(self):
        return self.NombreEquipage*self.StructureCoque*self.ValeurCanonnade

    def PavillonNoir(self,autre_navire):
        NbSelf=self.NombreEquipage
        NbAutre=autre_navire.NombreEquipage
        if NbSelf/NbAutre>1:
            Bonus=int(-NbSelf/NbAutre)
        else:
            Bonus=int(NbAutre/NbSelf)
        MembreMotive=len(autre_navire.Equipage)
        Test=len(autre_navire.Equipage.Reddition(Bonus))
        if Test<MembreMotive/2:
            return (f"Le capitaine hisse le drapeau blanc \n Il est pret à vous céder sa marchandise sans combat \n  \n Veuillez vous rendre dans l'onglet Marchandise/Actions \n")
            (f"Vous pourrez alors procéder au pillage de {self.Marchandise.Name} pour {self.Marchandise.Name} \n")
        return (f"Le capitaine ne cède pas, vous devez alors le poursuivre avant d'entrer au combat, si vous parvenez à le suivre \n Veuillez vous rendre dans Navire/Actions et \n")
        (f" (et choisir CombatNaval entre {self.Name} et {autre_navire.Name}")

    def Commercer(self,autre_navire):
        if "Interlope" in autre_navire.Compagnie:
            return (f"Le capitaine semble enclin à commercer avec vous \n Il est pret à vous acheter de la marchandise à son CoursExces +10% par réussite de Commerce sous Expression\n Vous pouvez également acheter sa marchandise à son cours pénurie -10% par test de Commerce sous expression réussie \n Veuillez vous rendre dans l'onglet Marchandise/Actions \n"
                    f"Vous pourrez alors procéder à l'achat et vente de marchandise pour {self.Marchandise.Name} et {autre_navire.Marchandise.Name}")
        else:
            return f"Le capitaine ne souhaite pas commercer avec vous et vous demande si vous avez des papiers en règle \n Si vous n'avez pas de papier en règle veuillez assurer un combat naval entre {self.Name} et {autre_navire.Name} \n Sinon vous continuez votre route"

    def NomNavire(self,Nationalite):
        Name=utils.NOMS_NAVIRE
        Name=Name[Name['Nationalite']==Nationalite]
        Name = random.choice(Name)
        return Name