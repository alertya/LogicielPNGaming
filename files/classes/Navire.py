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
import tkinter as tk
from tkinter import messagebox
from openpyxl import load_workbook
from typing import Dict, List
from .Equipage import Equipage
from .Marchandise import Marchandise
# Remplacer les imports relatifs selon la structure exacte du projet si nécessaire
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

    def __init__(self, Type: str, Name: str,Region:str):
                # -------------------------
                # Paramètres requis à la création
                # -------------------------
                self.type_navire: str = Type  # Représente 'Bateau' ou 'CategorieNavire' du CSV
                self.Name: str = Name  # Représente 'Nom' dans le CSV

                # -------------------------
                # Rencontre & Origine
                # -------------------------
                self.de_rencontre: int = 0
                self.type_rencontre: str = ""
                self.de_depart: int = 0
                self.regions_depart: str = Region
                self.de_compagnie: int = 0
                self.Compagnie: str = ""

                # -------------------------
                # Identification & Catégorie
                # -------------------------
                self.bateau: str = ""
                self.de_bateau: int = 0
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
                self.cargaison3: int = 0
                self.vivre: float = 0.0
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
                print(ligne_data)
                # 2. Parcours de toutes les colonnes pour mettre à jour l'objet
                for colonne, valeur in ligne_data.items():

                # 3. Vérification de l'existence de l'attribut dans la classe avant modification
                    if hasattr(self, colonne):
                        setattr(self, colonne, valeur)
                self.Tonnage:int=self.CalculTonnage()
                self.TonnageMarchandise=random.randint(4,10)/10*self.Tonnage
                self.Equipage: int = self.CalculEquipage()
                self.StructureCoqueMax: float = self.StructureCoque
                self.StructureVoileMax: float = self.StructureVoile
                EquipageNavire=Equipage(self.Equipage,"Matelot",self.Name+"_Equipage")
                self.EquipageNom=self.Name+"_Equipage"
                self.Marchandise = Marchandise()
                self.Marchandise =self.Marchandise.GenerateMarchandise(Region)
                self.Marchandise.Tonnage=self.TonnageMarchandise
                self.Marchandise.Name = self.Name + "_Marchandises"
                self.Marchandise.sauvegarder(self.Name+"_Marchandises")

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
    def CheckNavire(self, bateau):
        return bateau, False

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
    def charger_depuis_csv(self, nom_fichier: str = "SauvegardeNavire"):
                """
                Parcourt les attributs de la classe et charge automatiquement leurs valeurs
                à partir d'un fichier CSV précédemment sauvegardé.
                """
                import os
                import csv

                chemin_fichier = os.path.join(config.BASE_PATH,'Navire', f"{nom_fichier}.csv")

                if not os.path.exists(chemin_fichier):
                    print(chemin_fichier)
                    print(f"Le fichier de sauvegarde {nom_fichier} n'existe pas.")
                    return False

                donnees_navire = None

                # 1. Lecture du fichier CSV
                with open(chemin_fichier, mode="r", newline="", encoding="cp1252") as f:
                    reader = csv.DictReader(f, delimiter=";")

                    # Sinon, on récupère par défaut la toute dernière ligne (dernière sauvegarde)
                    lignes = list(reader)
                    if lignes:
                        donnees_navire = lignes[-1]

                if not donnees_navire:
                    print("Aucune donnée correspondante trouvée dans le fichier CSV.")
                    return False

                # 2. Parcours automatique des attributs existants pour modifier l'objet
                for cle, valeur in donnees_navire.items():
                    # Si l'attribut n'existe pas dans l'__init__ du Navire actuel, on l'ignore
                    if not hasattr(self, cle):
                        continue

                    # Si la case du CSV est complètement vide, on passe
                    if valeur == "":
                        continue

                    # On détecte le type d'origine de l'attribut dans notre __init__
                    type_origine = type(getattr(self, cle))

                    # 3. Conversion intelligente du texte CSV vers le bon type Python
                    try:
                        if type_origine is bool:
                            # Gestion des booléens ("True", "O", "1" -> True)
                            setattr(self, cle, valeur.lower() in ["true", "o", "1", "yes"])

                        elif type_origine is float:
                            # Remplace la virgule française par un point informatique avant conversion
                            valeur_nettoyee = valeur.replace(",", ".")
                            setattr(self, cle, float(valeur_nettoyee))

                        elif type_origine is int:
                            setattr(self, cle, int(valeur))

                        elif type_origine in [dict, list]:
                            # Recrée des structures vides si l'import brut est une chaîne textuelle brute
                            if valeur in ["{}", "[]"]:
                                setattr(self, cle, type_origine())
                        else:
                            # Par défaut, on l'assigne sous forme de chaîne (str)
                            setattr(self, cle, valeur)

                    except ValueError:
                        # En cas de problème de conversion, on laisse la valeur par défaut pour ne pas planter
                        print(f"Erreur de conversion pour l'attribut '{cle}' avec la valeur '{valeur}'.")

                return True

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