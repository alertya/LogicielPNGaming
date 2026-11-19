import math
import os
import csv
import pandas as pd
import random
import config
import utils
from classes.Navire import Navire
from classes.Equipage import Equipage
from classes.Navigation import Navigation
from classes.Maladie import Maladie
class Voyage:

    def __init__(self, Nom="", Navire="", Annee=1715,etapes=None):
        self.Name = Nom
        self.Navire = Navire
        self.navire_rencontre=None
        self.Annee = Annee
        self.Etapes = etapes if etapes is not None else []
        self.NavireRencontreAventurier=""
        self.NavireRencontreMarchand= ""
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
            ligne = etape.copy()

            ligne["NomTrajet"] = nom
            ligne["Navire"] = self.Navire
            ligne["Annee"] = self.Annee
            ligne["Ordre"] = i
            ligne["Jour"] = self.Jour
            ligne["EtapeCourante"] = self.EtapeCourante
            ligne["Avancement"] = self.Avancement
            ligne["NavireRencontreAventurier"] = self.NavireRencontreAventurier
            ligne["NavireRencontreMarchand"] = self.NavireRencontreMarchand

            lignes.append(ligne)

        df = pd.DataFrame(lignes)

        df.to_csv(
            os.path.join(config.BASE_PATH, "Voyage", f"{nom}.csv"),
            sep=";",
            decimal=",",
            encoding="cp1252",
            index=False
        )

        # ----------------------------------
        # Sauvegarde du journal
        # ----------------------------------

        journal_lignes = []

        for jour, evenements in self.Journal.items():
            for evenement in evenements:

                texte = str(evenement)

                try:
                    texte.encode("cp1252")

                except UnicodeEncodeError as e:
                    print("ERREUR ENCODAGE")
                    print("Jour :", jour)
                    print("Événement :", repr(texte))
                    print(
                        "Caractères incompatibles :",
                        repr(texte[e.start:e.end])
                    )

                    # Remplacement des caractères incompatibles
                    texte = texte.encode(
                        "cp1252",
                        errors="replace"
                    ).decode("cp1252")

                journal_lignes.append({
                    "Jour": jour,
                    "Evenement": texte
                })

        df_journal = pd.DataFrame(
            journal_lignes,
            columns=["Jour", "Evenement"]
        )

        df_journal.to_csv(
            os.path.join(
                config.BASE_PATH,
                "Journal",
                f"{nom}_journal.csv"
            ),
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
        voyage.NavireRencontreAventurier=str(df["NavireRencontreAventurier"].iloc[0])
        voyage.NavireRencontreMarchand = str(df["NavireRencontreMarchand"].iloc[0])
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
        print(self.Navire)
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
        self.NavireRencontreMarchand, self.NavireRencontreAventurier = (
            self.determiner_rencontre(
                self.Annee,
                etape["Region"],
                SeuilMarchand,
                Seuilventurier,
                self.Jour,
                etape["ZoneMaritime"]
            )
        )

        if self.NavireRencontreMarchand:
            NavireRencontreMarchand=Navire.charger_depuis_csv(self.NavireRencontreMarchand)
            actions = NavireRencontreMarchand.actions_rencontre()
            journal.append(f"Vous rencontrez le navire {self.NavireRencontreMarchand}.")
        if self.NavireRencontreAventurier:
            NavireRencontreAventurier=Navire.charger_depuis_csv(self.NavireRencontreAventurier)
            actions = NavireRencontreAventurier.actions_rencontre()
            journal.append(f"Vous rencontrez le navire {self.NavireRencontreAventurier}.")
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
                return {
                    "journal": "Le voyage est terminé.",
                    "rencontre": False,
                    "voyage": self.Name,
                    "navire": self.Navire,
                    "navire_rencontre_marchand": None,
                    "navire_rencontre_aventurier": None
                }

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
            "navire_rencontre_marchand": self.NavireRencontreMarchand,
            "navire_rencontre_aventurier": self.NavireRencontreAventurier,
            "voyage": self.Name,
            "navire": self.Navire
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
            # Sélection du navire rencontré
            if action in (
                    "Commercer",
                    "Poursuivre",
                    "HisserPavillonRouge",
                    "HisserPavillonNoir"
            ):

                valeurs = valeurs or {}

                self.file_rencontres = []

                navire_aventurier = valeurs.get("NavireRencontreAventurier")
                navire_marchand = valeurs.get("NavireRencontreMarchand")

                # Priorité au navire aventurier
                if navire_aventurier is not None:
                    self.file_rencontres.append(
                        ("Aventurier", navire_aventurier)
                    )

                # Ensuite, le navire marchand
                if navire_marchand is not None:
                    self.file_rencontres.append(
                        ("Marchand", navire_marchand)
                    )
                # Vérification du navire concerné



                # Exécution de l'action
                if action == "Commercer":
                    return self.Commercer()

                elif action == "Poursuivre":
                    return self.Poursuivre()

                elif action == "HisserPavillonRouge":
                    return self.HisserPavillonRouge()

                elif action == "HisserPavillonNoir":
                    return self.HisserPavillonNoir()

            return ""

    def get_actions(self):
        return ["JourSuivant","Commerce",'HisserPavillonNoir','Poursuivre','HisserPavillonRouge']

    def afficher_rencontre_suivante(self):

        if not self.file_rencontres:
            self.NavireRencontre = None
            print("Toutes les rencontres sont terminées.")
            return

        type_rencontre, nom_navire = self.file_rencontres.pop(0)

        self.NavireRencontre = nom_navire

        print("Type de rencontre :", type_rencontre)
        print("Navire rencontré :", nom_navire)

        self.ouvrir_formulaire_rencontre(
            self.nom_voyage_rencontre,
            nom_navire,
            type_rencontre
        )

    def determiner_rencontre(self, annee, region, SeuilMa, SeuilAv, Jour, zone):

        df = utils.DE_RENCONTRE

        ZoneCommerce, ZoneCompagnie, ZoneRencontre = Navire.ConvertZone(region)

        lignes = df[df["Zone"] == zone]

        if lignes.empty:
            raise ValueError(f"Zone de rencontre inconnue : {zone}")

        DeMarchand = lignes["Marchand"].iloc[0]
        DeAventurier = lignes["Aventurier"].iloc[0]

        NomNavireMarchand = ""
        NomNavireAventurier = ""

        print("Initialisation paramètres rencontre navire terminée")

        # -------------------------------------------
        # Fonction de tirage des dés
        # -------------------------------------------
        def lancer_de(valeur):

            valeur = str(valeur).strip().upper()

            if "D" in valeur:
                nombre, faces = valeur.split("D", 1)

                nombre = int(nombre) if nombre else 1
                faces = int(faces)

                return sum(
                    random.randint(1, faces)
                    for _ in range(nombre)
                )

            return random.randint(1, int(valeur))

        # -------------------------------------------
        # Rencontre marchande
        # -------------------------------------------
        tirage_marchand = lancer_de(DeMarchand)

        print("Tirage marchand :", tirage_marchand)

        if SeuilMa >= tirage_marchand:
            Type, garde_cote = Navire.CalculType(
                ZoneRencontre,
                annee
            )

            navire_marchand = Navire(
                Type,
                str(Jour) + "_Marchand",
                ZoneCommerce
            )

            navire_marchand.GardeCote = garde_cote

            navire_marchand.sauvegarder()

            navire_marchand.ReconnaissanceNavire(
                navire_marchand,
                3
            )

            NomNavireMarchand = navire_marchand.Name

            self.AfficherReconnu(
                NomNavireMarchand + "_Reconnu"
            )

            print("Navire marchand créé :", NomNavireMarchand)

        # -------------------------------------------
        # Rencontre aventurière
        # -------------------------------------------
        tirage_aventurier = lancer_de(DeAventurier)

        print("Tirage aventurier :", tirage_aventurier)

        if SeuilAv >= tirage_aventurier:
            Type, garde_cote = Navire.CalculType(
                ZoneRencontre,
                annee
            )

            navire_aventurier = Navire(
                Type,
                str(Jour) + "_Aventurier",
                ZoneCommerce
            )

            navire_aventurier.GardeCote = garde_cote
            navire_aventurier.Compagnie = "Pirate"

            navire_aventurier.sauvegarder()

            navire_aventurier.ReconnaissanceNavire(
                navire_aventurier,
                3
            )

            NomNavireAventurier = navire_aventurier.Name

            self.AfficherReconnu(
                NomNavireAventurier + "_Reconnu"
            )

            print("Navire aventurier créé :", NomNavireAventurier)

        # -------------------------------------------
        # Résultat
        # -------------------------------------------
        return NomNavireMarchand, NomNavireAventurier

    def Commercer(self):

        if self.NavireRencontre is None:
            return "Aucun navire rencontré."

        navire = Navire.charger_depuis_csv(self.NavireRencontre)

        if navire is None:
            return "Impossible de charger le navire rencontré."

        if any(
                compagnie in str(navire.Compagnie)
                for compagnie in ("Interlope", "Pirate")
        ):
            return (
                f"Vous pouvez commercer avec {navire.Name}. Vous pouvez acheter des cargaisons à {navire.MarchandiseNom} et vendre les votre à 80% du cours"
            )

        return "Le capitaine ne souhaite pas commercer avec vous."

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
    def HisserPavillonNoir(self):
        navire = Navire.charger_depuis_csv(self.NavireRencontre)
        equipage=Equipage(navire.NombreEquipage,"Matelot",navire.EquipageNom)
        return equipage.MoraleEquipage(navire.EquipageNom,"Noir")
    def HisserPavillonRouge(self):
        navire = Navire.charger_depuis_csv(self.NavireRencontre)
        equipage=Equipage(navire.NombreEquipage,"Matelot",navire.EquipageNom)
        return equipage.MoraleEquipage(navire.EquipageNom,"Rouge")