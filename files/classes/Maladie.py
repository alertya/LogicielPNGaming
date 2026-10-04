from classes.Equipage import Equipage
import pandas as pd
import numpy as np
import random
import os
import config
import utils
from types import SimpleNamespace
class Maladie:

    @staticmethod
    def test_maladie(equipage_nom, nb_jours=1, endemique=False):



        texte = ""

        texte += Maladie.evolution_maladies(equipage_nom, nb_jours)
        equipage = Equipage.charger_depuis_csv(equipage_nom)


        for _ in range(nb_jours):

            for membre in equipage.Membres:

                if membre.Maladie != "":
                    continue

                chance = 140 if endemique else 600

                if random.randint(1, chance) != 1:
                    continue
                maladie = Maladie.TirerMaladie()
                if utils.Test(2, maladie.Virulence) < 2:

                    membre.Maladie = maladie.Nom
                    membre.EtatMaladie = maladie.EtatCrise
                    membre.Cycle = maladie.Cycle

                    texte += (
                        f"{membre.Nom} contracte la {maladie.Nom}.\n"
                    )

        equipage.Save(equipage_nom)

        return texte

    @staticmethod
    def evolution_maladies(equipage_nom, nb_jours):
        equipage = Equipage.charger_depuis_csv(equipage_nom)
        texte = ""

        maladies = utils.MALADIES

        for _ in range(nb_jours):

            morts = []

            for membre in equipage.Membres:

                if membre.Maladie == "":
                    continue

                membre.Cycle -= 1

                if membre.Cycle > 0:
                    continue

                mal = maladies[
                    maladies["Maladie"] == membre.Maladie
                    ].iloc[0]

                membre.Cycle = mal["Cycle"]

                succes = utils.Test(
                    2,
                    mal["Virulence"]
                )

                if succes <= 0:

                    membre.EtatMaladie += mal["ReductionEtat"]

                    if membre.EtatMaladie < -5:
                        morts.append(membre)
                        texte += (
                            f"{membre.Nom} succombe à la {membre.Maladie}.\n"
                        )

                elif succes > 1:

                    membre.EtatMaladie += 1

                    if membre.EtatMaladie >= 0:
                        texte += (
                            f"{membre.Nom} guérit de la {membre.Maladie}.\n"
                        )

                        membre.Maladie = ""
                        membre.EtatMaladie = 0

            for mort in morts:
                equipage.Membres.remove(mort)

        equipage.Save(equipage_nom)

        return texte

    @staticmethod
    def preparation_repas(equipage_nom):
        """
        Renvoie le nombre de repas préparés pendant une journée.
        """

        equipage = Equipage.charger_depuis_csv(equipage_nom)

        repas = 0
        repas_par_succes = 5

        for _ in range(8):  # 8 heures de cuisine

            for membre in equipage.Membres:

                if "Cuisinier" not in str(membre.Traits):
                    continue
                else:
                    succes = utils.Test(membre.Cuisine, 0)
                    repas += succes * repas_par_succes
        equipage.Save(equipage_nom)
        return max(0, repas)

    @staticmethod
    def impact_famine(equipage_nom):

        equipage = Equipage.charger_depuis_csv(equipage_nom)

        texte = ""

        repas = Maladie.preparation_repas(equipage_nom)

        nb_hommes = len(equipage.Membres)

        if nb_hommes == 0:
            return ""

        # Moral
        if repas < nb_hommes:
            equipage.Attitude(
                -2 * (1 - repas / nb_hommes)
            )

        # Nombre d'hommes n'ayant pas mangé
        manque = max(0, nb_hommes - repas)

        for _ in range(manque):

            membre = random.choice(equipage.Membres)

            membre.Famine -= 1

            texte += (
                f"{membre.Nom} souffre de la faim.\n"
            )

            if membre.Famine <= -30:

                membre.Maladie = "Famine"

                if membre.EtatMaladie == 0:
                    membre.EtatMaladie = -1

        equipage.Save(equipage_nom)

        return texte
    def JourMaladie(self,NbJour,NomEquipage):

        Text=""
        Text+=self.evolution_maladies(NomEquipage,NbJour)
        Text+=self.impact_famine(NomEquipage)

        Text+=self.test_maladie(NomEquipage,NbJour,1)
        Text+=self.ReconnaissanceMaladie(NomEquipage)
        return Text
    @staticmethod
    def ReconnaissanceMaladie(nom_equipage):
        equipage = Equipage.charger_depuis_csv(nom_equipage)

        membres = equipage.Membres
        if not membres:
            return False

        personnes_a_inspecter = 0

        # Les médecins examinent l'équipage
        for membre in membres:

            if "Médecin" not in membre.Traits:
                continue

            succes = utils.Test(membre.Medecine, 0)
            if succes > 0:
                personnes_a_inspecter += succes * 10

        if personnes_a_inspecter <= 0:
            return "Aucun malade n'est à signaler ou isoler"

        personnes_a_inspecter = min(personnes_a_inspecter, len(membres))

        inspectes = random.sample(membres, personnes_a_inspecter)

        for membre in inspectes:
            if membre.Maladie not in ("", None):
                membre.Isole = True          # nouvel attribut booléen
                equipage.Save(nom_equipage)
                return "Nous avons repéré un indidividu malade, il est en isolement"

        equipage.Save(nom_equipage)
        return "Aucun malade n'est à signaler ou isoler"
    @staticmethod
    def TirerMaladie():
        df = utils.MALADIES

        ligne = df.sample(n=1).iloc[0].to_dict()
        return SimpleNamespace(**ligne)