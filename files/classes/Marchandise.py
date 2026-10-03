# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:05:00 2023

@author: USER
"""

import random

import os

import pandas as pd

import config





class Marchandise:

    def __init__(self):

        self.Cargaisons = []
        self.Name = "Test.csv"


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
        for cargaison in self.Cargaisons:
            if k in cargaison["Cargaison"]:
                cargaison["PrixNormal"] = Valeur
                cargaison["PrixExces"] = Valeur
                cargaison["PrixPenurie"] = Valeur

        return self

    def CalculMonetaireMarchandise(
            self,
            cargaison,
            tonnage_navire,
            nb_canons,
            succes,
            port):
        BonusAleaNPort = cargaison["ModRichesseNormal"]
        BonusNPort = cargaison["BonusRichesseNormal"]

        BonusAleaPort = cargaison["ModRichessePort"]
        BonusPort = cargaison["BonusRichessePort"]

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

    def AjoutMarchandise(self, nom, tonnage):

        catalogue = pd.read_csv(
            config.BASE_PATH + "/Marchandises.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        ligne = catalogue[catalogue["Cargaison"] == nom]

        if ligne.empty:
            return

        ligne = ligne.iloc[0].to_dict()

        ligne["Tonnage"] = tonnage

        for cargaison in self.Cargaisons:

            if cargaison["Cargaison"] == nom:
                cargaison["Tonnage"] += tonnage
                return

        self.Cargaisons.append(ligne)

    def SupprimerMarchandise(self, nom, tonnage):

        for cargaison in self.Cargaisons:

            if cargaison["Cargaison"] == nom:

                cargaison["Tonnage"] -= tonnage

                if cargaison["Tonnage"] <= 0:
                    self.Cargaisons.remove(cargaison)

                return True

        return False

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

    def GenerateMarchandise(self, region):

        de = random.randint(1, 100)

        marchandises = pd.read_csv(
            config.BASE_PATH + "/Marchandises.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        ligne = marchandises[
            (marchandises["Region"] == region)
            & (marchandises["De"] >= de)
            ]

        if ligne.empty:
            ligne = marchandises[
                marchandises["Region"] == region
                ]

        return ligne.iloc[0].to_dict()

    def sauvegarder(self, name=None):

        if name is None:
            name = self.Name

        df = pd.DataFrame(self.Cargaisons)

        df.to_csv(
            os.path.join(config.BASE_PATH, "Marchandise", f"{name}.csv"),
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )

    @classmethod
    def charger_depuis_csv(cls, nom_fichier):

        chemin = os.path.join(
            config.BASE_PATH,
            "Marchandise",
            f"{nom_fichier}.csv"
        )

        if not os.path.exists(chemin):
            return None

        obj = cls()
        obj.Name = nom_fichier

        df = pd.read_csv(
            chemin,
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        obj.Cargaisons = df.to_dict("records")

        return obj

    def get_actions(self):        return ["Acheter", "Vendre", "Piller"]
    def executer_action(self, action,instance,valeurs=None):

        if action == "Vendre":
            self.SupprimerMarchandise(valeurs["Cargaison"],valeurs['Tonnage'])
            self.sauvegarder(self.Name)

        elif action == "Acheter":
            vendeur = Marchandise.charger_depuis_csv(
                valeurs["Marchandise"]
            )

            vendeur.SupprimerMarchandise(
                valeurs["Cargaison"],
                valeurs["Tonnage"]
            )

            self.AjoutMarchandise(
                valeurs["Cargaison"],
                valeurs["Tonnage"]
            )

            vendeur.sauvegarder(vendeur.Name)
            self.sauvegarder(self.Name)

        return f"{action} effectué."