import os
import csv
import pandas as pd
import random
import config
import utils
from classes.Navire import Navire
from classes.Navigation import Navigation
from classes.Maladie import Maladie
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

        journal = ""
        for jour in sorted(self.Journal):
            journal += f"Jour {jour}\n"
            for ligne in self.Journal[jour]:
                journal += f"  • {ligne}\n"
            journal += "\n"

        return {
            "Nom": self.Name,
            "Navire": self.Navire,
            "Année": self.Annee,
            "Jour": self.Jour,
            "Journal": journal,
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
            ligne["Jour"] = self.Jour
            ligne["EtapeCourante"] = self.EtapeCourante
            ligne["Avancement"] = self.Avancement
            lignes.append(ligne)

        df = pd.DataFrame(lignes)

        df.to_csv(
            os.path.join(config.BASE_PATH, "Voyage", f"{nom}.csv"),
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )
        journal_lignes = []

        for jour, evenements in self.Journal.items():
            for evenement in evenements:
                journal_lignes.append({
                    "Jour": jour,
                    "Evenement": evenement
                })

        df_journal = pd.DataFrame(journal_lignes)

        df_journal.to_csv(
            os.path.join(config.BASE_PATH, "Voyage", f"{nom}_journal.csv"),
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

        voyage.Jour = int(df["Jour"][0])
        voyage.EtapeCourante = int(df["EtapeCourante"][0])
        voyage.Avancement = float(df["Avancement"][0])

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

    def avancer_jour(self):
        """Fait progresser le voyage d'une journée."""

        # Voyage terminé
        if self.EtapeCourante >= len(self.Etapes):
            return "Le voyage est déjà terminé."

        etape = self.Etapes[self.EtapeCourante]

        self.Jour += 1
        journal = []

        # -------------------------------------------------
        # Chargement du navire
        # -------------------------------------------------

        navire = Navire.charger_depuis_csv(self.Navire)
        navigation = Navigation(navire,False)
        # -------------------------------------------------
        # Navigation test de navigation, bonus/malus de la distance en fonction des résultats
        # -------------------------------------------------

        bonus_navigation = navigation.TestNavigation(navire.Name)

        distance_jour = navire.VitesseMoyenne * bonus_navigation / 100

        self.Avancement += distance_jour
        ########
        journal.append(
            f"Le navire parcourt {distance_jour:.1f} MN "
            f"({self.Avancement:.1f}/{etape['Distance']} MN)."
        )

        # -------------------------------------------------
        # Maladies
        # -------------------------------------------------
        malade=Maladie()
        texte = malade.JourMaladie(1,navire.EquipageNom)
        if texte:
            journal.append(texte)

        # -------------------------------------------------
        # Hauts-fonds
        # -------------------------------------------------

        if (
                etape["TaillePortEscale"] != "Aucune (pas d'escale)"
                or etape["ZoneMaritime"] in ("côtes", "Littoral",'port',"mouillage","comptoir")
        ):

            texte = Navigation.HautsFonds(
                navire.Name,
                etape["ZoneMaritime"]
            )

            if texte:
                journal.append(texte)
        # -------------------------------------------------
        # Tempêtes
        # -------------------------------------------------

        texte = navigation.Tempest(navire.Name)

        if texte:
            if isinstance(texte, tuple):
                journal.append(texte[0])
            else:
                journal.append(texte)

        # -------------------------------------------------
        # Rencontres
        # -------------------------------------------------

        navire_rencontre = self.determiner_rencontre(self.Annee,etape["Region"],4,4,self.Jour,etape['ZoneMaritime'])
        if navire_rencontre:
            actions = navire_rencontre.actions_rencontre()
            journal.append(f"Vous rencontrez le navire {navire_rencontre.Name}.")


        # -------------------------------------------------
        # Arrivée
        # -------------------------------------------------

        if self.Avancement >= etape["Distance"]:

            self.Avancement -= etape["Distance"]

            journal.append(
                f"Arrivée dans la région {etape['Region']}."
            )

            self.EtapeCourante += 1

            if self.EtapeCourante >= len(self.Etapes):
                journal.append("🏁 Le voyage est terminé.")

        # -------------------------------------------------
        # Journal
        # -------------------------------------------------

        self.Journal[self.Jour] = journal

        # -------------------------------------------------
        # Sauvegarde
        # -------------------------------------------------

        self.sauvegarder()

        return {
            "journal": "\n".join(journal),
            "rencontre": navire_rencontre is not None,
            "navire_rencontre": navire_rencontre
        }

    def AfficherVoyage(self):

        nom_voyage = self.comboVoyage.get()

        if nom_voyage not in self.Voyages:
            return

        infos = self.Voyages[nom_voyage].Affichage()

        self.lblNom.config(text=infos["Nom"])
        self.lblNavire.config(text=infos["Navire"])
        self.lblJour.config(text=str(infos["Jour"]))

        distance_restante = 0

        if self.EtapeCourante < len(self.Etapes):
            distance_restante += (
                    self.Etapes[self.EtapeCourante]["Distance"] - self.Avancement
            )

            # étapes suivantes
            for e in self.Etapes[
                     self.EtapeCourante + 1:
                     ]:
                distance_restante += e["Distance"]

        self.lblDistance.config(text=f"{distance_restante:.0f} mn")

        # Journal
        self.txtJournal.delete("1.0", tk.END)
        self.txtJournal.insert("1.0", infos["Journal"])

        # Tableau des étapes
        self.tree.delete(*self.tree.get_children())

        for e in infos["Étapes"]:
            self.tree.insert(
                "",
                "end",
                values=(
                    e["Ordre"],
                    e["Région"],
                    e["Distance"],
                    e["Zone"],
                    e["Port"],
                ),
            )

    def executer_action(self, action, valeurs=None):

        if action == "JourSuivant":
            return self.avancer_jour()

        elif action == "Commercer":
            return self.Commercer(valeurs['navire_rencontre'])

        elif action == "Poursuivre":
            return self.Poursuivre(valeurs['navire_rencontre'])

        elif action == "PavillonNoir":
            return self.PavillonNoir(valeurs['navire_rencontre'])

        elif action == "Canonner":
            return self.Canonner(valeurs['navire_rencontre'])

        return ""

    def get_actions(self):
        return ["JourSuivant"]

    import re
    import random
    import pandas as pd
    import config

    def determiner_rencontre(self, annee,region,SeuilMa,SeuilAv,Jour,zone):
        df = utils.DE_RENCONTRE
        ZoneCommerce,ZoneCompagnie,ZoneRencontre=Navire.ConvertZone(region)
        DeMarchand = df[df["Zone"] == zone]["Marchand"].iloc[0]
        DeAventurier = df[df["Zone"] == zone]["Aventurier"].iloc[0]
        navire_rencontre=None
        if "D" not in DeMarchand:
            DeMarchand=int(DeMarchand)
            if SeuilMa>=random.randint(1,DeMarchand): ###Alors on rencontre un navire marchand
                Type = Navire.CalculType(ZoneRencontre, annee)
                Compagnie = Navire.CalculType(ZoneCompagnie, annee)
                navire_rencontre = Navire(Type, str(Jour) + "_Marchand", ZoneCommerce)
                navire_rencontre.Compagnie = Compagnie
                navire_rencontre.sauvegarder()
                navire_rencontre.ReconnaissanceNavire(navire_rencontre, 3)
        if SeuilAv >= random.randint(1, DeAventurier):  ###Alors on rencontre un navire aventurier
            Type=Navire.CalculType(ZoneRencontre,annee)
            Compagnie=Navire.CalculType(ZoneCompagnie,annee)
            navire_rencontre=Navire(Type,str(Jour)+"_Aventurier",ZoneCommerce)
            navire_rencontre.Compagnie = Compagnie
            navire_rencontre.Compagnie="Pirate"
            navire_rencontre.sauvegarder()
            navire_rencontre.ReconnaissanceNavire(navire_rencontre,3)
        return navire_rencontre

    def Commercer(self):
        return "Fonction pas encore implemente"
    def Canonner(self):
        return "Fonction pas encore implemente"
    def Poursuivre(self):
        return "Fonction pas encore implemente"
    def PavillonNoir(self):
        return "Fonction pas encore implemente"
