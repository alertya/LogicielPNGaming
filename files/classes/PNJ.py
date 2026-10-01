
import pandas as pd
from config import BASE_PATH
import numpy as np
import utils
import os
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


    def Save(self):

        TempDF = pd.DataFrame([
            vars(pnj)
            for pnj in self.Membres
        ])

        TempDF.to_csv(BASE_PATH+"/Equipage/"+self.Name+".csv",sep=";",decimal=",",encoding="cp1252", index= False)


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
        Text = ""

        if TypeRecrutant == "Pirate":

            # Modification de l'adhésion à la cause pirate
            for membre in EquipageRecrute.Membres:
                membre.Pirate *= (1 + SuccesRecrutement / 10)

                # Conversion en entier
                membre.Pirate = int(round(membre.Pirate))

            # Membres hostiles
            NbHostiles = sum(
                1
                for membre in EquipageRecrute.Membres
                if membre.Pirate < 0
            )

            Text += (
                f"{NbHostiles} sont prêts à dénoncer "
                f"l'équipage pirate\n"
            )

            # Membres qui rejoignent
            PersonnesRecrutees = [
                membre
                for membre in EquipageRecrute.Membres
                if membre.Pirate > 1
            ]

            Text += (
                f"{len(PersonnesRecrutees)} sont prêts "
                f"à rejoindre l'équipage\n"
            )

            # Transfert des membres
            self.Membres.extend(PersonnesRecrutees)

            # Recalcul de la valeur de combat
            self.ValeurCombat = self.CalculCombatEquipage()

        return Text

    def SoinsEquipage(
            self,
            CompMedecine,
            CompChirurgie
    ):

        for membre in self.Membres:
            membre.PV = membre.PVMax - 1

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
            for membre in self.Membres
        )


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


