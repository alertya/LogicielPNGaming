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
from config import *




class Port:

    def __init__(self, Nom):

        self.Cargaison = Nom
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



    ####Constantes
    def TriMarchandiseDataframe(Marchandises):
        exclure = ["passagers", "de monnaie", "Passagers", "pèlerins", "Pèlerins"]

        # Filtrage ligne par ligne : on garde uniquement celles qui ne contiennent pas un des mots
        Marchandises = Marchandises[~Marchandises['Cargaison'].str.lower().apply(
            lambda x: any(mot in x for mot in exclure)
        )]

        return Marchandises
    def TriMarchandiseList(Marchandises):
        exclure = ["passagers", "de monnaie", "pèlerins"]
        exclure_lower = [mot.lower() for mot in exclure]

        result = [
            item for item in Marchandises
            if not any(mot in item.lower() for mot in exclure_lower)
        ]

        return result
    def calcul_prix_variable(row):
        court = row['Cours']
        court=1-court
        if court < 0.5:
            return row['PrixPenurie']+(row['PrixNormal']-row['PrixPenurie'])*court
        elif court >= 0.5:
            return row['PrixNormal']+(row['PrixExces']-row['PrixNormal'])*(court-0.5)
        else:
            return row['PrixBase']
    def CoursMarchandise(DerniersJour,Region,TaillePort):
        Marchandises = pd.read_csv(BASE_PATH+"/Marchandises.csv", sep=";", decimal=",", encoding="cp1252")
        TaillesPort = pd.read_csv(BASE_PATH+"/DeRencontre.csv", sep=";", decimal=",", encoding="cp1252")
        TaillePort=TaillesPort[TaillesPort['Zone']==TaillePort].iloc[0]
        TaillePort=TaillePort['Marchand']

        if "D" in str(TaillePort):
            TaillePort=TaillePort.replace('D', '')
            TaillePort=int(TaillePort)
        TaillePort = int(TaillePort)
        Marchandises['Tonnage']=0

        TonnageMoyen=202*random.randint(40,100)/100*DerniersJour*TaillePort/2
        MatelotMoyenMin=32
        MatelotMoyenMax=178

        for k in range(DerniersJour):

            Navires = random.randint(1, TaillePort)
            MatelotRandom = random.randint(MatelotMoyenMin, MatelotMoyenMax) * DerniersJour * TaillePort / 2
            TonnageMoyen = 202 * random.randint(40, 100) / 100 * DerniersJour * TaillePort / 2
            CoursActuel = TonnageMoyen / MatelotRandom
            for j in range(Navires):
                Navire,Text=RencontreVoyage.RencontreNavire(str(k),Region,0,"")
                Tonnage=random.randint(Navire['TonnageMin'].iloc[0].astype(int),Navire['TonnageMax'].iloc[0].astype(int))
                Marchandise=RetourMarchandise(Tonnage,Region)
                # Normalisation pour comparaison fiable avec ajout marchandise et suffixe
                Marchandises['Cargaison'] = Marchandises['Cargaison'].astype(str).str.strip().str.lower()

                for cle, valeur in Marchandise.items():
                    cle_normalise = str(cle).strip().lower()
                    valeur=int(valeur)
                    mask = Marchandises['Cargaison'] == cle_normalise
                    if mask.any():
                        Marchandises.loc[mask, 'Tonnage'] = Marchandises.loc[mask, 'Tonnage'] + valeur
                    else:
                        nouveau = {'Cargaison': cle, 'Tonnage': valeur}
                        Marchandises = pd.concat([Marchandises, pd.DataFrame([nouveau])], ignore_index=True)
        Marchandises['Cours']=Marchandises['Tonnage']/MatelotRandom*CoursActuel
        Marchandises['PrixAchat']=Marchandises.apply(calcul_prix_variable, axis=1)
        Marchandises['PrixVente'] = Marchandises['PrixAchat']*0.8
        Marchandises=Marchandises[Marchandises['Tonnage']>0]
        Marchandises=Marchandises[Marchandises['Cargaison']!='vide']
        Marchandises = Marchandises[Marchandises['Cargaison'] != 'déjà pillé par un aventurier']
        Marchandises = Marchandises[Marchandises['Cargaison'] != '10 déjà pillé par un aventurier']
        Marchandises.to_csv(MARCHANDISE_PATH+"/"+"CoursMarchandise"+Region+".csv",sep=";",decimal=",",encoding="cp1252")
        return Marchandises

    ###Permet de simuler la recherche d'un marchand et sa capacité d'achat/revente en fonction du port
    def TrouverMarchand(Region):
        Marchand=pd.DataFrame()
        Navire=RencontreVoyage.RencontreNavire("Defaut.csv",Region,0,"Defaut")[0]
        Navire=Navire.iloc[0]
        Marchandises=RetourMarchandise(Navire['Tonnage'],Region)
        Marchand['Nom']=utils.RandomNom()[0]+" "+utils.RandomNom()[1]
        Marchand['Commerce']=utils.Compute(1)
        Text=""
        Marchand['Fortune']=CalculPiecesDeMonnaie(utils.Test(Marchand['Commerce'].iloc[0],0)*10)
        Marchand['Opinion']=-3
        CapaciteAchat=Marchand['Fortune']
        ProbaMarchandise=CapaciteAchat/600000
        CapaciteVente=ProbaMarchandise
        ActualiserToutMarchand()
        return Text,CapaciteAchat,CapaciteVente

    def PossessionPieceHuit():
        Base=114
        Bonus=random.randint(0,90)
        return Base+Bonus



    def CalculPiecesDeMonnaie(Bonus):
        Base=random.randint(2,200)

        Valeur=GeneEquipage.ConvertRancon(Bonus+Base)
        return Valeur['PieceDeHuit']

    def CalculMonetaireMarchandise(BonusMarchand,MarchandisesMarchand):
        Valeur=0
        List=["passagers","de monnaie","Passagers","pèlerins","Pèlerins"]
        Port=0
        for k in List:
            lignes = MarchandisesMarchand[MarchandisesMarchand['Cargaison'].astype(str).str.contains(k, case=False, na=False)]
            for _, row in lignes.iterrows():
                Bonus = 0

                BonusAleaNPort = row["ModRichesseNormal"]
                BonusNPort = row["BonusRichesseNormal"]
                BonusAleaPort = row["ModRichessePort"]
                BonusPort = row["BonusRichessePort"]

                if Port == 1:
                    BonusAlea = max(BonusAleaNPort, BonusAleaPort)
                    Bonus = max(BonusPort, BonusNPort)
                else:
                    BonusAlea = BonusAleaNPort
                    Bonus = BonusNPort

                print("Modificateur de richesse aléatoire max:", BonusAlea)
                BonusAlea = random.randint(1, int(BonusAlea))
                Bonus += BonusAlea

                print("Bonus total:", Bonus)
                Valeur += CalculPiecesDeMonnaie(BonusMarchand + Bonus)
        return Valeur

    def CalculTaillePort(Ville):
        CompNegatif = ['Maladie', 'Vide', 'IndigeneHostile']
        CompNeutre = ['SympathisantPirate']

        # Charger les données
        Ports = pd.read_csv(BASE_PATH+"/CaracterePort.csv", sep=";", decimal=",", encoding="cp1252")

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

    def AjoutMarchandise(NameMarchandise, TonnageMarchandise, Name):
        # Chargement de toutes les marchandises disponibles
        MarchandisesDisponibles = pd.read_csv(BASE_PATH + "/Marchandises.csv", sep=";", decimal=",", encoding="cp1252")

        # Filtrage sur la marchandise choisie
        ligne_marchandise = MarchandisesDisponibles[MarchandisesDisponibles['Cargaison'] == NameMarchandise].copy()

        # Ajout des colonnes nécessaires
        ligne_marchandise['Tonnage'] = TonnageMarchandise
        ligne_marchandise['Cours'] = 0

        # Chemin du fichier de cargaison du navire
        output_path = os.path.join(MARCHANDISE_PATH, Name )
        os.makedirs(MARCHANDISE_PATH, exist_ok=True)

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
    def SupprimerMarchandise(NameMarchandise, Name, quantite=1):
        """
        Retire `quantite` de tonnage à la marchandise `NameMarchandise` dans le fichier `Name.csv`.
        Si le tonnage devient <= 0, la ligne est supprimée.
        """

        file_path = os.path.join(MARCHANDISE_PATH, Name)

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

    def ActualiserToutMarchand():
        Listes=pd.read_csv(BASE_PATH + "/Connaissances.csv", sep=";", decimal=",",
                         encoding="cp1252")
        Listes=Listes[Listes['Type']=='Marchand']
        for _, k in Listes.iterrows():
            MiseAJourMarchand(k['Prenom']+"_"+k['Nom'],k['Region'])

    def MiseAJourMarchand(Identite,Region):
        Marchandises=CoursMarchandise(1,Region,"Au port (petit)")
        Valeurs = pd.read_csv(BASE_PATH+"/ValeursRancon.csv", sep=";", decimal=",", encoding="cp1252")

        Marchand = pd.read_csv(BASE_PATH + "/PNJ/" + Identite + ".csv", sep=";",
                               decimal=",", encoding="cp1252")
        Marchand=Marchand.iloc[0]
        CapaciteVente=RencontreVoyage.Test(Marchand['Commerce'])*10+PossessionPieceHuit()

        CapaciteVente=GeneEquipage.ConvertRancon(CapaciteVente)['PieceDeHuit']/600000
        Marchand = pd.read_csv(BASE_PATH + "/Marchandise/" + Identite + "_Marchandise" + Region + ".csv", sep=";",
                               decimal=",", encoding="cp1252")
        CapaciteVente=Marchandises['Tonnage'].sum()*CapaciteVente
        CargaisonVente=Marchandises.copy()
        CargaisonVente['Tonnage']=0
        CargaisonVente['CapaciteAchat']=0
        CargaisonVente['Identite']=Identite
        CapaciteVente=int(CapaciteVente)

        # Select one row's 'Option' using 'Weight' as ponderation
        # Weighted sampling of indices
        for k in range(CapaciteVente):
            indice = np.random.choice(
                Marchandises['Cargaison'],
                size=1,
                replace=False,  # or False, depending on your needs
                p=Marchandises['Tonnage'] / Marchandises['Tonnage'].sum()
            )
            # Extraction de la valeur
            march = indice[0]
            CargaisonVente.loc[CargaisonVente['Cargaison']==march,"Tonnage"]+=1
        CargaisonVente=CargaisonVente[CargaisonVente['Tonnage']>0]

        if len(CargaisonVente) == 0:
            CargaisonVente.loc[len(CargaisonVente)] = [0] * CargaisonVente.shape[1]
        Marchand['Region'] = Region

        Text=""
        Marchand = Marchand.iloc[0]
        CapaciteAchat=Marchand['CapaciteAchat']

        Valeur=Valeurs[Valeurs['PieceDeHuit']==CapaciteAchat]
        Valeur=Valeur.iloc[0]
        BonusCapaciteAchat=random.randint(Valeur['ValeurInferieur']+1,Valeur['ValeurSuperieure'])
        CapaciteAchat=GeneEquipage.ConvertRancon(BonusCapaciteAchat)['PieceDeHuit']

        CargaisonVente['CapaciteAchat']+=CapaciteAchat
        CargaisonVente.to_csv(BASE_PATH+"/Marchandise/" + Identite +"_Marchandise"+Region+ ".csv", sep=";", decimal=",", encoding="cp1252")

        Text=Text+"\n Il peut vous racheter jusqu'a "+str(CapaciteAchat)+ " pieces de huit de marchandise \n"
        Text=Text+"\n Vous pouvez consulter ses marchandises et ses courts dabs le fichier "+ Identite +"_Marchandise"+Region+ ".csv \n"
        return Text,CapaciteAchat,CapaciteVente


    def Vente(NomMarchandise, NomMarchand, Succes,Region):
        # Charger les données
        Marchandises = pd.read_csv(os.path.join(BASE_PATH, "Marchandise", NomMarchandise + ".csv"), sep=";",
                                   decimal=",", encoding="cp1252")
        Marchandises=TriMarchandiseDataframe(Marchandises)
        Marchand = pd.read_csv(os.path.join(BASE_PATH, "PNJ", NomMarchand + ".csv"), sep=";",
                               decimal=",", encoding="cp1252")

        # Calcul du succès de vente
        SuccesMarchand = RencontreVoyage.Test(Marchand['Commerce'].iloc[0])

        Vendeur=pd.read_csv(os.path.join(BASE_PATH, "Marchandise", NomMarchand+"_Marchandise"+Region + ".csv"), sep=";",
                               decimal=",", encoding="cp1252")

        SuccesVente = SuccesMarchand - Succes
        Marchandises['PrixVente'] *= (1 - SuccesVente / 10)

        # Initialisation
        MarchandisesVente = pd.DataFrame(columns=Marchandises.columns)
        CapaciteAchat = Vendeur['CapaciteAchat'].iloc[0]

        # Vente simulée
        while CapaciteAchat > 0:
            Marchandise = Marchandises.sample().iloc[0]  # Une ligne en Series
            prix = Marchandise['PrixVente']

            # Vérifie que le marchand peut acheter
            if prix > CapaciteAchat:
                break

            # Ajouter la ligne à MarchandisesVente
            MarchandisesVente = pd.concat([MarchandisesVente, pd.DataFrame([Marchandise])], ignore_index=True)
            CapaciteAchat -= prix
            SupprimerMarchandise(Marchandise['Cargaison'],NomMarchandise,1)

        ActualiserToutMarchand()
        return MarchandisesVente

    def Pillage(NomNavirePillant,NomNavirePille):
        NavirePillant=pd.read_csv(os.path.join(BASE_PATH, "Navire", NomNavirePillant), sep=";",
                                   decimal=",", encoding="cp1252")
        TonnageMax=NavirePillant['TonnageMax']-NavirePillant['Tonnage']
        TonnageMax=TonnageMax.iloc[0]
        MarchandisePille=pd.read_csv(os.path.join(BASE_PATH, "Marchandise", "Marchandise_"+NomNavirePille ), sep=";",
                                   decimal=",", encoding="cp1252")

        MarchandisePillant=pd.read_csv(os.path.join(BASE_PATH, "Marchandise", "Marchandise_"+NomNavirePillant ), sep=";",decimal=",", encoding="cp1252")

        # Remplacer les NaN (vides ou erreurs) par 0
        MarchandisePille["PrixNormal"] = MarchandisePille["PrixNormal"].fillna(0)
        #MarchandisePille = MarchandisePille.sort_values(by="PrixNormal", ascending=False)
        while (not MarchandisePille.empty and TonnageMax > 0):
            MarchandisePille = pd.read_csv(os.path.join(BASE_PATH, "Marchandise", "Marchandise_" + NomNavirePille),
                                           sep=";",
                                           decimal=",", encoding="cp1252")
            MarchandiseNom=MarchandisePille['Cargaison'].iloc[0]
            AjoutMarchandise(MarchandiseNom,1,"Marchandise_"+NomNavirePillant)
            SupprimerMarchandise(MarchandiseNom, "Marchandise_"+NomNavirePille, 1)
            NavirePillant['Tonnage']+=1
            TonnageMax-=1
        MarchandisePillant.to_csv(os.path.join(BASE_PATH, "Marchandise", "Marchandise_"+NomNavirePillant), sep=";",
                                   decimal=",", encoding="cp1252")

        MarchandisePille.to_csv(os.path.join(BASE_PATH, "Marchandise", "Marchandise_" + NomNavirePille),
                                       sep=";",
                                       decimal=",", encoding="cp1252")

        NavirePillant.to_csv(os.path.join(BASE_PATH, "Navire", NomNavirePillant), sep=";",
                                    decimal=",", encoding="cp1252")




        Text="Le pillage du navire "+NomNavirePille+ " a ete realise"
        return Text

    def RetourMarchandise(Tonnage,Region):
        Marchandises=pd.read_csv(BASE_PATH+"/Marchandises.csv", sep=";", decimal=",", encoding="cp1252")
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












