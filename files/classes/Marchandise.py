# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:05:00 2023

@author: USER
"""

import numpy as np
import random
import warnings
import time
import csv
import os
import sys
import math
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import messagebox
import utils
import config




class Marchandise:

    def __init__(self):

        self.Cargaison = "Rhum"
        self.Region = "Europe du nord"
        self.Volume = 1
        self.PrixPenurie=150
        self.PrixNormal=100
        self.PrixExces=1
        self.Densite=1
        self.Tonnage=1
        self.ModRichesseNormal=1
        self.ModRichessePort=1
        self.BonusRichesseNormal=1
        self.BonusRichessePort=1
        self.ID=1
        self.Name='Test.csv'


    def ConvertRancon(self,Nombre):
        Rancon = pd.read_csv(config.BASE_PATH + "/ValeursRancon.csv", sep=";", decimal=",", encoding="cp1252")
        Rancon = Rancon[Rancon['ValeurDe'] >= Nombre]
        Rancon = Rancon.iloc[0]
        return Rancon

    def PossessionPieceHuit(self):
        Base=114
        Bonus=random.randint(0,90)
        return Base+Bonus

    def CheckButin(self,TonnageNavire,NbCanons,Port,SuccesCommerce):
        ListButins=['de marque','de monnaie','Esclave','Pèlerin']
        Valeur=self.CalculMonetaireMarchandise(TonnageNavire,NbCanons,SuccesCommerce,Port)
        Valeur=Valeur['PieceDeHuit']
        for k in ListButins:
            if k in self.Nom:
                self.__setattr__("PrixNormal",Valeur)
                self.__setattr__("PrixExces", Valeur)
                self.__setattr__("PrixPenurie", Valeur)

        return self

    def CalculMonetaireMarchandise(self,TonnageNavire,NbCanonsNavire, ReussiteCommerce,Port):
        De=random.randint(2,200)
        TonnageNavire=TonnageNavire/10
        ReussiteCommerce=ReussiteCommerce*10


        BonusAleaNPort=self.ModRichesseNormal
        BonusNPort=self.BonusRichesseNormal
        BonusAleaPort=self.ModRichessePort
        BonusPort=self.BonusRichessePort
        if Port == 1:
            BonusAlea = max(BonusAleaNPort, BonusAleaPort)
            Bonus = max(BonusPort, BonusNPort)
        else:
            BonusAlea = BonusAleaNPort
            Bonus = BonusNPort


        BonusAlea = random.randint(1, int(BonusAlea))
        Bonus += BonusAlea
        De=De+Bonus
        De+=NbCanonsNavire+TonnageNavire+ReussiteCommerce
        Valeur=self.ConvertRancon(De)
        return Valeur

    def CalculTaillePort(self,Ville):
        CompNegatif = ['Maladie', 'Vide', 'IndigeneHostile']
        CompNeutre = ['SympathisantPirate']

        # Charger les données
        Ports = pd.read_csv(config.BASE_PATH+"/CaracterePort.csv", sep=";", decimal=",", encoding="cp1252")

        # Copie pour éviter de modifier l'original directement
        df = Ports.copy()

        # Normaliser chaque colonne (sauf 'Ville')
        colonnes_a_normaliser = [col for col in df.columns if col != 'Ville']
        for col in colonnes_a_normaliser:
            somme = df[col].sum()
            if somme != 0:
                df[col] = df[col] / somme
            else:
                df[col] = 0  # Évite division par 0

        # Calcul du score par ligne
        def score_ligne(row):
            score = 0
            for col in colonnes_a_normaliser:
                if col in CompNegatif:
                    score -= row[col]
                elif col in CompNeutre:
                    continue  # score neutre
                else:
                    score += row[col]
            return score

        df['Score'] = df.apply(score_ligne, axis=1)
        TaillePort=df[df['Ville']==Ville]
        return TaillePort

    def AjoutMarchandise(self,Name, TonnageMarchandise):
        # Chargement de toutes les marchandises disponibles
        MarchandisesDisponibles = pd.read_csv(config.BASE_PATH + "/Marchandises.csv", sep=";", decimal=",", encoding="cp1252")

        # Filtrage sur la marchandise choisie
        ligne_marchandise = MarchandisesDisponibles[MarchandisesDisponibles['Cargaison'] == NameMarchandise].copy()

        # Ajout des colonnes nécessaires
        ligne_marchandise['Tonnage'] = TonnageMarchandise
        ligne_marchandise['Cours'] = 0

        # Chemin du fichier de cargaison du navire
        output_path = os.path.join(config.MARCHANDISE_PATH, Name )
        os.makedirs(config.MARCHANDISE_PATH, exist_ok=True)

        # Si le fichier existe déjà, on met à jour ou ajoute
        if os.path.exists(output_path):
            existing_df = pd.read_csv(output_path, sep=";", decimal=",", encoding="cp1252")

            # Si la marchandise est déjà présente
            if NameMarchandise in existing_df['Cargaison'].values:
                existing_df.loc[existing_df['Cargaison'] == NameMarchandise, 'Tonnage'] += 1
            else:
                existing_df = pd.concat([existing_df, ligne_marchandise], ignore_index=True)

            # Sauvegarde
            existing_df.to_csv(output_path, sep=";", decimal=",", encoding="cp1252", index=False)

        else:
            # Fichier inexistant → création avec la marchandise
            ligne_marchandise.to_csv(output_path, sep=";", decimal=",", encoding="cp1252", index=False)

        return ligne_marchandise
    def SupprimerMarchandise(self, Name, quantite=1):
        """
        Retire `quantite` de tonnage à la marchandise `NameMarchandise` dans le fichier `Name.csv`.
        Si le tonnage devient <= 0, la ligne est supprimée.
        """

        file_path = os.path.join(config.MARCHANDISE_PATH, Name+".csv")

        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas.")
            return False

        try:
            df = pd.read_csv(file_path, sep=";", decimal=",", encoding="cp1252")
        except pd.errors.EmptyDataError:
            print(f"Le fichier {file_path} est vide.")
            return False

        if 'Cargaison' not in df.columns or 'Tonnage' not in df.columns:
            print(f"Les colonnes 'Cargaison' ou 'Tonnage' sont absentes dans {file_path}.")
            return False

        # Trouver les lignes correspondant à la marchandise ciblée
        mask = df['Cargaison'] == NameMarchandise

        if not mask.any():
            print(f"Aucune ligne pour la marchandise '{NameMarchandise}' trouvée dans {file_path}.")
            return False

        # Décrémenter le tonnage
        df.loc[mask, 'Tonnage'] = df.loc[mask, 'Tonnage'] - quantite

        # Supprimer les lignes où tonnage <= 0
        df = df[df['Tonnage'] > 0]

        # Réécrire le fichier
        df.to_csv(file_path, sep=";", decimal=",", encoding="cp1252", index=False)

        print(f"Retiré {quantite} de tonnage à '{NameMarchandise}' dans {Name}.csv.")
        return True



    def Pillage(self,NomNavirePillant,NomNavirePille):
        NavirePillant=pd.read_csv(os.path.join(config.BASE_PATH, "Navire", NomNavirePillant), sep=";",
                                   decimal=",", encoding="cp1252")
        TonnageMax=NavirePillant['TonnageMax']-NavirePillant['Tonnage']
        TonnageMax=TonnageMax.iloc[0]
        MarchandisePille=pd.read_csv(os.path.join(config.BASE_PATH, "Marchandise", "Marchandise_"+NomNavirePille ), sep=";",
                                   decimal=",", encoding="cp1252")

        MarchandisePillant=pd.read_csv(os.path.join(config.BASE_PATH, "Marchandise", "Marchandise_"+NomNavirePillant ), sep=";",decimal=",", encoding="cp1252")

        # Remplacer les NaN (vides ou erreurs) par 0
        MarchandisePille["PrixNormal"] = MarchandisePille["PrixNormal"].fillna(0)
        #MarchandisePille = MarchandisePille.sort_values(by="PrixNormal", ascending=False)
        while (not MarchandisePille.empty and TonnageMax > 0):
            MarchandisePille = pd.read_csv(os.path.join(config.BASE_PATH, "Marchandise", "Marchandise_" + NomNavirePille),
                                           sep=";",
                                           decimal=",", encoding="cp1252")
            MarchandiseNom=MarchandisePille['Cargaison'].iloc[0]
            self.AjoutMarchandise(MarchandiseNom,1,"Marchandise_"+NomNavirePillant)
            self.SupprimerMarchandise(MarchandiseNom, "Marchandise_"+NomNavirePille, 1)
            NavirePillant['Tonnage']+=1
            TonnageMax-=1
        MarchandisePillant.to_csv(os.path.join(config.BASE_PATH, "Marchandise", "Marchandise_"+NomNavirePillant), sep=";",
                                   decimal=",", encoding="cp1252")

        MarchandisePille.to_csv(os.path.join(config.BASE_PATH, "Marchandise", "Marchandise_" + NomNavirePille),
                                       sep=";",
                                       decimal=",", encoding="cp1252")

        NavirePillant.to_csv(os.path.join(config.BASE_PATH, "Navire", NomNavirePillant), sep=";",
                                    decimal=",", encoding="cp1252")




        Text="Le pillage du navire "+NomNavirePille+ " a ete realise"
        return Text

    def RetourMarchandise(self,Tonnage,Region):
        Marchandises=pd.read_csv(config.BASE_PATH+"/Marchandises.csv", sep=";", decimal=",", encoding="cp1252")
        Volum=-999
        Total = 0
        Cargaison=[]
        Chargement={}
        while Volum < 0:
            # Generate a random number for filtering
            de = random.randint(1, 100)
            # Filter data for the specified region and "De" range
            filtered_data = Marchandises[
                (Marchandises["Region"] == Region) &
                (Marchandises["De"] <= de)

                ]


            # Check if there are any matches
            if not filtered_data.empty:
                # Pick the first match (or randomly select from matches)
                # Concatenate 'Cargaison' and 'Suffixe' columns
                libelle = filtered_data["Cargaison"].iloc[-1]
                if libelle in Chargement:
                    Chargement[libelle] += filtered_data["Volume"].iloc[-1]
                else:
                    Chargement[libelle] =filtered_data["Volume"].iloc[-1]
                Ratio=filtered_data['Volume']
                Cargaison.append(libelle)
                # Randomly generate a volume check
                des = random.randint(1, 10)
                Total=Total+filtered_data["Volume"].iloc[-1]
                if des <= filtered_data["Volume"].iloc[-1]:
                    Volum = 1

        divisor=Total

        Chargement= {key: value / divisor*Tonnage for key, value in Chargement.items()}
        return Chargement


    def GetMarchandise(self,Nom):
        Marchandises=pd.read_csv(config.BASE_PATH + "/Marchandises.csv",encoding="cp1252",decimal=",",sep=";")
        donnees = Marchandises[
            Marchandises["Cargaison"].str.contains(Nom, na=False)
        ].iloc[0].to_dict()
        objet=Marchandise()
        for attribut, valeur in donnees.items():
            setattr(objet,attribut, valeur)
        return objet
    def GenerateMarchandise(self,Region):
        de=random.randint(1,100)
        Marchandises = pd.read_csv(config.BASE_PATH + "/Marchandises.csv", encoding="cp1252", decimal=",",
                                   sep=";")


        donnees = Marchandises[Marchandises["Region"] == Region]
        donnees=donnees[donnees["De"]>=de].iloc[0]
        objet = Marchandise()
        for attribut, valeur in donnees.items():
            setattr(objet, attribut, valeur)
        return objet



    def sauvegarder(self,Name):

        ligne = {}

        for cle, valeur in self.__dict__.items():
            ligne[cle] = valeur

        df = pd.DataFrame([ligne])

        df.to_csv(
            os.path.join(config.BASE_PATH, "Marchandise", f"{Name}.csv"),
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
            "Marchandise",
            f"{nom_fichier}.csv"
        )

        if not os.path.exists(chemin_fichier):
            print(f"Le fichier {chemin_fichier} n'existe pas.")
            return None

        # Création d'un objet Marchandise vide
        marchandise = cls()

        import pandas as pd

        df = pd.read_csv(
            chemin_fichier,
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        if df.empty:
            return marchandise

        # Dernière ligne du fichier
        donnees = df.iloc[-1]

        for cle, valeur in donnees.items():

            if not hasattr(marchandise, cle):
                continue

            # Ignore les valeurs manquantes
            if pd.isna(valeur):
                continue

            setattr(marchandise, cle, valeur)

        return marchandise

    def get_actions(self):        return ["Acheter", "Vendre", "Piller"]
    def executer_action(self, action,valeurs=None):

        if action == "Vendre":
            self.SupprimerMarchandise(valeurs["Marchandise"],valeurs['Tonnage'])
            self.sauvegarder(self.Name)

        elif action == "Acheter":
            self.AttribuerRole()
            self.sauvegarder(self.Name)
        elif action == "Piller":
            self.Pillage(NameMarchandisePillant,self.Name)
            self.sauvegarder(self.Name)
            self.sauvegarder(NameMarchandisePillant)
        return f"{action} effectué."