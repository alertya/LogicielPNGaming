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

    def __init__(self, Type="Sloop", Name="Test",Region="Brésil"):
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
                df=pd.read_csv(config.BASE_PATH+"/RencontreNavire.csv",sep=";",decimal=",",encoding="cp1252")
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
                self.EquipageNom=self.Name+"_Equipage"
                self.Marchandise = Marchandise()
                Cargaison =self.Marchandise.GenerateMarchandise(Region)
                self.Marchandise.AjoutMarchandise(Cargaison["Cargaison"],self.TonnageMarchandise)
                self.Marchandise.Tonnage=self.TonnageMarchandise
                self.Marchandise.Name = self.Name + "_Marchandises"
                self.Marchandise.sauvegarder(self.Name+"_Marchandises")
                self.Equipage=Equipage(self.NombreEquipage,"Matelot",self.EquipageNom)
                self.sauvegarder()

    def RencontreNavire(self, Jour=None, Region=None, SaveBateau=False, CompagnieCommerciale="Defaut") -> 'Navire':
                """Génère une rencontre navale et retourne un objet Navire configuré."""

                # Gestion des variables d'environnement de la méthode
                if Jour is None:
                    Jour = getattr(self, "Jour", None) or getattr(self, "Name", None) or "Rencontre"

                # Chargement des données de rencontre depuis le CSV
                DFTemp = pd.read_csv(os.path.join(BASE_PATH, "RencontreNavire.csv"), sep=";", decimal=",", encoding="cp1252")

                # Test du type d'événement
                if "_AVENTURIER" in str(Jour):
                    Aventurier = 1
                    Allegence = "Pirate"
                else:
                    Aventurier = 0
                    Allegence = CompagnieCommerciale

                Garde_Cote = False

                # Détermination du type de rencontre
                de = random.randint(1, 100)
                Rencontre = DFTemp[DFTemp["DeRencontre"] >= de]["TypeRencontre"].iloc[0]

                # Détermination de l'origine, compagnie, et type de bateau
                Depart, Compagnie, Rencontre = self.OrigineNavire(Region)

                de = random.randint(1, 100)
                Bateau = DFTemp[DFTemp["DeBateau"] >= de]["Bateau"].iloc[0]

                # Sélection des informations du navire de base
                Bateau, Garde_Cote = self.CheckNavire(Bateau) if hasattr(self, 'CheckNavire') else (Bateau, False)

                row_navire = DFTemp[DFTemp["Nom"] == Bateau].iloc[0]
                if Aventurier == 1:
                    while row_navire["Pirate"] == "N":
                        de = random.randint(1, 100)
                        Bateau = DFTemp[DFTemp["DeBateau"] >= de]["Bateau"].iloc[0]
                        row_navire = DFTemp[DFTemp["Nom"] == Bateau].iloc[0]

                # Détermination de l'allure du navire rencontrant
                Vent = [
                    'PresBabord', 'PresTribord', 'LargueBabord', 'LargueTribord',
                    'GrandLargueBabord', 'GrandLargueTribord', 'Vent arriere babord', 'Vent arriere tribord'
                ]
                Allure = random.choice(Vent)

                # ---- INSTANCIATION DE LA CLASSE NAVIRE POUR LE NAVIRE RENCONTRÉ ----
                # On extrait un identifiant unique temporaire ou générique (ex: 999)
                nouveau_navire = Navire(Nb=999, Type=str(row_navire['Nom']), Name=f"Navire_{Jour}")

                # Assignation des variables descriptives et d'allégeance
                nouveau_navire.allure = Allure
                nouveau_navire.compagnie = Compagnie
                nouveau_navire.allegence = Allegence
                nouveau_navire.regions_depart = Depart
                nouveau_navire.pirate = True if row_navire.get("Pirate", "N") == "Y" else False
                nouveau_navire.reputation = int(10 * random.random() ** 3)
                nouveau_navire.equipage_fichier = f"{Jour}_EQUIPAGE.csv"

                # Compilation du log text de rencontre
                text_log = f"Vous avez aperçu un {nouveau_navire.type} avec l'allure {nouveau_navire.allure} \n"
                if Garde_Cote:
                    text_log += "  en tant que GARDE COTE\n"

                # Calcul des capacités et des caractéristiques d'armement de la ligne CSV
                TonnageMax = float(row_navire["TonnageMax"])
                TonnageMin = float(row_navire["TonnageMin"])
                Tonnages = float(random.randint(int(TonnageMin), int(TonnageMax)))

                # Remplissage de la cargaison
                de_cargaison = random.randint(40, 100) if Aventurier == 0 else random.randint(1, 100)
                # Utilisation sécurisée de utils
                if hasattr(utils, 'utils') and hasattr(utils.utils, 'ConvertFloatToInt'):
                    Tonnage = utils.utils.ConvertFloatToInt(Tonnages * de_cargaison / 100)
                else:
                    Tonnage = int(Tonnages * de_cargaison / 100)

                nouveau_navire.tonnage_max = Tonnages
                nouveau_navire.tonnage = Tonnage

                # Caractéristiques d'armement / équipage
                nouveau_navire.canons = int(row_navire.get('NbCanons', 0))
                Equip = random.randint(int(row_navire["EquipMin"]), int(row_navire["EquipMax"]))
                nouveau_navire.equipage = Equip
                nouveau_navire.equipage_min = int(row_navire["EquipMin"])

                # Calcul modificateur richesse & bonus combat (mémoire/logs si besoin)
                BonusDe1 = random.randint(1, 100)
                BonusCanon = nouveau_navire.canons
                BonusTonnage = min(Tonnage / 10, 100)
                BonusDe2 = random.randint(1, 100)
                ModificateurRichess = BonusTonnage + BonusCanon + BonusDe2 + BonusDe1

                # Intégration du système de marchandises externe
                NiveauMarchandise = Marchandise.RetourMarchandise(Tonnage, Depart)
                for key, value in NiveauMarchandise.items():
                    if "vide" in key or "pillé" in key:
                        nouveau_navire.tonnage = 0
                    Marchandise.AjoutMarchandise(key, value, f"Marchandise_{Jour}.csv")

                # Génération des compétences de l'équipage
                Temp, CompEquipage = self.GeneEquipage() if hasattr(self, 'GeneEquipage') else ("", {})
                text_log += "\n" + Temp + "\n"

                # Assignation des compétences d'équipage reçues au nouvel objet
                nouveau_navire.combat = CompEquipage.get('combat', 0)
                nouveau_navire.manoeuvre = CompEquipage.get('manoeuvre', 0)
                nouveau_navire.pointage = CompEquipage.get('pointage', 0)
                nouveau_navire.recharge = CompEquipage.get('recharge', 0)
                nouveau_navire.ruse = CompEquipage.get('ruse', 0)
                nouveau_navire.valeur_combat = float(CompEquipage.get('valeur_combat', 0.0))
                nouveau_navire.valeur_canonnade = float(CompEquipage.get('valeur_canonnade', 0.0))

                # Enregistrement du log final
                nouveau_navire.text_rencontre = text_log

                return nouveau_navire

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
        import os
        import csv

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
        navire = cls()

        # Le nom du navire devient le nom du fichier
        navire.Name = nom_fichier

        # Chargement des attributs
        for cle, valeur in donnees.items():

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
                    pass  # à adapter si tu souhaites les restaurer

                else:
                    setattr(navire, cle, valeur)

            except ValueError:
                print(f"Erreur de conversion : {cle} = {valeur}")

        return navire

    def CalculType(self, zone, annee):
        de = random.randint(1, 100)

        df = pd.read_csv(config.BASE_PATH + "/GeneNavire.csv",sep=";",decimal=",",encoding="cp1252")

        df = df[df['Zone'] == zone]
        df = df[df['PeriodMax'] > annee]
        df = df[df['Intervalle'] <= de]

        if df.empty:
            return None

        return df['Bateau'].iloc[-1]

    def CalculCompagnie(self, zone, annee):
        de = random.randint(1, 100)

        df = pd.read_csv(
                config.BASE_PATH + "/CompagnieCommerciale.csv",
                sep=";",
                decimal=",",
                encoding="cp1252"
            )

        df = df[df["Zone"] == zone]
        df = df[df["PeriodMax"] > annee]
        df = df[df["Intervalle"] <= de]

        if df.empty:
            return None

        ligne = df.iloc[-1]

        compagnie = f"{ligne['Acteur']} ({ligne['Nationalite']})"

        return compagnie
    def ConvertZone(self,region):
        df = pd.read_csv(config.BASE_PATH + "/ListeRegions.csv", sep=";", decimal=",", encoding="cp1252")
        df=df[df['RegionsCommerciale']==region]
        return df['RegionsCommerciale'].iloc[0],df['RegionsCompagnie'].iloc[0],df['RegionsRencontre'].iloc[0]

    def ProbaRencontre(self,zone, annee):
        df = pd.read_csv(
                config.BASE_PATH + "/CompagnieCommerciale.csv",
                sep=";",
                decimal=",",
                encoding="cp1252"
            )

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
            Compagnie=self.CalculCompagnie(ZoneCompagnie,annee)
            Type=self.CalculType(ZoneRencontre,annee)
            NavireRencontre=Navire(Type,nom,region)
            NavireRencontre.Compagnie=Compagnie
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
            self.SupprimerMarchandise(valeurs["Marchandise"],valeurs['Tonnage'])
            self.sauvegarder(self.Name)

        elif action == "CombatNaval":
            self.CombatNaval(valeurs['Navire1'],valeurs['Munition1'],valeurs['Bonus1'],valeurs['Navire2'],valeurs['Munition2'],valeurs['Bonus2'])
            self.sauvegarder(self.Name)
        elif action == "Reparer":

            Cout,TempsJour =self.Reparer(instance)
            return f"Reparation  effectuée pour un cout de {Cout} et il faut {TempsJour} jours d'escale."

    def Piller(self, navire_pille):

        place_restante = self.TonnageMax - self.Tonnage

        while place_restante > 0 and navire_pille.Marchandise.Cargaisons:

            cargaison = navire_pille.Marchandise.Cargaisons[0]

            self.Marchandise.AjoutMarchandise(
                cargaison,
                1
            )

            navire_pille.Marchandise.SupprimerMarchandise(
                cargaison,
                1
            )

            self.Tonnage += 1
            place_restante -= 1

        self.Marchandise.sauvegarder(self.Marchandise.Name)
        navire_pille.Marchandise.sauvegarder(navire_pille.Marchandise.Name)

        self.sauvegarder(self.Name)
        navire_pille.sauvegarder(navire_pille.Name)

        return "Le pillage a été réalisé."

    def DegatsNavire(self,navire_attaquant, navire_attaque, type_munition,bonus):

        navire_attaquant=Navire.charger_depuis_csv(navire_attaquant)
        navire_attaque=Navire.charger_depuis_csv(navire_attaque)
        bonus_tir = navire_attaque.CategorieNavire - 3

        succes_tir = utils.Test(navire_attaquant.Equipage.ResultatCompetence("Pointage",bonus)[1])
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

        succes_recharge = utils.Test(navire_attaquant.navire_attaquant.Equipage.ResultatCompetence("Recharge",bonus)[1])
        recharge = utils.ConvertFloatToInt(7 - succes_recharge)

        degats = 0.9925 * np.exp(
            0.2298 * (navire_attaquant.ValeurCanonnade - 3.9721 + 2 * succes_tir)
        )

        degats = utils.ConvertFloatToInt(degats)
        navire_attaque.sauvegarder()
        navire_attaquant.sauvegarder()
        return degats, recharge

    def PerteNavire(self,navire, pertes, type_munition):
        navire=Navire.charger_depuis_csv(navire)
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
        navire1.sauvegarder()
        navire2.sauvegarder()
        texte +=f"{navire1.Name} a perdu {perte1} hommes"
        texte +=f"{navire2.Name} a perdu {perte2} hommes"

        return texte