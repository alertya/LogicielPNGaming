# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:05:00 2023

@author: USER
"""

import numpy as np
import random

import csv

import math
import os
import pandas as pd
import tkinter as tk
import utils
from config import *
from tkinter import messagebox
from openpyxl import load_workbook
from Equipage import *
from Marchandise import *
import Navigation
import Voyage
#####Variable voyage

NbJour = 6
CompetenceVigie = 2

####Constantes
Nb = 182
Nbsss = 2
Superficie = 106460000 / 2
NbDaysOfCyclone = 59  ###https://public.wmo.int/fr/cyclones-tropicaux-0
NbDaysOfTempest = 27
Surface = np.pi * 750 * 750

SeuilMa = 4
DeMa = 20
SeuilAv = 4
DeAv = 40

Munitions = ['Boulets', 'Rames', 'Mitraille']
Proba = round(Superficie / Surface * 182 / 59)


class Navire:
    def __init__(self, Nb, Type, Name):

        self.Name = Name
        self.Type = Type
        self.Membres = []

        # Etat partagé de l'objet
        self.Jour = None
        self.Navire = None
        self.Equipage = []
        self.Marchandises = {}
        self.Text = ""

        Pond = pd.read_csv(
            BASE_PATH + "/ListeProf.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        Ponds = Pond[Pond["Type"] == Type]

        for _ in range(Nb):

            donnees = Ponds.iloc[0].to_dict()

            for column in Pond.columns[1:71]:

                if column not in ["Salaire", "Employeur"]:
                    donnees[column] = utils.Compute(
                        Ponds[column].iloc[0]
                    )

            donnees["ArmesBlanches"] = max(
                donnees["Dague"],
                donnees["Hache"],
                donnees["Sabre"]
            )

            membre = type("MembreEquipage", (), {})()

            for attribut, valeur in donnees.items():
                setattr(membre, attribut, valeur)

            membre.Nom = ""
            membre.Maladie = ""
            membre.Moral = 2
            membre.Attitude = int(
                np.random.normal(50, 5)
            )
            membre.Groupe = ""
            membre.Role = ""
            membre.Pirate = 1
            membre.KillCount = 0
            membre.LastSuccess = 0
            membre.Famine = 0
            membre.PVMax = random.randint(5, 8)
            membre.PV = membre.PVMax
            self.Membres.append(membre)

    def RencontreNavire(self, Jour=None, Region=None, SaveBateau=False, CompagnieCommerciale="Defaut"):
        """Génère une rencontre navale et conserve le résultat dans self.Navire.

        Signature historique acceptée : (Jour, Region, SaveBateau, CompagnieCommerciale).
        Si ``Jour`` n'est pas fourni, ``self.Jour`` est utilisé.
        """
        if Jour is None:
            Jour = self.Jour or self.Name or "Rencontre"
        self.Jour = Jour
        self.Text = ""
        Text = ""
        # Chargement des données de rencontre
        DFTemp = pd.read_csv(BASE_PATH + "/RencontreNavire.csv", sep=";", decimal=",", encoding="cp1252")
        ###On teste si le navire est un navuire aventurier (pirate) ou un navire marchand
        de = random.randint(1, 100)
        Compagnie = CompagnieCommerciale
        if "_AVENTURIER" in Jour:
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
        # Sélection des informations du navire
        Bateau = self.CheckNavire(Bateau)[0]
        Navire = DFTemp[DFTemp["Nom"] == Bateau].iloc[0]
        if Aventurier == 1:
            while Navire["Pirate"] == "N":
                de = random.randint(1, 100)
                Bateau = DFTemp[DFTemp["DeBateau"] >= de]["Bateau"].iloc[0]
                Navire = DFTemp[DFTemp["Nom"] == Bateau].iloc[0]
        else:
            Bateau, Garde_Cote = self.CheckNavire(Bateau)

        # Détermination de l'allure du navire
        Vent = [
            'PresBabord', 'PresTribord', 'LargueBabord', 'LargueTribord',
            'GrandLargueBabord', 'GrandLargueTribord', 'Vent arriere babord', 'Vent arriere tribord'
        ]
        Allure = random.choice(Vent)

        # Sélection des informations du navire
        Navire = DFTemp[DFTemp["Nom"] == Bateau]
        TypeNavire = Navire['Nom']
        # Texte descriptif de la rencontre
        Text += (
            f"Vous avez aperçu un {TypeNavire} avec l'allure {Allure} \n"
        )

        if Garde_Cote:
            # Texte descriptif de la rencontre
            Text += (
                f"  en tant que GARDE COTE\n"
            )

        # Calcul du tonnage de cargaison
        if Aventurier == 0:
            de_cargaison = random.randint(40, 100)  ###Si navire marchand remplissage compris entre 40 et 100%
        else:
            de_cargaison = random.randint(1, 100)  ###Si pirate remplissage entre 0 et 100%
        TonnageMax = Navire["TonnageMax"].iloc[0]
        TonnageMin = Navire["TonnageMin"].iloc[0]
        Tonnages = random.randint(int(TonnageMin), int(TonnageMax))
        Tonnage = utils.utils.ConvertFloatToInt(Tonnages * de_cargaison / 100)
        Navire['TonnageMax'] = Tonnages
        Navire['Tonnage'] = Tonnage
        BonusDe1 = random.randint(1, 100)
        BonusCanon = Navire['NbCanons'].iloc[0]
        BonusTonnage = min(Tonnage / 10, 100)
        BonusDe2 = random.randint(1, 100)
        ModificateurRichess = BonusTonnage + BonusCanon + BonusDe2 + BonusDe1

        # Calcul de l'équipage
        Equip = random.randint(int(Navire["EquipMin"].iloc[0]), int(Navire["EquipMax"].iloc[0]))
        EquipMax = Navire["EquipMax"].iloc[0]

        # Informations sur la cargaison
        NiveauMarchandise = Marchandise.RetourMarchandise(Tonnage, Depart)
        for key, value in NiveauMarchandise.items():
            if "vide" in key or "pillé" in key:
                Navire['Tonnage'] = 0
            Marchandise.AjoutMarchandise(key, value, "Marchandise_" + Jour + ".csv")
        # Text += f"Cargaison à bord du nvaire {NiveauMarchandise}.\n"

        # Ajout des nouvelles informations au DataFrame du navire
        Navire['EquipageNom'] = f"{Jour}_EQUIPAGE.csv"
        Navire['Compagnie'] = Compagnie
        Navire['Equipage'] = Equip
        Navire['RegionsDepart'] = Depart
        Navire['Allure'] = Allure
        Navire['Allegence'] = Allegence
        Navire['Reputation'] = int(10 * random.random() ** 3)
        # Génération de l'équipage
        Temp, CompEquipage = self.GeneEquipage()
        Text += "\n" + Temp + "\n"
        for k, values in CompEquipage.items():
            Navire[k] = values
        Navire['ValeurCombat'] = self.CalculCombatNavire(Navire)
        ValeurCombat = Navire['ValeurCombat'].iloc[0]
        Text += f"Valeur de combat de  : {ValeurCombat} \n"
        # Sin on couhaite une sauvegarde des données
        if SaveBateau:
            file_path = NAVIRE_PATH + "/" + Jour + ".csv"
            Navire.to_csv(file_path, sep=";", decimal=",", encoding='cp1252')
            print(Text.strip())
            print(f"Les informations du navire ont été sauvegardées dans {file_path}.")

        SaveEquipage = SaveBateau
        # Génération finale de l'équipage
        Equipage.Generate(Equip, 'Matelot', f"{Jour}", 0, True, SaveEquipage)
        self.FicheNavire(Jour, Navire, NiveauMarchandise)

        self.Navire = Navire
        self.Text = Text
        self.Marchandises = NiveauMarchandise
        return Navire, Text

    def CheckNavire(self, Bateau=None, Type=None):
        """Vérifie le type de navire et indique s'il s'agit d'un garde-côte.

        L'ancienne version utilisait les variables globales ``Type`` et ``Typ``
        qui n'existaient pas dans la méthode. La version objet utilise donc
        explicitement les arguments fournis.
        """
        Garde_Cote = False

        if Bateau is None:
            return None, False

        type_garde_cote = (
                Type == "Garde côte (relancer jusqu’à trouver sloop, goélette, "
                        "brigantin, brick, chebec, etc)"
        )

        if not type_garde_cote:
            return Bateau, False

        DFTemp = pd.read_csv(
            BASE_PATH + "/RencontreNavire.csv",
            sep=";", decimal=",", encoding="cp1252"
        )

        Lists = [
            'Brick', 'Brigantin', 'Corvette', 'Cotre',
            'Deux-ponts trois-mâts barque', 'Deux-ponts trois-mâts carré',
            'Flibot', 'Flûte', 'Frégate trois-mâts barque',
            'Frégate trois-mâts carré', 'Gabare',
            'Galiote (Brick PSx1.5)', 'Goélette balaou', 'Goélette brick',
            'Goélette franche', 'Goélette de guerre', 'Schooner',
            'Houari (Goélette franche avec modif)',
            'Ketch (Brigantin avec modif)', 'Langard (Brigantin)',
            'Négrier (Brick ou Marchand avec modif)',
            'Paquebot (Goélette balaou)', 'pingre (Flûte)',
            'patach (Goélette franche)',
            'pilote (Goélette franche, montre la route à suivre au port)',
            'pinnasse (Goelette franche)', 'plut (Brigantin, Néerlandais)',
            'prame (deux ponts trois mat barque avec modif)',
            'ramberge (Sloop, riviere, anglais)', 'Senau (brick avec modif)',
            'Sloop', 'traversier (Chasse-marée, francais)',
            'trois-mâts goélette', 'trois-ponts', 'yacht (sloop)'
        ]

        while Bateau not in Lists:
            de = random.randint(1, 100)
            selection = DFTemp[DFTemp["DeBateau"] >= de]
            if selection.empty:
                break
            candidat = selection["Bateau"].iloc[0]
            if candidat in Lists:
                Bateau = candidat
                break
            Bateau = candidat

        Garde_Cote = True
        return Bateau, Garde_Cote

    def GeneNavire(self, TypeNavire, Name, Region, NbHommes, SaveNavire):
        Text = ""
        DFTemp = pd.read_csv(BASE_PATH + "/RencontreNavire.csv", sep=";", decimal=",", encoding="cp1252")
        # Détermination du type de rencontre
        de = random.randint(1, 100)
        Rencontre = DFTemp[DFTemp["DeRencontre"] >= de]["TypeRencontre"].iloc[0]

        # Détermination de l'origine, compagnie, et type de bateau
        Depart, Compagnie, Rencontre = self.OrigineNavire(Region)
        Rencontre = DFTemp[DFTemp["DeRencontre"] >= de]["TypeRencontre"].iloc[0]
        de = random.randint(1, 100)
        Compagnie = DFTemp[DFTemp["DeCompagnie"] >= de]["Compagnie"].iloc[0]
        de = random.randint(1, 100)
        Bateau = DFTemp[DFTemp["Nom"] == TypeNavire]["Nom"].iloc[0]
        Bateau, Garde_Cote = self.CheckNavire(Bateau)
        # Détermination de l'allure du navire
        Vent = [
            'PresBabord', 'PresTribord', 'LargueBabord', 'LargueTribord',
            'GrandLargueBabord', 'GrandLargueTribord', 'Vent arriere babord', 'Vent arriere tribord'
        ]
        Allure = random.choice(Vent)

        # Sélection des informations du navire
        Navire = DFTemp[DFTemp["Nom"] == Bateau]

        # Texte descriptif de la rencontre
        Text += (
            f"Un navire {Bateau} de {Compagnie} venant de {Depart} a été généré au nom de {Name}\n"
        )
        if Garde_Cote:
            # Texte descriptif de la rencontre
            Text += (
                f"  en tant que GARDE COTE\n"
            )

        # Calcul du tonnage de cargaison
        de_cargaison = random.randint(40, 100)
        TonnageMax = Navire["TonnageMax"].iloc[0]
        TonnageMin = Navire["TonnageMin"].iloc[0]
        Tonnages = random.randint(int(TonnageMin), int(TonnageMax))
        Tonnage = utils.ConvertFloatToInt(Tonnages * de_cargaison / 100)
        BonusDe1 = random.randint(1, 100)
        BonusCanon = Navire['NbCanons'].iloc[0]
        BonusTonnage = min(Tonnage / 10, 100)
        BonusDe2 = random.randint(1, 100)
        ModificateurRichess = BonusTonnage + BonusCanon + BonusDe2 + BonusDe1

        # Ajout des informations de cargaison
        des_cargaison = random.randint(1, 100)
        Text += (
            f"Cargaison de MARCHAND contenant {de_cargaison}% de tonnage ({Tonnage}/{Tonnages})\n"
            f"Cargaison de AVENTURIER rempli à {des_cargaison}% de tonnage ({utils.ConvertFloatToInt(des_cargaison * Tonnages / 100)}/{Tonnages})\n"
            f"Bonus de richesse {ModificateurRichess} sans le modificateur de richesse associé et les teste de commerce érudition\n"
        )

        # Calcul de l'équipage
        de_equipage = random.randint(40, 100)
        EquipMax = Navire["EquipMax"].iloc[0]
        EquipTot = Navire["Equipage tout"].iloc[0]
        Equip = min(int(NbHommes), int(EquipMax))

        # Ajout des informations sur l'équipage
        Text += (
            f"Équipage rempli à {de_equipage}% ({Equip}/{EquipMax} hommes).\n"
            f"Équipage minimal pour manœuvrer et canonner en bordée : {EquipTot}.\n"
        )

        # Informations sur la cargaison
        NiveauMarchandise = Marchandise.RetourMarchandise(Tonnage, Depart)
        Text += f"Cargaison à bord du nvaire {NiveauMarchandise}.\n"

        # Ajout des nouvelles informations au DataFrame du navire
        Navire['Name'] = Name
        Navire['EquipageNom'] = f"{Name}_EQUIPAGE.csv"
        Navire['Compagnie'] = Compagnie
        Navire['Equipage'] = Equip
        Navire['RegionsDepart'] = Depart
        Navire['Allure'] = Allure
        Navire['Vivre'] = random.randint(0, 45)
        Navire['StructureCoqueMax'] = Navire['StructureCoque'].iloc[0]
        Navire['StructureVoileMax'] = Navire['StructureVoile'].iloc[0]
        # Génération de l'équipage
        Temp, CompEquipage = self.GeneEquipage()
        Text += "\n" + Temp + "\n"
        for k, values in CompEquipage.items():
            Navire[k] = values
        Navire['ValeurCombat'] = self.CalculCombatNavire(Navire)

        # Sauvegarde des données
        file_path = BASE_PATH + "/Navire/" + Name + ".csv"
        Navire.to_csv(file_path, sep=";", decimal=",", encoding='cp1252')
        print(Text.strip())
        messagebox.showinfo("Info", f"Les informations du navire ont été sauvegardées dans {file_path}.")
        messagebox.showinfo("Info", f"Veuillez remplir le formulaire de la deuxieme fenetre pour générer l'equipage")
        print(f"Les informations du navire ont été sauvegardées dans {file_path}.")

        # Génération finale de l'équipage
        Equipage.Generate(Equip, 'Matelot', f"{Name}", 0, 0, SaveNavire)
        self.FicheNavire(Name, Navire, NiveauMarchandise)
        self.Navire = Navire
        self.Text = Text
        self.Marchandises = NiveauMarchandise
        return Navire, Text

    def Test(self, Nb):
        Success = 0
        for k in range(Nb):
            Success = 0
            if Nb == 0:
                Test = random.choice(range(12)) + 1
                if Test > 9:
                    Success = -1
                elif Test == 1:
                    Success = 2
                elif Test <= 5:
                    Success = 1
            elif k > 0:
                for h in range(k):
                    Test = random.choice(range(10)) + 1
                    if Test == 1:
                        if Success == -1:
                            Success = 0
                        else:
                            Success = Success + 2
                    elif Test <= 5:
                        if Success == -1:
                            Success = 0
                        Success = Success + 1
                    elif Test > 9 and Success < 1:
                        Success = -1
        return Success

    def ReconnaissanceNavire(self, Vigilance, Navire):
        Te = 0
        Text = "Votre vigie a apercu un navire avec \n"
        Cat = ['CategorieNavire', 'NbCanons', 'NbMats', 'Longueur']
        for k in Cat:
            Succes = utils.Test(Vigilance, 0)
            Valeur = Navire[k]
            Estimation = utils.MaxGauss(Valeur, Valeur / 2, Succes)
            Text += " Un " + k + " de " + str(Estimation) + " \n"
        return Text


    def DegatsNavire(self, NavireAttaquant, NavireAttaque, TypeMunition):  ###A IMPLEMENTER
        NavVictime = pd.read_csv(BASE_PATH + "/Navire/" + NavireAttaque, sep=";", decimal=",", encoding='cp1252')
        TempDF = pd.read_csv(BASE_PATH + "/Navire/" + NavireAttaquant, sep=";", decimal=",", encoding='cp1252')
        NavVictime = NavVictime.iloc[0]
        NavireDegat = TempDF.iloc[0]
        HommesCanonnade = NavireDegat['Equipage'] - NavireDegat['Equipage tout']
        BonusCanonnade = min(1, HommesCanonnade / (NavireDegat['Equipage tout'] - NavireDegat[
            'EquipMin']))  ####Calcul du malus des dégats si nombre d'hommes insuffisant pour recharger les canons
        BonusCanonnade = int(BonusCanonnade)
        Cannonade = int(TempDF['Valeur canonnade'].iloc[0]) * BonusCanonnade
        BonusTir = NavVictime['CategorieNavire'] - 3

        SuccesTir = self.Test(TempDF['Pointage'].iloc[0])
        SuccesTir = SuccesTir + SuccesTir * (BonusTir) / 5
        SuccesTir = utils.ConvertFloatToInt(SuccesTir)
        LocalisationTir = random.choice(range(6)) + 1
        if TypeMunition != "Mitraille":
            if NavVictime['NbMats'] == 3 or TypeMunition == 'Coque':
                if LocalisationTir < 2:
                    SuccesTir += 2
                if LocalisationTir > 5:
                    SuccesTir += 1
            elif NavVictime['NbMats'] == 2:
                if LocalisationTir < 4:
                    SuccesTir += 2
                if LocalisationTir > 3:
                    SuccesTir += 1
        SuccesRecharge = self.Test(TempDF['Recharge'].iloc[0])
        Recharge = 7 - SuccesRecharge
        if TypeMunition == "Mitraille":
            Convert = pd.read_csv(BASE_PATH + "/CalibreCanon.csv", sep=";", decimal=",", encoding='cp1252')
            Convert = Convert[Convert['Valeur boulet'] == Cannonade]['Valeur mitraille'].iloc[0]
            Degat = 0.9925 * np.exp(0.2298 * (
                        Convert - 3.9721 + 2 * SuccesTir))  ####Calcul de valeur numérique des dégats à partir des canons et des succes de tir
        else:
            Degat = 0.9925 * np.exp(0.2298 * (
                        Cannonade - 3.9721 + 2 * SuccesTir))  ####Calcul de valeur numérique des dégats à partir des canons et des succes de tir
        Degat = utils.ConvertFloatToInt(Degat)
        Recharge = utils.ConvertFloatToInt(Recharge)
        return Degat, Recharge

    def PerteNavire(self, Navire, Pertes, TypeMunition):
        if Pertes < 0:
            Pertes = 0
        path = os.path.join(BASE_PATH, "Navire", Navire)
        TempDF = pd.read_csv(path, sep=";", decimal=",", encoding='cp1252')
        Pertes = int(Pertes)
        Text = "\n"

        col_voile = "StructureVoile"
        col_coque = "StructureCoque"
        col_equipage = "Equipage"
        col_equipage_nom = "EquipageNom"

        if TypeMunition == "Voile":
            if col_voile in TempDF.columns:
                TempDF.at[0, col_voile] = max(0, TempDF.at[0, col_voile] - Pertes)
            Text += f"{Navire} a perdu {Pertes} points de structure en voile.\n"

        elif TypeMunition == "Coque":
            if col_coque in TempDF.columns:
                TempDF.at[0, col_coque] = max(0, TempDF.at[0, col_coque] - Pertes)
            Text += f"{Navire} a perdu {Pertes}  points de structure en coque.\n"

        elif TypeMunition == "Mitraille":
            if col_equipage_nom in TempDF.columns:
                Equipage.Tues(Pertes, TempDF.at[0, col_equipage_nom])
            if col_equipage in TempDF.columns:
                TempDF.at[0, col_equipage] = max(0, TempDF.at[0, col_equipage] - Pertes)
            Text += f"{Navire} a perdu {Pertes} hommes.\n"

        else:
            Text += f"Type de munition inconnu : {TypeMunition}.\n"

        # Vérifications état critique
        if col_coque in TempDF.columns and TempDF.at[0, col_coque] <= 0:
            Text += f"{Navire} A COULE, VOUS VOUS ETES ECHOUE.\n"
            print(Text)
            Pertes = 999
        if col_voile in TempDF.columns and TempDF.at[0, col_voile] <= 0:
            Text += f"{Navire} a dématé.\n"
            print(Text)

        # Sauvegarde
        TempDF.to_csv(path, sep=";", decimal=",", encoding='cp1252', index=False)

        # Construction de l’état à retourner
        etat_navire = {
            "StructureCoque": TempDF.at[0, col_coque] if col_coque in TempDF.columns else None,
            "StructureVoile": TempDF.at[0, col_voile] if col_voile in TempDF.columns else None,
            "Equipage": TempDF.at[0, col_equipage] if col_equipage in TempDF.columns else None,
        }
        print(etat_navire)
        return Pertes, Text

    def GeneEquipage(self, ):
        """
        Génère les compétences d'un équipage avec des nombres aléatoires
        en utilisant numpy pour éviter les répétitions.
        """
        Comps = ["Combat", "Manoeuvre", "Pointage", "Recharge", "Ruse"]
        Text = "Fiche équipage \n"
        Temp = ""
        CompEquipage = {}

        for comp in Comps:
            total_value = 0

            for _ in range(4):  # Boucle pour générer 4 sous-valeurs
                Base = np.random.randint(1, 366)  # Valeur de base
                Metier = np.random.randint(1, 11)  # Métier lié

                # Déterminer la valeur de base en fonction de Base
                if Base < 190:
                    Val = 0
                elif Base < 310:
                    Val = 1
                elif Base < 355:
                    Val = 2
                else:
                    Val = 3

                # Déterminer le bonus en fonction de Metier
                if Metier <= 2:
                    Bonus = 1
                elif Metier <= 6:
                    Bonus = 2
                elif Metier <= 8:
                    Bonus = 3
                else:
                    Bonus = 4

                Res = Val + Bonus
                total_value += Res

            # Calcul de la moyenne des 4 valeurs, convertie en entier
            final_value = utils.ConvertFloatToInt(total_value / 4)
            CompEquipage[comp] = str(final_value)
            Temp += f"Comp : {comp} Valeur : {final_value}\n"

        Text += Temp + "\n"
        self.Equipage = CompEquipage
        return Text, CompEquipage

    def CombatNaval(self, Name1, Munition1, Name2, Munition2):
        Text = ""
        Navire1 = pd.read_csv(BASE_PATH + "/Navire/" + Name1, sep=";", decimal=",", encoding="cp1252")
        Navire1 = Navire1.iloc[0]
        Navire2 = pd.read_csv(BASE_PATH + "/Navire/" + Name2, sep=";", decimal=",", encoding="cp1252")
        Navire2 = Navire2.iloc[0]
        Degat1, Recharge1 = self.DegatsNavire(Name1, Name2, Munition1)
        Degat2, Recharge2 = self.DegatsNavire(Name2, Name1, Munition2)
        Text = Text + Name1 + " a besoin de " + str(Recharge1) + " tours pour recharger sa prochaine batterie \n"
        Text = Text + Name2 + " a besoin de " + str(Recharge2) + " tours pour recharger sa prochaine batterie \n"
        print(Name1 + " a besoin de " + str(Recharge1) + " pour recharger sa prochaine batterie")
        print(Name2 + " a besoin de " + str(Recharge2) + " pour recharger sa prochaine batterie")
        if (Navire1['Equipage'] > 0):
            if Munition2 != "Mitraille":
                Perte1, Temp = self.PerteNavire(Name1, Degat2, Munition2)
                Equipage.Tues(Degat2, Navire1['EquipageNom'])
            else:
                Perte1 = Equipage.Tues(Degat2, Navire1['EquipageNom'])
                Temp = Navire1['EquipageNom'] + " a perdu " + str(Perte1) + " hommes d'équipage \n"
            Text = Text + Temp + "\n"
            Text = Text + Equipage.Attitude(Navire1['EquipageNom'], -Perte1 / Navire1['Equipage'] * 50)[1]
        else:
            print(Name1 + " a ete decimee")
        if (Navire2['Equipage'] > 0):
            if Munition1 != "Mitraille":
                Perte2, Temp = self.PerteNavire(Name2, Degat1, Munition1)
                Equipage.Tues(Degat1, Navire2['EquipageNom'])
            else:
                Perte2 = Equipage.Tues(Degat1, Navire2['EquipageNom'])
                Temp = Navire2['EquipageNom'] + " a perdu " + str(Perte2) + " hommes d'équipage \n"
            Text = Text + Temp + "\n"
            Text = Text + Equipage.Attitude(Navire2['EquipageNom'], -Perte2 / Navire2['Equipage'] * 50)[1]
        else:
            print(Name2 + " a ete decimee")
        print(Name1 + " a perdu " + str(Perte1) + " hommes")

        print(Name2 + " a perdu " + str(Perte2) + " hommes")
        return Text

    # self.RMarchand(SeuilMa,DeMa,SeuilAv,DeAv,NbJour,CompetenceVigie)

    ###Determine l'origine du navire en fonction de sa région de rencontre
    def OrigineNavire(self, RegionCommerce):
        de = random.randint(1, 100)
        Marchandises = pd.read_csv(BASE_PATH + "/Marchandises.csv", sep=";", decimal=",", encoding="cp1252")
        # Filter data for the specified region and "De" range

        Regions = pd.read_csv(BASE_PATH + "/ListeRegions.csv", sep=";", decimal=",", encoding="cp1252")

        RegionNavire = Regions[Regions["RegionsCommerciale"] == RegionCommerce]["RegionsRencontre"].iloc[0]
        RegionCompagnie = Regions[Regions["RegionsCommerciale"] == RegionCommerce]["RegionsCompagnie"].iloc[0]
        filtered_data = Marchandises[
            (Marchandises["Region"] == RegionCommerce) &
            (Marchandises["DeOrigine"] <= de)
            ]

        # Check if there are any matches
        if not filtered_data.empty:
            # Pick the first match (or randomly select from matches)

            # Concatenate 'Cargaison' and 'Suffixe' columns
            Origine = filtered_data["Origine"].iloc[-1]
        else:
            Origine = RegionCommerce
        return Origine, RegionNavire, RegionCompagnie

    def CalculCombatNavire(self, Navire):
        EsperanceParSucces = 0.6 * 0.5
        ValCanon = float(Navire['Valeur canonnade'].iloc[0])
        Pointage = float(Navire['Pointage'].iloc[0])
        DegMoy = 0.9925 * np.exp(0.2298 * (ValCanon - 9.9721 + 2 * Pointage * EsperanceParSucces))
        return Navire['StructureCoque'].iloc[0] * DegMoy / (7 - float(Navire['Recharge'].iloc[0]) * EsperanceParSucces)

    def CalculInteretCombat(self, NavirePirate, NavirePJ):
        Interet = 0
        SeuilCombatInteret = 0.8  ###Ratio de valeur de combat pour lequel le pirate a un interet
        NavirePirate = NavirePirate.iloc[0]
        NavirePJ = NavirePJ.iloc[0]
        RatioCombat = NavirePirate['ValeurCombat'] / NavirePJ['ValeurCombat']
        SeuilMarchandise = 30
        if RatioCombat >= SeuilCombatInteret:
            if (NavirePirate['TonnageMax'] - NavirePirate['Tonnage']) > SeuilMarchandise / RatioCombat:
                Interet = 1

        return Interet

    def BonusVisionHauteurMat(self, CategorieNavire):
        if CategorieNavire == 0:  ##Si c'est une chaloupe, bonus de 5
            Bonus = 5
        if CategorieNavire == 1:  ##Si c'est un sloop, bonus de 8
            Bonus = 8
        if CategorieNavire == 2:  ##Si c'est une géoellte, bonus de 10
            Bonus = 10
        if CategorieNavire == 3:  ##Si c'est un vaisseau de ligne, bonus de 18
            Bonus = 18
        return Bonus

    def ChoixRencontre(self, NavirePJ, NavirePNJ, Distance, Choix, Interet):
        CommerceCapitaine = utils.Compute(1)
        Text = ""
        if Choix == "NeRienFaire":
            if Interet == 0:
                Text += "Vous n'avez rien a faire, le navire s'éloigne de vous et vous continuez votre trajet"
            else:
                Text += "Le navire se rapproche de vous \n"

        LireEcrireCapitaine = utils.Compute(1)
        if Choix == "Poursuivre":
            Navigation.CoursePoursuite(3, Distance)
        ReussiteLire = utils.Test(LireEcrireCapitaine, 0)
        if Choix == "Attaquer":
            Text += "Vous avez choisi d'attaquer le " + NavirePNJ[
                'Name'] + "\n Veuillez vous rendre dans l'onglet BatailleNavale et sélectionnez les navires combattants ainsi que vos munitions \n"
        ReussiteCommerce = utils.Test(CommerceCapitaine, 0)
        if Choix == "Commercer":
            if "Pirate" in NavirePNJ['Allegence'] or "Interlope" in NavirePNJ['Allegence']:
                TauxVente = 80 - ReussiteCommerce * 10
                TauxAchat = 100 + ReussiteCommerce * 10
                Text += (
                            "Vous pouvez acheter ou vendre des marchandises au capitaine, faites un text de Commerce sous Expression,"
                            " \n vous pouvez vendre à ") + str(
                    TauxVente) + " plus votre reussite*10 % \n et acheter à " + str(
                    TauxAchat) + "moins votre reussite*10 % \n"

            else:
                Result = random.randint(1, 10)
                if Result < 2:
                    Text += "Le capitaine n'est pas intéressé pour commerce avec vous, vous continuez votre trajet séparemment \n"
                else:
                    Text += "Le capitaine vous demande les papiers de provenance de vos marchandises avant de vous conseille le port le plus proche pour écouler votre matrchandise\n"
                    if ReussiteLire > 1:
                        Text += "\n si c'est un faux,  vous devez générer une bataille terrestre entre " + NavirePJ[
                            'EquipageNom'] + " et " + NavirePNJ['EquipageNom'] + (""
                                                                                  " \n si vous perdez, la partie est terminée pour vous, si vous gagnez vous pouvez piller le navire et ou récupérer également le navire si il vous reste assez d'hommes \n")

        Text = Text + " \n si vous avez effectué, toutes les actions exigées ou souhaitées, vous pouvez fermer la fenêtre ! \n"
        messagebox.showinfo(
            "Résultat",
            Text
        )
        return Text

    def DeterminationParametre(self, Periode, RegionMaritime):
        Regions = pd.read_csv(BASE_PATH + "/ListeRegions.csv", sep=";", encoding='cp1252', decimal=",")
        ZoneCompagnie = Regions[Regions["RegionsCommerciale"] == RegionMaritime]["RegionsCompagnie"].iloc[0]
        ZoneNavire = Regions[Regions["RegionsCommerciale"] == RegionMaritime]["RegionsRencontre"].iloc[0]
        Comp = random.randint(1, 100)
        Parametres = pd.read_csv(BASE_PATH + '/CompagnieCommerciale.csv', sep=";", encoding='cp1252', decimal=",")
        Parametres = Parametres[Parametres['Zone'] == ZoneCompagnie]
        Parametres = Parametres[Periode <= Parametres['PeriodMax']]
        Parametres = Parametres[Comp <= Parametres['Intervalle']]
        Parametres = Parametres.iloc[0]
        Parametres["Compagnie"] = Parametres["Acteur"] + Parametres["Nationalite"]
        Navire = random.randint(1, 100)
        Navires = pd.read_csv(BASE_PATH + "/GeneNavire.csv", sep=";", encoding='cp1252', decimal=",")
        Navires = Navires[Navires['Zone'] == ZoneNavire]
        print(Navires)
        Navire = Navires[Navire <= Navires['DeBateau']]["Bateau"].iloc[0]
        Navire = self.CheckNavire(Navire)
        Parametres["Navire"] = Navire
        return Parametres

    def Escale(self, RegionMaritime, Port, Navire, Action, SuccesAction):
        NomNavire = Navire
        NavireDF = pd.read_csv(NAVIRE_PATH + NomNavire + ".csv", sep=";", encoding="cp1252", decimal=",")
        Navire = NavireDF.iloc[0]
        ReparCoque = Navire['StructureCoqueMax'] - Navire['StructureCoque']
        ReparVoile = Navire['StructureVoileMax'] - Navire['StructureVoile']
        NbJourReparation = 0
        NbJourEscale = 0
        Text = ""
        if Action == "Reparer":
            CompCharpentier = utils.Compute(1)
            Cout = (ReparCoque + ReparCoque) / (Navire['StructureCoqueMax'] + Navire['StructureVoileMax']) * Navire[
                'Cout']
            Navire['StructureCoque'] = Navire['StructureCoqueMax']
            Navire['StructureVoile'] = Navire['StructureVoileMax']
            for k in range(ReparCoque + ReparVoile):
                NbJourReparation += utils.TestValeurNonNumerique(CompCharpentier, 0)[0]
            NbJourEscale = max(NbJourReparation, NbJourEscale)
            NavireDF.iloc[0] = Navire
            NavireDF.to_csv(NAVIRE_PATH + NomNavire + ".csv", sep=";", encoding="cp1252", decimal=",", index=False)
            Text += "Votre navire est réparé pour un cout de " + str(Cout) + " pièces de huit en " + str(
                NbJourEscale) + "jours \n"
        if Action == "Recruter":
            NbHommes = 0
            Navire = self.RencontreNavire(1, RegionMaritime, 0, "Defaut")[0].iloc[0]
            NbHommes += Navire['Equipage']
            NbHommesRecrute = NbHommes / 10 * SuccesAction
            Text += Equipage.Recrute(NbHommesRecrute, "Matelot", Navire, 0)
        if Action == "Acheter":
            Marchandises = Marchandise.TrouverMarchand(RegionMaritime)[2]

        return Text

    def FicheNavire(self, Name, Navire, Marchandises):
        # Ouvrir le fichier
        wb = load_workbook(BASE_PATH + "/FicheNavire.xlsx")

        # Sélectionner la feuille
        ws = wb["Fiche"]
        Navire = Navire.iloc[0]
        # Remplir des cellules
        ws["B2"] = Name
        ws["D3"] = Navire['RegionsDepart']
        ws["D2"] = Navire['Allegence']
        ws["B4"] = Navire['Nom']
        ws["D4"] = Navire['Pirate']
        ws["G2"] = Navire['Manoeuvre']
        ws["G4"] = Navire['Combat']
        ws["G5"] = Navire['Pointage']
        ws["G6"] = Navire['Recharge']
        ws["G7"] = Navire['Ruse']
        ws["G8"] = Navire['ValeurCombat']
        ws["B13"] = Navire['NbCanons']
        ws["B12"] = Navire['Valeur canonnade']
        ws["B10"] = Navire['StructureCoque']
        ws["B11"] = Navire['StructureVoile']
        ws["D5"] = Navire['EquipageNom']
        ws["G10"] = Navire['Longueur']
        ws["G11"] = Navire['NbMats']
        ws["G12"] = Navire['CategorieNavire']
        ws["G13"] = Navire['Longueur']
        ws["B16"] = Navire['Pres']
        ws["B17"] = Navire['Largue']
        ws["B18"] = Navire['Grand largue']
        ws["B19"] = Navire['Vent arriere']
        ws["B20"] = Navire['Vitesse moyenne']
        ws["B21"] = Navire['TonnageMax']
        ws["B22"] = Navire['Tonnage']
        ws["B7"] = Navire['Equipage']
        ws["B6"] = Navire['Reputation']
        row = 26
        for key, value in Marchandises.items():
            ws.cell(row=row, column=1).value = key
            ws.cell(row=row, column=2).value = value
            row += 1
        # Sauvegarder
        wb.save(BASE_PATH + "/Rencontre/" + Name + ".xlsx")

    def FormulaireRencontre(self, NavirePJ, NavirePNJ, Distance, Text, Interet):

        root1 = tk.Toplevel()
        root1.title("FormulaireRencontre")
        root1.geometry("600x200")

        # Texte en haut
        label_text = tk.Label(
            root1,
            text=Text,
            wraplength=550,
            justify="left"
        )
        label_text.pack(pady=20)

        # Cadre contenant les boutons
        frame_actions = tk.Frame(root1)
        frame_actions.pack(pady=10)

        Actions = [
            "NeRienFaire",
            "Poursuivre",
            "Attaquer",
            "Commercer"
        ]

        def executer_choix(choix):
            TextResultat = self.ChoixRencontre(
                NavirePJ,
                NavirePNJ,
                Distance,
                choix, Interet
            )

            messagebox.showinfo(
                "Résultat",
                TextResultat
            )

            root1.destroy()

        # Création des boutons sur une seule ligne
        for k in Actions:
            bouton = tk.Button(
                frame_actions,
                text=k,
                command=lambda choix=k: executer_choix(choix)
            )

            bouton.pack(
                side="left",
                padx=5
            )

        # Bloque les interactions avec les autres fenêtres
        root1.grab_set()

        # Attend que la fenêtre soit fermée
        root1.wait_window()








































