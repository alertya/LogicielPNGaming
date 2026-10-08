import math
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
        self.NavireRencontre=""
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
            ChanceRencontreMarchand=0,
            DeAventurier=0,
            CompetenceVigie=0):

        self.Etapes.append({
            "Region": Region,
            "Distance": Distance,
            "ZoneMaritime": ZoneMaritime,
            "TaillePortEscale": TaillePortEscale,
            "ChanceRencontreAventurier": ChanceRencontreAventurier,
            "ChanceRencontreMarchand": ChanceRencontreMarchand,
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
            ligne['NavireRencontre']=self.NavireRencontre
            lignes.append(ligne)

        df = pd.DataFrame(lignes)
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
            os.path.join(config.BASE_PATH, "Journal", f"{nom}_journal.csv"),
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )



    @classmethod
    def charger_depuis_csv(cls, nom):

        fichier = os.path.join(
            config.BASE_PATH,
            "Voyage",
            nom + ".csv"
        )

        if not os.path.exists(fichier):
            return None

        df = pd.read_csv(
            fichier,
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        if df.empty:
            return None


        # Création du voyage
        voyage = cls(
            df["NomTrajet"].iloc[0],
            df["Navire"].iloc[0],
            df["Annee"].iloc[0]
        )

        # Données générales
        voyage.Jour = int(df["Jour"].iloc[0])
        voyage.EtapeCourante = int(df["EtapeCourante"].iloc[0])
        voyage.Avancement = float(df["Avancement"].iloc[0])
        voyage.NavireRencontre=str(df["NavireRencontre"].iloc[0])
        # Reconstruction des étapes
        for _, ligne in df.iterrows():
            voyage.AjouterEtape(
                Region=ligne["Region"],
                Distance=ligne["Distance"],
                ZoneMaritime=ligne["ZoneMaritime"],
                TaillePortEscale=ligne["TaillePortEscale"],
                ChanceRencontreAventurier=ligne["ChanceRencontreAventurier"],
                ChanceRencontreMarchand=ligne.get("ChanceRencontreMarchand", 0),
                DeAventurier=ligne["DeAventurier"],
                CompetenceVigie=ligne["CompetenceVigie"]
            )

        # ============================================================
        # Chargement du journal
        # ============================================================

        fichier_journal = os.path.join(
            config.BASE_PATH,
            "Journal",
            nom + "_journal.csv"
        )

        if os.path.exists(fichier_journal):

            df_journal = pd.read_csv(
                fichier_journal,
                sep=";",
                decimal=",",
                encoding="cp1252"
            )

            voyage.Journal = {}

            for _, ligne in df_journal.iterrows():

                jour = int(ligne["Jour"])
                evenement = ligne["Evenement"]

                if jour not in voyage.Journal:
                    voyage.Journal[jour] = []

                voyage.Journal[jour].append(evenement)

        return voyage

    def avancer_jour(self,Seuilventurier,SeuilMarchand):
        """Fait progresser le voyage d'une journée."""
        print("Calcul etape")
        # Voyage terminé
        if self.EtapeCourante >= len(self.Etapes):
            return "Le voyage est déjà terminé."

        etape = self.Etapes[self.EtapeCourante]

        self.Jour += 1
        journal = []

        # -------------------------------------------------
        # Chargement du navire
        # -------------------------------------------------
        print("Chargement du navire")
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
        print("Determination maladie")
        malade=Maladie()
        texte = malade.JourMaladie(1,navire.EquipageNom)
        if texte:
            journal.append(texte)

        # -------------------------------------------------
        # Hauts-fonds
        # -------------------------------------------------
        print("Calcul navigation")
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
        print("Calcul tempête")
        texte = navigation.Tempest(navire.Name)

        if texte:
            if isinstance(texte, tuple):
                journal.append(texte[0])
            else:
                journal.append(texte)

        # -------------------------------------------------
        # Rencontres
        # -------------------------------------------------
        print("Calcul rencontre")
        self.NavireRencontre = self.determiner_rencontre(
            self.Annee,
            etape["Region"],
            SeuilMarchand,
            Seuilventurier,
            self.Jour,
            etape["ZoneMaritime"]
        )

        if self.NavireRencontre:
            NavireRencontre=Navire.charger_depuis_csv(self.NavireRencontre)
            actions = NavireRencontre.actions_rencontre()
            journal.append(f"Vous rencontrez le navire {NavireRencontre}.")
        print("Navire ajouté dans le journal")

        # -------------------------------------------------
        # Arrivée
        # -------------------------------------------------
        print("Calcul avancement")
        if self.Avancement >= etape["Distance"]:

            self.Avancement -= etape["Distance"]

            journal.append(
                f"Arrivée dans la région {etape['Region']}."
            )

            self.EtapeCourante += 1

            if self.EtapeCourante >= len(self.Etapes):
                journal.append("Le voyage est terminé.")

        # -------------------------------------------------
        # Journal
        # -------------------------------------------------

        self.Journal[self.Jour] = journal

        # -------------------------------------------------
        # Sauvegarde
        # -------------------------------------------------
        print("Sauvegarde")
        self.sauvegarder()

        return {
            "journal": "\n".join(journal),
            "rencontre": self.NavireRencontre is not None,
            "navire_rencontre": self.NavireRencontre
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

            if self.EtapeCourante >= len(self.Etapes):
                return {
                    "journal": "Le voyage est terminé.",
                    "rencontre": False
                }

            chanceAventurier = self.Etapes[self.EtapeCourante].get(
                "ChanceRencontreAventurier", 0
            )
            chanceMarchand = self.Etapes[self.EtapeCourante].get(
                "ChanceRencontreMarchand", 0
            )

            return self.avancer_jour(chanceAventurier, chanceMarchand)

        elif action == "Commercer":
            return self.Commercer()

        elif action == "Poursuivre":
            return self.Poursuivre()


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
        print("Initialisation parametre rencontre navire termine")
        NomNavireRencontre=""
        if "D" not in DeMarchand:
            DeMarchand=int(DeMarchand)


            tirage = random.randint(1, DeMarchand)

            if SeuilMa>=tirage: ###Alors on rencontre un navire marchand

                Type,garde_cote = Navire.CalculType(ZoneRencontre, annee)
                print("Determination type navire marchand réalisé")

                navire_rencontre = Navire(Type, str(Jour) + "_Marchand", ZoneCommerce)
                navire_rencontre.GardeCote = garde_cote
                print("Initialisation  navire marchand réalisé")
                Compagnie,Nationalite = navire_rencontre.CalculCompagnie(ZoneCompagnie, annee)
                print("Calcul compagnie  navire marchand réalisé")
                navire_rencontre.Compagnie = Compagnie
                navire_rencontre.Nationalite = Nationalite
                navire_rencontre.sauvegarder()
                navire_rencontre.ReconnaissanceNavire(navire_rencontre, 3)
                NomNavireRencontre = navire_rencontre.Name
                navire_reconnu = self.AfficherReconnu(navire_rencontre.Name + "_Reconnu")

        tirage = random.randint(1, DeAventurier)

        if SeuilAv >= tirage:  ###Alors on rencontre un navire aventurier


            Type,garde_cote = Navire.CalculType(ZoneRencontre, annee)
            print("Determination type navire aventurier réalisé")
            navire_rencontre = Navire(Type, str(Jour) + "_Marchand", ZoneCommerce)
            print("Initialisation  navire aventurier réalisé")
            Compagnie,Nationalite = navire_rencontre.CalculCompagnie(ZoneCompagnie, annee)
            navire_rencontre.GardeCote=garde_cote
            print("Calcul compagnie  navire aventurier réalisé")
            navire_rencontre = Navire(Type, str(Jour) + "_Marchand", ZoneCommerce)
            print("Navire créé :", navire_rencontre)

            navire_rencontre.Compagnie = "Pirate"
            navire_rencontre.Nationalite=Nationalite
            navire_rencontre.sauvegarder()
            navire_rencontre.ReconnaissanceNavire(navire_rencontre, 3)
            navire_reconnu=self.AfficherReconnu(navire_rencontre.Name+"_Reconnu")
            NomNavireRencontre=navire_rencontre.Name

        return NomNavireRencontre

    def Commercer(self):

        navire=Navire.charger_depuis_csv(self.NavireRencontre)
        if "Interlope" in navire.Compagnie or "Pirate" in navire.Compagnie:
            return f"Vous pouvez commercer avec {navire.Name}, veuillez vous rendre dans l'onglet Marchandise, actions et\n  vous pouvez vendre  dans {self.Navire.Marchandise.Name} en cours Exces et acheter des marchandises au {navire.Marchandise.Name} à 80% du cout normal"
        else:
            return f"Le capitaine ne souhaite pas commercer avec vous"

    def Poursuivre(self):
        theta=random.randint(0,360)
        navire = Navire.charger_depuis_csv(self.NavireRencontre)
        dx=math.cos(theta)
        dy=math.sin(theta)
        rayon=random.randint(1,8)
        dx=dx*rayon
        dy=dy*rayon
        heure=random.randint(1,12)+6
        return f"Il est {heure } heures. Vous essayez de poursuivre ce navire, veuillez transmettre la fiche navire de vos PJs et de garder la fiche de {navire.Name} \n Le navire se situe à {dx} miles à babord et {dy} devant vous \n si vous arrivez à vous approcher du navire avant la nuit tombée \n Vous pouvez entamer un combat naval dans Navire Action entre votre navire et {navire.Name}\n Vous pouvez hisser le pavillon noir avant afin d'intimider l'équipage adverse"

    def AfficherReconnu(self,name):
        navire = Navire.charger_depuis_csv(name)

        return f"Le navire est de {navire.CategorieNavire} avec une longueur de {navire.Longueur},un tonnage de {navire.Tonnage}, {navire.NbMats} mats et {navire.NbCanons} canons."