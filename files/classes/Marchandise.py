# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:05:00 2023

@author: USER
"""

import random

import os

import pandas as pd

import config

import utils
from pandas.errors import EmptyDataError


class Marchandise:

    def __init__(self):

        self.Cargaisons = []
        self.Name = "TestMarchandise.csv"

    def Affichage(self):
        return {
            "Cargaison": {
                "type": "tableau",
                "colonnes": ["Marchandise", "Tonnage", "Prix"],
                "donnees": [
                    {
                        "Marchandise": c["Nom"],
                        "Tonnage": c["Tonnage"],
                        "Prix": c["PrixNormal"],
                    }
                    for c in self.Cargaisons
                ]
            }
        }
    def ConvertRancon(self,Nombre):
        Rancon = utils.VALEUR_RANCON
        Rancon = Rancon[Rancon['ValeurDe'] >= Nombre]
        Rancon = Rancon.iloc[0]
        return Rancon

    def PossessionPieceHuit(self):
        Base=114
        Bonus=random.randint(0,90)
        return Base+Bonus


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
        Ports = utils.CARACTERE_PORT

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
    @staticmethod
    def AjoutMarchandise(Acheteur, NomMarchandise, tonnage):
        catalogue = utils.MARCHANDISES

        ligne = catalogue[catalogue["Cargaison"] == NomMarchandise]

        if ligne.empty:
            return

        ligne = ligne.iloc[0].to_dict()

        ligne["Tonnage"] = tonnage

        for cargaison in Acheteur.Cargaisons:

            if cargaison["Cargaison"] == NomMarchandise:
                cargaison["Tonnage"] += tonnage
                Acheteur.sauvegarder(Acheteur.Name)
                return

        Acheteur.Cargaisons.append(ligne)
        Acheteur.sauvegarder(Acheteur.Name)


    def SupprimerMarchandise(self, nom_marchandise, tonnage):

        for cargaison in self.Cargaisons:

            if cargaison["Cargaison"] == nom_marchandise:

                cargaison["Tonnage"] -= tonnage

                if cargaison["Tonnage"] <= 0:
                    self.Cargaisons.remove(cargaison)

                return True

        return False

    def RetourMarchandise(self,Tonnage,Region):
        Marchandises=utils.MARCHANDISES
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

        marchandises =utils.MARCHANDISES
        ligne = marchandises[
            (marchandises["Region"] == region)
            & (marchandises["De"] >= de)
            ]

        if ligne.empty:
            ligne = marchandises[
                marchandises["Region"] == region
                ]
        self.sauvegarder(self.Name)
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
        print("CHARGEMENT MARCHANDISE :", nom_fichier)
        chemin = os.path.join(
            config.BASE_PATH,
            "Marchandise",
            f"{nom_fichier}.csv"
        )

        obj = cls()
        obj.Name = nom_fichier

        if not os.path.exists(chemin):
            obj.Cargaisons = []
            return obj

        try:
            df = pd.read_csv(
                chemin,
                sep=";",
                decimal=",",
                encoding="cp1252"
            )
            obj.Cargaisons = df.to_dict("records")

        except EmptyDataError:
            obj.Cargaisons = []

        return obj

    def get_actions(self):        return ["Acheter", "Vendre", "Piller"]
    def executer_action(self, action,instance,valeurs=None):
        vendeur = Marchandise.charger_depuis_csv(valeurs['Vendeur'])

        if action == "Vendre":
            vendeur.SupprimerMarchandise(valeurs["Cargaison"],valeurs['Tonnage'])
            vendeur.sauvegarder(vendeur.Name)
            return f"La vente de {valeurs["Tonnage"]} de {valeurs["Cargaison"]} a ete effectué. \n"
        if action == "Acheter":
            acheteur = Marchandise.charger_depuis_csv(valeurs['Acheteur'])
            vendeur.SupprimerMarchandise(
                valeurs["Cargaison"],
                valeurs["Tonnage"]
            )

            acheteur.AjoutMarchandise(acheteur,
                valeurs["Cargaison"],
                valeurs["Tonnage"]
            )

            vendeur.sauvegarder(vendeur.Name)
            acheteur.sauvegarder(acheteur.Name)
            return f"L'achat de {valeurs["Tonnage"]} de {valeurs["Cargaison"]} auprès de {vendeur.Name} a ete effectué.\n Les marchandises supplémentaires ont été ajoutées à {acheteur.Name} \n"
        if action == "Piller":

            acheteur = Marchandise.charger_depuis_csv(valeurs['Acheteur'])
            for cargaison in vendeur.Cargaisons.copy():
                acheteur.AjoutMarchandise(acheteur,
                    cargaison["Cargaison"],
                    cargaison["Tonnage"]
                )
                vendeur.SupprimerMarchandise(
                    cargaison["Cargaison"],
                    cargaison["Tonnage"]
                )

            vendeur.sauvegarder()
            acheteur.sauvegarder()
            return f"Le pillage de {vendeur.Name} a ete effectué.\n Les marchandises supplémentaires ont été ajoutées à {acheteur.Name} \n"
        return f"{action} effectué."

    def changer_cargaison(self, event=None):
        nom = self.variables["Cargaison"].get()

        ligne = utils.MARCHANDISES[
            utils.MARCHANDISES["Cargaison"] == nom
            ].iloc[0]

        self.var_prix_exces.set(ligne["PrixExces"])
        self.var_prix_normal.set(ligne["PrixNormal"])
        self.var_prix_penurie.set(ligne["PrixPenurie"])

    @classmethod
    def Generer(cls, nom_stock, nom_marchandise, tonnage):

        marchandise = cls()

        marchandise.Name = nom_stock

        marchandise.AjouterMarchandise(
            nom_marchandise,
            tonnage
        )

        marchandise.sauvegarder()

        return "Marchandise générée."