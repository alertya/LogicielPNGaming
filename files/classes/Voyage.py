import os
import csv
import pandas as pd
import config

class Voyage:

    def __init__(self, Nom="", Navire="", Annee=1715,etapes=None):
        self.Name = Nom
        self.Navire = Navire
        self.Annee = Annee
        self.Etapes = etapes if etapes is not None else []

        self.EtapeCourante = 0
        self.Avancement = 0
        self.Jour = 1
        self.Journal = {
            1: []}

    def AjouterEtape(
            self,
            Region,
            Distance,
            ZoneMaritime="",
            TaillePortEscale="",
            ChanceRencontreAventurier=0,
            DeAventurier=0,
            CompetenceVigie=0):

        self.Etapes.append({
            "Region": Region,
            "Distance": Distance,
            "ZoneMaritime": ZoneMaritime,
            "TaillePortEscale": TaillePortEscale,
            "ChanceRencontreAventurier": ChanceRencontreAventurier,
            "DeAventurier": DeAventurier,
            "CompetenceVigie": CompetenceVigie
        })

    def Affichage(self):

        lignes = []

        for i, etape in enumerate(self.Etapes, start=1):
            lignes.append({
                "Ordre": i,
                "Région": etape["Region"],
                "Distance": etape["Distance"],
                "Zone": etape.get("ZoneMaritime", ""),
                "Port": etape.get("TaillePortEscale", "")
            })

        return {
            "Nom": self.Name,
            "Navire": self.Navire,
            "Année": self.Annee,
            "Jour": self.Jour,
            "Journal": "\n".join(self.Journal.get(self.Jour, [])),
            "Étapes": lignes
        }
    def sauvegarder(self, nom=None):
        nom = nom or self.Name

        lignes = []

        for i, etape in enumerate(self.Etapes, start=1):
            ligne = etape.copy()  # copie du dictionnaire de l'étape
            ligne["NomTrajet"] = nom
            ligne["Navire"] = self.Navire
            ligne["Annee"] = self.Annee
            ligne["Ordre"] = i
            lignes.append(ligne)

        df = pd.DataFrame(lignes)

        df.to_csv(
            os.path.join(config.BASE_PATH, "Voyage", f"{nom}.csv"),
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )



    @classmethod
    def charger_depuis_csv(cls, nom):

        fichier = os.path.join(config.BASE_PATH, "Voyage", nom + ".csv")
        if not os.path.exists(fichier):
            return None
        df = pd.read_csv(
            fichier,
            sep=";",
            decimal=",",
            encoding="cp1252"
        )
        voyage = cls(
            df["NomTrajet"][0],
            df["Navire"][0],
            df["Annee"][0]
        )

        for _, ligne in df.iterrows():
            voyage.AjouterEtape(
                Region=ligne["Region"],
                Distance=ligne["Distance"],
                ZoneMaritime=ligne["ZoneMaritime"],
                TaillePortEscale=ligne["TaillePortEscale"],
                ChanceRencontreAventurier=ligne["ChanceRencontreAventurier"],
                DeAventurier=ligne["DeAventurier"],
                CompetenceVigie=ligne["CompetenceVigie"]
            )

        return voyage

    def Affichage(self):

        return {
            "Informations": {
                "Nom": self.Name,
                "Navire": self.Navire,
                "Année": self.Annee,
                "Jour": self.Jour
            },

            "Etapes": {
                "type": "tableau",
                "colonnes": [
                    "Ordre",
                    "Région",
                    "Distance"
                ],
                "donnees": [
                    (
                        i + 1,
                        e["Region"],
                        e["Distance"]
                    )
                    for i, e in enumerate(self.Etapes)
                ]
            },

            "Journal": self.Journal.get(self.Jour, [])
        }