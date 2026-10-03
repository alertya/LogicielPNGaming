
import pandas as pd
from config import BASE_PATH
import numpy as np
import utils
import os
import csv
import random


class Equipage:


    def __init__(self, Nb, Type, Name):

        self.Name = Name
        self.Type = Type
        self.Membres = []

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
            membre.PVMax=random.randint(5,8)
            membre.PV=membre.PVMax
            self.Membres.append(membre)
            Equipage.Save(self)

    def Save(self):
        """
        Sauvegarde tous les membres de l'équipage dans un fichier CSV.
        Chaque colonne correspond à un attribut du membre, chaque ligne à un membre.
        """
        # Si l'équipage est vide, inutile de créer un fichier vide sans colonnes
        if not self.Membres:
            print("L'équipage est vide, sauvegarde annulée.")
            return

        # Construction du chemin du fichier
        dossier_equipage = os.path.join(BASE_PATH, "Equipage")
        os.makedirs(dossier_equipage, exist_ok=True)  # Crée le dossier s'il n'existe pas
        chemin_fichier = os.path.join(dossier_equipage, f"{self.Name}.csv")

        # 1. Extraction dynamique de tous les attributs possibles du premier membre
        # (Fonctionne avec vars(pnj) ou pnj.__dict__)
        entetes = list(vars(self.Membres[0]).keys())

            # 2. Écriture du fichier CSV
        with open(chemin_fichier, mode="w", newline="", encoding="cp1252") as f:
            writer = csv.DictWriter(f, fieldnames=entetes, delimiter=";")
            writer.writeheader()  # Écrit la ligne des attributs

            for pnj in self.Membres:
                donnees_membre = vars(pnj)
                ligne_formatee = {}

                    # Nettoyage et formatage des données (ex: gestion des float avec virgule)
                for cle, valeur in donnees_membre.items():
                    if isinstance(valeur, float):
                        ligne_formatee[cle] = str(valeur).replace(".", ",")
                    else:
                        ligne_formatee[cle] = valeur

                writer.writerow(ligne_formatee)
        print(f"Équipage '{self.Name}' sauvegardé avec succès.")

    @classmethod
    def charger_depuis_csv(cls, Name: str) -> 'Equipage':
        """
        Méthode de classe qui lit un fichier CSV d'équipage, instancie la classe Equipage,
        recrée chaque membre ligne par ligne avec ses attributs typés, et renvoie l'objet Equipage.
        """
        # Nettoyage de l'espace dans le nom du fichier présent dans votre code d'origine
        chemin_fichier = os.path.join(BASE_PATH, "Equipage", f"{Name}.csv")

        if not os.path.exists(chemin_fichier):
            print(f"Le fichier d'équipage {chemin_fichier} n'existe pas.")
            return None

            # 1. Instanciation d'un nouvel équipage tout neuf
        nouvel_equipage = Equipage(10,"Matelot","TestEquipage")

            # 2. Lecture et parcours du fichier CSV
        with open(chemin_fichier, mode="r", newline="", encoding="cp1252") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                    # Si vous avez une classe Membre officielle importée (ex: Membre), remplacez par : membre = Membre()
                    # Sinon, on conserve la création dynamique d'un objet générique propre :
                membre = type("MembreEquipage", (), {})()

                    # Pour chaque colonne, on applique dynamiquement l'attribut au membre
                for attribut, valeur in row.items():
                        # Conversion des cases vides
                    if valeur == "":
                        setattr(membre, attribut, "")
                        continue

                        # Tentative de conversion de type intelligente pour le membre (int, float, str)
                    try:
                        if "," in valeur and valeur.replace(",", "").replace("-", "").isdigit():
                            setattr(membre, attribut, float(valeur.replace(",", ".")))
                        elif valeur.replace("-", "").isdigit():
                            setattr(membre, attribut, int(valeur))
                        elif valeur.lower() in ["true", "false"]:
                            setattr(membre, attribut, valeur.lower() == "true")
                        else:
                            setattr(membre, attribut, valeur)
                    except ValueError:
                        # En cas d'échec de conversion, on laisse la chaîne brute
                        setattr(membre, attribut, valeur)

                    # Ajout du membre reconstruit dans notre liste d'équipage
                nouvel_equipage.Membres.append(membre)

            # 3. Renvoi de la classe Equipage peuplée
        return nouvel_equipage

    ###Convertit le nombre de succes en action courte
    def ConvertSuccessToAction(self,Success):
        ActCourte = 4 - Success
        ActLongue = 7 - Success
        return ActCourte,ActLongue



    def RecruteList(self,NbList,TypeList,Name,Bonus,window):
        Text=""
        for k in range(len(NbList)):
            Nb=int(NbList[k].get())
            Tmp=self.Recrute(Nb,TypeList[k],Bonus)
            Text=Text+Tmp
        window.destroy()
        return Text

    def Recrute(self, Nb, Type, Bonus):

        Pond = pd.read_csv(
            BASE_PATH + "/ListeProf.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        Ponds = Pond[Pond["Type"] == Type]

        Temp = ""

        for _ in range(Nb):

            donnees = Ponds.iloc[0].to_dict()

            # Génération des compétences
            for k in Ponds.columns[1:71]:

                if k not in ["Salaire", "Employeur"]:
                    donnees[k] = utils.Compute(Ponds[k].iloc[0])

            # Armes blanches
            donnees["ArmesBlanches"] = max(
                donnees["Dague"],
                donnees["Hache"],
                donnees["Sabre"]
            )

            # Attributs propres au membre
            donnees["Nom"] = ""
            donnees["Maladie"] = ""
            donnees["Moral"] = 2
            donnees["Groupe"] = ""
            donnees["Pirate"] = 1
            donnees["Score"] = 0
            donnees["Role"] = ""
            donnees["Famine"] = 0
            donnees["KillCount"] = 0
            donnees["LastSuccess"] = 0

            donnees["Attitude"] = int(
                np.random.normal(50, 5)
            )

            # Création du membre
            membre = type("Membre", (), {})()

            for attribut, valeur in donnees.items():
                setattr(membre, attribut, valeur)

            # Calculs individuels
            self.ScoreMembre(membre)
            self.AttributeGroupeMembre(membre)

            self.Membres.append(membre)

        self.ValeurCombat = self.CalculCombatEquipage()

        return Temp

    def CalculPointDeVieMembre(self, membre):

        PVMax = random.randint(5,8)


        return PVMax
    def ScoreMembre(self, membre):

        Capi = [
            "Balistique",
            "Connaissances nautiques",
            "Hydrographie",
            "Navigation",
            "Tactique",
            "MeneurHommes"
        ]

        Second = [
            "Connaissances nautiques",
            "MeneurHommes",
            "Pratique nautique",
            "Tactique"
        ]

        Canonnier = [
            "Balistique",
            "Connaissances nautiques",
            "MeneurHommes",
            "Recharge",
            "Pointage",
            "Tactique"
        ]

        MaitreEquipage = [
            "Connaissances nautiques",
            "Enseignement",
            "Intimidation",
            "Pratique nautique",
            "MainsNue"
        ]

        MaitreCanonnier = [
            "Pointage",
            "Recharge",
            "Connaissances nautiques",
            "Enseignement",
            "Intimidation",
            "Pratique nautique"
        ]

        QuartierMaitre = [
            "MeneurHommes",
            "Connaissances nautiques",
            "Droit",
            "Empathie",
            "Enseignement",
            "Pratique nautique",
            "Persuasion",
            "Timonerie"
        ]

        # Score général
        exclusions = [
            "Nom",
            "Groupe",
            "Maladie",
            "Attitude",
            "Pirate",
            "Role",
            "Type",
            "Salaire",
            "Employeur"
        ]

        scores = []

        for attribut, valeur in vars(membre).items():

            if attribut not in exclusions:
                if isinstance(valeur, (int, float)):
                    scores.append(valeur)

        membre.Score = sum(scores) / len(scores)

        # Scores spécialisés
        membre.Capi = self.CalculScore(membre, Capi)
        membre.Second = self.CalculScore(membre, Second)
        membre.Canonnier = self.CalculScore(membre, Canonnier)
        membre.MaitreEquipage = self.CalculScore(membre, MaitreEquipage)
        membre.MaitreCanonnier = self.CalculScore(membre, MaitreCanonnier)
        membre.QuartierMaitre = self.CalculScore(membre, QuartierMaitre)

        return membre

    def AttributeGroupeMembre(self, membre):

        Roles = pd.read_csv(
            BASE_PATH + "/RoleColonie.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        membre.Groupe = membre.Role

        for _, row in Roles.iterrows():

            Comp = row["Competence"]
            Seuil = row["Seuil"]
            Role = row["Role"]

            if (
                    getattr(membre, Comp, 0) >= Seuil
                    and membre.Groupe == ""
            ):
                membre.Groupe = Role

        return membre
    def CalculScore(self, membre, competences):

        valeurs = [
            getattr(membre, competence)
            for competence in competences
        ]

        return sum(valeurs) / len(valeurs)

    def CalculCombatEquipage(self):

        MembresValides = self.HommesValides()

        return (
                sum(membre.ArmesBlanches for membre in MembresValides)
                *
                sum(membre.PV for membre in MembresValides)
        )


    def CalculScoreMembre(self, membre, competences):

        valeurs = []

        for competence in competences:

            valeur = getattr(membre, competence, 0)

            if isinstance(valeur, (int, float)):
                valeurs.append(valeur)

        if not valeurs:
            return 0

        return sum(valeurs) / len(valeurs)
    def Groupe(self, Seuil, Comp, NouvName):

        MembresCorrespondants = []

        for membre in self.Membres:

            valeur = getattr(membre, Comp, 0)

            if valeur >= Seuil:

                if NouvName not in membre.Groupe:

                    if membre.Groupe:
                        membre.Groupe += "," + NouvName
                    else:
                        membre.Groupe = NouvName

                MembresCorrespondants.append(membre)

        self.Save()

        return MembresCorrespondants

    def ResultatCompetence(self, Comp, Bonus):

        Membres = self.HommesValides()
        Resultats = []

        for membre in Membres:
            Valeur = getattr(membre, Comp, 0)

            Resultat = utils.lancer_de(
                Valeur,
                Bonus
            )[0]


            Resultats.append(Resultat)

        if not Resultats:
            return 0, 0

        Total = sum(Resultats)
        Moyen = Total / len(Resultats)

        return Total, Moyen
    def Tues(self, Morts):

        if Morts < 0:
            Morts = 0

        if Morts == 0:
            return 0

        if Morts < len(self.Membres):

            # Sélection des PNJ qui meurent
            morts = random.sample(self.Membres, Morts)

            # Suppression des PNJ
            for pnj in morts:
                self.Membres.remove(pnj)

            # Recalcul de la valeur de combat
            self.ValeurCombat = self.CalculCombatEquipage()

        else:

            # Tout l'équipage est décimé
            self.Membres.clear()
            self.ValeurCombat = 0

            print("Votre équipage a été décimé")

        return Morts

    def Degats(self, Comp, Bonus):

        if Comp == "":
            return 0

        # Nombre de membres
        Len = len(self.HommesValides())

        if Len == 0:
            return 0

        Degats = self.ResultatCompetence(Comp,Bonus)[0]

        return Degats

    def DegatsMesure(self, Comp, Bonus):

        if Comp == "":
            return 0

        MembresValides = self.HommesValides()

        Len = len(MembresValides)

        if Len == 0:
            return 0

        Degats = self.ResultatCompetence(Comp,Bonus)[0]

        DegMoy = Degats / Len

        Valeur = (
                0.9925
                * np.exp(
            0.2298
            * (Len - 9.9721 + 2 * DegMoy)
        )
        )

        return Valeur

    def Perte(self, Degats):

        Mort = 0
        Degats = int(Degats)

        for _ in range(Degats):

            # Plus personne dans l'équipage
            if len(self.Membres) < 1:
                print(f"{self.Name} a été décimé")
                break

            # Choisir un membre aléatoirement
            membre = random.choice(self.Membres)

            # Perdre 1 PV
            membre.PV -= 1

            # Mort du membre
            if membre.PV < 1:
                self.Membres.remove(membre)

                Mort += 1

        # Recalcul de la puissance de combat
        self.ValeurCombat = self.CalculCombatEquipage()

        print(f"Nombre de morts : {Mort}")

        return Mort


    def BatailleTerrestre(
            self,
            ArmeeAdverse,
            Comp1,
            Comp2,
            Bonus1,
            Bonus2
    ):

        Text = ""

        Armee1Valide = self.HommesValides()
        Armee2Valide = ArmeeAdverse.HommesValides()

        Armee1Valide = [
            membre for membre in Armee1Valide
            if membre.Moral > -1
        ]

        Armee2Valide = [
            membre for membre in Armee2Valide
            if membre.Moral > -1
        ]

        Text += (
            f"{self.Name} a encore "
            f"{len(Armee1Valide)} disponibles au combat\n"
        )

        Text += (
            f"{ArmeeAdverse.Name} a encore "
            f"{len(Armee2Valide)} disponibles au combat\n"
        )

        Degat1 = self.Degats(Comp1, Bonus1)
        Degat2 = ArmeeAdverse.Degats(Comp2, Bonus2)

        Perte1 = 0
        Perte2 = 0

        if Armee1Valide:

            Perte1 = self.Perte(Degat2)

            Text += self.Attitude(
                -Perte1 / len(self.Membres) * 50
            )[1]

        else:

            Text += (
                f"{self.Name} a été décimé "
                "ou s'est rendu/enfui\n"
            )

        if Armee2Valide:

            Perte2 = ArmeeAdverse.Perte(Degat1)

            Text += ArmeeAdverse.Attitude(
                -Perte2 / len(ArmeeAdverse.Membres) * 50
            )[1]

        else:

            Text += (
                f"{ArmeeAdverse.Name} a été décimé "
                "ou s'est rendu/enfui\n"
            )

        return Text

    ###Exemple, cl


    def Role(self):

        Roles = [
            "Capi",
            "Second",
            "MaitreEquipage",
            "MaitreCanonnier",
            "Canonnier",
            "QuartierMaitre"
        ]

        for membre in self.Membres:

            membre.Role = ""

            for role in Roles:

                if getattr(membre, role, 0) == max(
                        getattr(membre, r, 0)
                        for r in Roles
                ):
                    membre.Role = role
                    break

    def Attitude(self, Modif):

        Texts = ""

        for membre in self.Membres:
            membre.Attitude += int(
                np.random.normal(
                    Modif,
                    abs(Modif / 10)
                )
            )

        Seuils = [
            25,
            10,
            0,
            -10,
            -25,
            -50
        ]

        for seuil in Seuils:

            count = sum(
                membre.Attitude < seuil
                for membre in self.Membres
            )

            if count > 0:
                Texts += (
                    f"Dans l'équipage {self.Name}, "
                    f"{count} ont une loyauté inférieure "
                    f"à {seuil} sur {len(self.Membres)} "
                    f"hommes disponibles.\n"
                )

        return self, Texts

    def AttributeExp(self, Comp, Exp):

        for membre in self.Membres:

            attribut_exp = Comp + "_exp"

            valeur_exp = getattr(
                membre,
                attribut_exp,
                0
            )

            valeur_exp += int(Exp)

            setattr(
                membre,
                attribut_exp,
                valeur_exp
            )

            valeur_comp = getattr(
                membre,
                Comp
            )

            condition = (
                                valeur_exp > 0
                                and valeur_comp < 0
                        ) or (
                                valeur_exp > valeur_comp * valeur_comp
                        )

            if condition:
                setattr(
                    membre,
                    Comp,
                    valeur_comp + 1
                )

                setattr(
                    membre,
                    attribut_exp,
                    0
                )

        return "Les expériences ont été attribuées."

    def Pirate(self, Symp):

        Text = ""

        for membre in self.Membres:

            tirage = np.random.randint(0, 10)

            if Symp == 1:

                if tirage > 0:
                    membre.Pirate = -1

                if tirage <= 5:
                    membre.Pirate = 1

                if tirage <= 1:
                    membre.Pirate = 2

            elif Symp == 0:

                if tirage > 5:
                    membre.Pirate = -1

                if tirage <= 2:
                    membre.Pirate = 1

            elif Symp == -1:

                membre.Pirate = -1

        Size1 = sum(
            membre.Pirate == -1
            for membre in self.Membres
        )

        Size2 = sum(
            membre.Pirate == 0
            for membre in self.Membres
        )

        Size3 = sum(
            membre.Pirate == 1
            for membre in self.Membres
        )

        Size4 = sum(
            membre.Pirate == 2
            for membre in self.Membres
        )

        Text = (
            f"{Size1} membres sont prêts à dénoncer "
            f"des agissements pirates\n"
            f"{Size2} membres sont neutres envers "
            f"des agissements pirates\n"
            f"{Size3} membres sont prêts à aider "
            f"des agissements pirates\n"
            f"{Size4} membres sont prêts à sauver "
            f"des agissements pirates\n"
        )

        return Text

    def AfficheColonne(self, Comp):

        valeurs = [
            getattr(membre, Comp)
            for membre in self.Membres
        ]

        return pd.Series(valeurs).value_counts().to_string()

    def RecruteEquipage(
            self,
            TypeRecrutant,
            EquipageRecrute,
            SuccesRecrutement
    ):

        texte = ""

        # Coefficient selon le type de recruteur
        bonus = {
            "Pirate": "Pirate",
            "Matelot": "Matelot",
        }

        caracteristique = bonus.get(TypeRecrutant, "Pirate")

        personnes_recrutees = []
        nb_hostiles = 0

        for membre in EquipageRecrute.Membres:

            # Augmente la caractéristique adaptée
            valeur = getattr(membre, caracteristique)
            valeur *= (1 + SuccesRecrutement / 10)
            valeur = int(round(valeur))
            setattr(membre, caracteristique, valeur)

            if valeur < 0:
                nb_hostiles += 1

            elif valeur > 1:
                personnes_recrutees.append(membre)

        texte += (
            f"{nb_hostiles} sont prêts à dénoncer le recruteur.\n"
        )

        texte += (
            f"{len(personnes_recrutees)} rejoignent l'équipage.\n"
        )

        # Transfert des membres
        for membre in personnes_recrutees:
            EquipageRecrute.Membres.remove(membre)
            self.Membres.append(membre)

        # Mise à jour des valeurs de combat
        self.ValeurCombat = self.CalculCombatEquipage()
        EquipageRecrute.ValeurCombat = EquipageRecrute.CalculCombatEquipage()

        return personnes_recrutees

    def SoinsEquipage(
            self
    ):

        for chirurgien in self.Membres:

            if chirurgien.Role != "Chirurgien":
                continue

            # Test de chirurgie
            print(chirurgien.Chirurgie)
            reussites = utils.Test(
                chirurgien.Chirurgie,
            )

            # Si Test renvoie un booléen, adapte cette partie
            if reussites <= 0:
                continue

            soins_restants = reussites * 10

            while soins_restants > 0:

                blesses = [
                    m for m in self.Membres
                    if m.PV < m.PVMax
                ]

                if not blesses:
                    break

                patient = random.choice(blesses)
                patient.PV += 1
                soins_restants -= 1

        return self
    def RepartCompetence(self, Seuil, Lists):

        Text = ""

        for competence in Lists:

            NbElements = sum(
                getattr(membre, competence, 0) >= Seuil
                for membre in self.Membres
            )

            if NbElements > 0:
                Text += (
                    f"{NbElements} ont la compétence "
                    f"{competence} égale ou supérieure à "
                    f"{Seuil}\n"
                )

        return Text

    def ActionEquipage(self, Intitule, SousGroupe, Bonus):

        # Lecture de la définition de l'action
        Actions = pd.read_csv(
            BASE_PATH + "/ListeActions.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        Action = Actions[
            Actions["Intitule"] == Intitule
            ]

        if Action.empty:
            raise ValueError(
                f"Action inconnue : {Intitule}"
            )

        Competence = Action["Competence"].iloc[0]

        # Membres disponibles
        Equipe = self.HommesValides()

        # Sélection du sous-groupe
        if SousGroupe != "Equipage":

            Equipe = [
                membre
                for membre in Equipe
                if getattr(membre, Competence, 0) >= 2
            ]

        elif Action["Groupe"].iloc[0] != "Equipage":

            Statut = Action["Groupe"].iloc[0]

            Equipe = [
                membre
                for membre in Equipe
                if membre.Role == Statut
            ]

        # Aucun membre disponible
        if len(Equipe) == 0:
            return 0, 0

        # Jet de l'action
        Total = self.ResultatCompetence(
            Competence,
            Bonus
        )[0]

        Moyen = Total / len(Equipe)

        return Total, Moyen

    ####Attribue des groupes par défaut en fonction des données du ficgier RoleColonie
    def AttributeGroupe(self):

        Roles = pd.read_csv(
            BASE_PATH + "/RoleColonie.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        for membre in self.Membres:

            membre.Groupe = membre.Role

            for _, row in Roles.iterrows():

                Comp = row["Competence"]
                Seuil = row["Seuil"]
                Role = row["Role"]

                if (
                        getattr(membre, Comp, 0) >= Seuil
                        and membre.Groupe == ""
                ):
                    membre.Groupe = Role

        return self

    def AttributionSalaireParRole(self):

        SalairesRole = pd.read_csv(
            BASE_PATH + "/SalaireRole.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        for membre in self.Membres:

            Type = membre.Type

            filtered = SalairesRole[
                SalairesRole["Type"] == Type
                ]

            if not filtered.empty:

                membre.Salaire = (
                    filtered["Salaire"].iloc[0]
                )

            else:

                membre.Salaire = -9999

        return sum(
            membre.Salaire
            for membre in self.Membres
        )

    def CalculSalaireEquipage(self):

        SalairesRole = pd.read_csv(
            BASE_PATH + "/SalaireRole.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        for membre in self.Membres:

            # Recherche du salaire correspondant au Type
            Type = membre.Type

            Salaire = SalairesRole.loc[
                SalairesRole["Type"] == Type,
                "Salaire"
            ]

            if not Salaire.empty:
                membre.Salaire = Salaire.iloc[0]
            else:
                membre.Salaire = -9999

            # Si le membre possède un rôle,
            # son Type devient son rôle
            if membre.Role is not None and membre.Role != "":
                membre.Type = membre.Role

        # Salaire total de l'équipage
        self.Salaire = self.CalculSalaireJournalier()

        return self.Salaire

    def CalculSalaireJournalier(self):

        return sum(
            membre.Salaire
            for membre in self.Membres)/29


    ####Retourne les hommes qui ne sont ni malades, ni blesses
    def HommesValides(self):

        return [
            membre
            for membre in self.Membres
            if membre.PV > 0
        ]

    ####Calcule les valeurs de combat de ton navire et équipage


    ###Determine le moral d'un equipage des hommes valides pour une action
    ###Si echec critique alors les hommes s'enfuient ou se cachent
    def MoraleEquipage(self, Bonus):

        for membre in self.Membres:

            # Les membres qui ont déjà Moral = -1
            # ne font pas de nouveau test
            if membre.Moral != -1:
                membre.Moral = utils.lancer_de(2, Bonus)[0]

        # Membres qui restent dans l'équipage
        self.Membres = [
            membre
            for membre in self.Membres
            if membre.Moral != -1
        ]

        # Mise à jour de la valeur de combat
        self.ValeurCombat = self.CalculCombatEquipage()

        return self.Membres

    ###A la fin d'une action, on remet le moral des restants à 2
    def ResetMoral(self):

        for membre in self.Membres:
            membre.Moral = 2

    def Reddition(self, Bonus):
        Equipage = self.MoraleEquipage(Bonus)

        if len(Equipage) < 1:
            return True

        return Equipage

    def get_actions(self):
        return ["Recruter", "Attribuer les rôles", "Distribuer les soldes","Bataille","Soins"]

    def executer_action(self, action, valeurs=None):

        if action == "Recruter":

            NbRecrute=self.RecruteEquipage(
                valeurs["Equipage_source"],
                valeurs["Equipage_cible"],
                valeurs["Nombre"]
            )
            EquipageRecrute=self.charger_depuis_csv(valeurs['Equipage_cible'])

            return "Vous avez recrute "+str(NbRecrute)+" marins en plus venant de "+EquipageRecrute.Name+"."

        elif action == "Attribuer les rôles":
            self.AttributeGroupe()
            # On fera cette partie plus tard
            return "Les roles ont été attribués dans "+self.Name

        elif action == "Distribuer les soldes":
            return "Vous payez le salaire du jour de votre equipage, veuillez retirer "+str(self.CalculSalaireJournalier())+" pièces de huit de votre inventaire."
            # On fera cette partie plus tard

        elif action == "Soins":
            self.SoinsEquipage(2,2)
            # On fera cette partie plus tard
            return "Fonction non implémentée."
        elif action == "Bataille":
            self.BatailleTerrestre(2,2)
            # On fera cette partie plus tard
            return "Fonction non implémentée."
        return "Action inconnue."
