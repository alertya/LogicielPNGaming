
import os as os
import pandas as pd
import numpy as np

import random
import tkinter as tk
from tkinter import ttk, messagebox

import utils
from ComputeFunction import GeneEquipage

from config import *


def InitialisationFiche(Identite):
    PJ=pd.DataFrame()
    PJ['Competences']=pd.read_csv(BASE_PATH+'/Competences.csv', sep=";", decimal=",", encoding='cp1252')['Competence']
    PJ['Valeur']=0
    PJ['Augmente']=0
    PJ['Experience']=0
    PJ['Metier'] = pd.read_csv(BASE_PATH + '/Competences.csv', sep=";", decimal=",", encoding='cp1252')[
        'Metier']
    PJ['Type']=pd.read_csv(BASE_PATH + '/Competences.csv', sep=";", decimal=",", encoding='cp1252')[
        'Type']


    return PJ
def AttributionCompetence(PJ,Compteurs,Bonus,Metiers):
    MetiersCombat = ['Sabre', 'Rapiere', 'Dague', 'Hache', 'ArmesBlanches1']
    Competences=pd.read_csv(BASE_PATH+'/Competences.csv', sep=";", decimal=",", encoding='cp1252')
    Competences.loc[Competences['Competence'].isin(Metiers), 'Metier'] = 0
    Competences.loc[Competences['Competence'].isin(MetiersCombat), 'Metier'] = 0
    Competences = Competences[Competences['Metier'] != 1]
    Increment=0
    while Increment<5 and Increment<100:
        Competence=Competences.sample().iloc[0]
        CompetenceLabel=Competence['Competence']
        Type=Competence['Type']
        # Vérifie si la compétence a déjà une valeur non nulle dans PJ
        # Et si le compteur du type est encore disponible
        while (

                PJ.loc[PJ['Competences'] == CompetenceLabel, 'Valeur'].values[0] != 0
                or Compteurs[Type] < 1
        ):


            Competence = Competences.sample().iloc[0]
            CompetenceLabel = Competence['Competence']
            Type = Competence['Type']

        Compteurs[Type]-=1
        PJ.loc[PJ['Competences'] == CompetenceLabel, 'Valeur']=Bonus
        if CompetenceLabel in Metiers:
            Compteurs[Competence['Type']] += 1

        Increment+=1
    return PJ
def CalculOrigineSociale(PJ,Origine):
    Origines=utils.ListOriginesSociales()

    while Origine=='Aleatoire':
        print(Origine)
        Origine=random.sample(Origines,1)[0]
        print(Origine)
    Metiers=['9999999']
    liste_cles = utils.ListCategorieCompetence()
    Compteurs = {cle: 0 for cle in liste_cles}
    if Origine=="Amuseur":
        Metiers=['Art','Lire']
        Compteurs['Technique']=1
        Compteurs['Physique'] = 2
        Compteurs['Sociale'] = 2
        Compteurs['Combat'] = 1
    if Origine=="Armee":
        Metiers=['Balistique','Escrime']
        Compteurs['Technique']=1
        Compteurs['Maritime'] = 1
        Compteurs['Connaissance'] = 1
        Compteurs['Physique'] = 1
        Compteurs['Sociale'] =1
        Compteurs['Combat'] = 2
    if Origine=="Bourgeois":
        Metiers=['Droit','Balistique','Etiquette','Hydrographie','Lire','Politique','Science']
        Compteurs['Connaissance']=2
        Compteurs['Sociale'] = 3
    if Origine=="Colon":
        Metiers=['Agriculture','Hydrographie','Survie']
        Compteurs['Technique']=2
        Compteurs['Physique'] = 3
        Compteurs['Maritime'] = 1
        Compteurs['Combat'] = 1
    if Origine=="Intellectuel":
        Metiers=['ConnSpe1','Balistique','Etiquette','Intendance','Ingénierie navale','Hydrographie','Lire','Medecine','Navigation','Politique','Science']
        Compteurs['Connaissance']=3
        Compteurs['Maritime'] = 1
        Compteurs['Sociale'] = 1
    if Origine=="Malandrin":

        Metiers=['Larcins']
        Compteurs['Physique'] = 3
        Compteurs['Sociale'] = 1
        Compteurs['Combat'] = 1
    if Origine=="Marine":
        Metiers=['Voilerie','Balistique','Cartographie','Connaissances nautiques','Signalisation','Hydrographie','Navigation']
        Compteurs['Physique'] = 1
        Compteurs['Maritime'] = 3
        Compteurs['Technique'] = 1
        Compteurs['Connaissance'] = 1
    if Origine=="Noblesse":
        Metiers=['Balistique','Etiquette','Hydrographie','Lire','Navgation','Politique']
        Compteurs['Connaissance']=1
        Compteurs['Maritime'] = 1
        Compteurs['Sociale'] = 3
        Compteurs['Combat'] = 1
        Compteurs['Physique'] = 1
    if Origine=="Paysan":
        Metiers=['Artisanat']
        Compteurs['Physique'] = 2
        Compteurs['Sociale'] = 2
        Compteurs['Technique'] = 2
    if Origine=="Tribu":
        Metiers=['Art','Charpenterie','Herboristerie','Survie','Arc','Javelot']
        Compteurs['Connaissance']=1
        Compteurs['Technique'] = 1
        Compteurs['Sociale'] = 1
        Compteurs['Combat'] = 1
        Compteurs['Physique'] = 2
    AttributionCompetence(PJ,Compteurs,2,Metiers)
    return PJ

def CalculEvenement(PJ,Evenement):
    Evenements=utils.ListeEvenement()

    while Evenement=='Aleatoire':
        Evenement=random.sample(Evenements,1)[0]
    Metiers=['9999999']
    liste_cles = utils.ListCategorieCompetence()
    Compteurs = {cle: 0 for cle in liste_cles}
    if Evenement=="Amoureuse":
        Metiers=['Escrime','Etiquette']

        Compteurs['Physique'] = 1
        Compteurs['Sociale'] = 3
        Compteurs['Combat'] = 1
    if Evenement=="Autoritaire":

        Compteurs['Physique'] = 1
        Compteurs['Sociale'] = 2
        Compteurs['Combat'] = 1
        Compteurs['Maritime'] = 1
    if Evenement=="Choyee":

        Compteurs['Connaissance'] = 2
        Compteurs['Sociale'] = 3
    if Evenement=="Laborieuse":

        Compteurs['Technique'] = 1
        Compteurs['Sociale'] = 1
        Compteurs['Maritime'] = 1
        Compteurs['Physique'] = 2
        Compteurs['Combat'] = 1
    if Evenement=="Amoureuse":
        Metiers=['Escrime','Etiquette']

        Compteurs['Physique'] = 1
        Compteurs['Sociale'] = 3
        Compteurs['Combat'] = 1
    if Evenement=="Orpheline":
        Metiers=['Larcins']

        Compteurs['Connaissance'] = 1
        Compteurs['Sociale'] =1
        Compteurs['Technique'] = 1
        Compteurs['Physique'] = 2
        Compteurs['Combat'] = 1
    if Evenement=="Rebelle":
        Metiers=['Droit','Larcins','Escrime']

        Compteurs['Connaissance'] = 1
        Compteurs['Sociale'] =2
        Compteurs['Combat'] = 2
    if Evenement=="Solitaire":
        Metiers=['Art','Lire','Science']

        Compteurs['Connaissance'] = 2
        Compteurs['Technique'] =1
        Compteurs['Sociale'] = 1
        Compteurs['Combat'] = 1
    if Evenement=="Studieuse":
        Metiers=['Balistique','Cartographie','ConnSpe','Ingenierie navale','Hydrographie','Lire','Medecine','Navigation','Science']
        Compteurs['Connaissance'] = 3
        Compteurs['Maritime'] =2
    if Evenement=="Mer":
        Metiers=['Voilerie','Signalisation','Connaissances nautiques','Navigation','Hydrographie','Escrime']

        Compteurs['Connaissance'] = 1
        Compteurs['Technique'] =2
        Compteurs['Physique'] = 1
        Compteurs['Combat'] = 1
        Compteurs['Maritime'] =3
    if Evenement=="Turbulente":
        Metiers=['Larcins','Escrime']

        Compteurs['Physique'] = 2
        Compteurs['Combat'] = 1
        Compteurs['Sociale'] =2
    AttributionCompetence(PJ,Compteurs,1,Metiers)
    return PJ
def GeneratePJ(Nam,Origine,Evenement1,Evenement2,Profession,NBFiches):
    Analyses=pd.DataFrame()
    for k in range(NBFiches):
        Name=Nam+str(k)
        print("Intialisation de la fiche")
        PJ=InitialisationFiche(Name)
        print("Calcul de l'origine sociale")
        PJ=CalculOrigineSociale(PJ,Origine)
        print("Calcul de l'evenement de jeunesse 1")
        PJ=CalculEvenement(PJ,Evenement1)
        print("Calcul de l'evenement de jeunesse 2")
        PJ=CalculEvenement(PJ,Evenement2)
        print("Calcul des points de professions")
        Bonus,PJ=AttributionProfession(PJ,Profession)
        print("Ajout des compétences en touche finale")
        PJ=AjoutFinale(PJ,Bonus)
        print("Mise en forme du perso sur "+BASE_PATH+"/PJ/"+Name+".csv")
        TempPJ=Analayse(PJ)
        TempPJ.columns = [f"Comp_{Name}", f"Valeur_{Name}"]
        print("CalculAnalysePJ")
        Analyses = pd.concat([Analyses, TempPJ], axis=1)
        #PJ.to_csv(BASE_PATH + "/PJ/" + Name + ".csv", sep=";", decimal=",", encoding='cp1252')
        MiseEnForme(PJ,Name)
        Text="Analyse des perso sur "+BASE_PATH+"/PJ/"+Name+"_Analyse.csv"
        CalculCarac(Name)
    Analyses.to_csv(BASE_PATH+"/PJ/"+Name+"_Analyse.csv",sep=";",encoding="cp1252",decimal=",")
    return Text,PJ
def AttributionProfession(PJ,Profession):
    Professions = pd.read_csv(BASE_PATH + '/Professions.csv', sep=";", decimal=",", encoding='cp1252')
    Profession=Professions[Profession]
    Profession=Profession.dropna()
    k=0
    cpt=0
    while k<12 and cpt<100:
        Competence=Profession.sample().iloc[0]
        while PJ.loc[PJ['Competences'] == Competence, 'Valeur'].values[0] >2 and cpt<100:
            Competence = Profession.sample().iloc[0]
            cpt += 1
        PJ.loc[PJ['Competences'] == Competence, 'Valeur']+=1
        k+=1

    Bonus=max(0,12-k)
    return Bonus,PJ

def AjoutFinale(PJ,Bonus):
    CompetencesInitial = pd.read_csv(BASE_PATH + '/Competences.csv', sep=";", decimal=",", encoding='cp1252')

    ####On filtre les compétences de métier non développées
    filtre = PJ.loc[~((PJ['Metier'] == 1) & (PJ['Valeur'] == 0))]
    Opti=1 ##Si on cherche à optimiser les gains
    Seuil=2

    for k in range(10+Bonus):
        filtered_PJ = filtre.loc[
            ~(
                    ((PJ['Valeur'] > 2) | (PJ['Augmente'] != 0) | (PJ['Augmente'] == "X"))
            )
        ]


        Competences = Optimisation(filtered_PJ, Seuil,Opti)
        Competence = Competences.sample().iloc[0]
        CompetenceLabel=Competence['Competences']


        PJ.loc[PJ['Competences'] == CompetenceLabel, 'Valeur']+=1
        PJ.loc[PJ['Competences'] == CompetenceLabel, 'Augmente']="X"
        Competences = Competences[Competences['Competences'] != CompetenceLabel]

    PJ['Metier']=pd.read_csv(BASE_PATH + '/Competences.csv', sep=";", decimal=",", encoding='cp1252')['Metier']
    # Sauvegarder dans un fichier
    return PJ


def MiseEnForme(PJ,Name):
    TypComp=['Connaissance','Technique','Maritime','Physique','Sociale','Combat']
    #NewPJ = pd.DataFrame(index=PJ.index)  # même index que PJ, mais sans colonnes
    TempPJ = PJ.copy()
    NewPJ = pd.DataFrame(index=[0])

    for k in TypComp:
        subdf = PJ[PJ['Type'] == k]

        for row in range(len(subdf)):
            # Prend la première ligne de ce type

            ligne = subdf.iloc[row]
            NewPJ.at[row, 'Comp' + k] = ligne['Competences']
            NewPJ.at[row, 'Valeur' + k] = ligne['Valeur']
            NewPJ.at[row, 'Augmente' + k] = str(ligne['Augmente'])
            NewPJ.at[row, 'Experience' + k] = ligne['Experience']
    NewPJ.to_csv(BASE_PATH + "/PJ/" + Name + ".csv", sep=";", decimal=",", encoding='cp1252')


def ReturnComp(Competence,PJ):
    Comps = pd.read_csv(BASE_PATH + '/Competences.csv', sep=";", decimal=",", encoding='cp1252')
    Comp=Comps[Comps['Competence']==Competence]
    Type=Comp['Type'].iloc[0]
    PJ = PJ[PJ['Comp'+Type] == Competence].iloc[0]
    return PJ['Comp'+Type] ,PJ['Valeur' + Type],PJ['Experience'+Type]


def CalculCarac(Name):
    PJ = pd.read_csv(BASE_PATH + "/PJ/" + Name + ".csv", sep=";", decimal=",", encoding='cp1252')
    Ada=0
    Adr=0
    Charisme=0
    Eru=0
    Exp=0
    Force=0
    Perception=0
    Pouvoir=0
    Resistance=0
    PJCarac=['Adaptabilite','Adresse','Charisme','Erudition','Expression','Force','Pouvoir','Perception','Resistance']
    PJ['Carac']=''
    PJ.loc[:8, 'Carac']=PJCarac

    Temp=pd.read_csv(BASE_PATH + '/CompToCarac.csv', sep=";", decimal=",", encoding='cp1252')
    Temp.fillna(0, inplace=True)
    Comps=pd.read_csv(BASE_PATH + '/Competences.csv', sep=";", decimal=",", encoding='cp1252')
    for k in Comps['Competence']:
        Valeur=ReturnComp(k,PJ)[1]

        Adr+=Temp[Temp['Competence']==k]['Adresse'].iloc[0]*Valeur

        Ada += Temp[Temp['Competence'] == k]['Adaptabilite'].iloc[0]*Valeur
        Charisme += Temp[Temp['Competence'] == k]['Charisme'].iloc[0]*Valeur
        Eru += Temp[Temp['Competence'] == k]['Erudition'].iloc[0]*Valeur
        Exp += Temp[Temp['Competence'] == k]['Expression'].iloc[0]*Valeur
        Force += Temp[Temp['Competence'] == k]['Force'].iloc[0]*Valeur
        Pouvoir += Temp[Temp['Competence'] == k]['Pouvoir'].iloc[0]*Valeur
        Perception += Temp[Temp['Competence'] == k]['Perception'].iloc[0]*Valeur
        Resistance += Temp[Temp['Competence'] == k]['Resistance'].iloc[0]*Valeur

    Somme=Ada+Adr+Charisme+Eru+Exp+Force+Perception+Pouvoir+Resistance
    Adr=Adr/Somme*45
    Ada = Ada / Somme * 45
    Charisme = Charisme / Somme * 45
    Eru = Eru / Somme * 45
    Exp = Exp / Somme * 45
    Force = Force / Somme * 45
    Pouvoir = Pouvoir / Somme * 45
    Perception = Perception / Somme * 45
    Resistance = Resistance / Somme * 45
    PJ.loc[0, 'ValeurCarac'] = Ada
    PJ.loc[1, 'ValeurCarac'] = Adr
    PJ.loc[2, 'ValeurCarac']= Charisme
    PJ.loc[3, 'ValeurCarac'] = Eru
    PJ.loc[4, 'ValeurCarac'] = Exp
    PJ.loc[5, 'ValeurCarac'] = Force
    PJ.loc[6, 'ValeurCarac'] = Pouvoir
    PJ.loc[7, 'ValeurCarac'] = Perception
    PJ.loc[8, 'ValeurCarac'] = Resistance
    PJ.to_csv(BASE_PATH + "/PJ/" + Name + ".csv", sep=";", decimal=",", encoding='cp1252')


def ModifCarac(Name,Carac,Valeur):
    PJ = pd.read_csv(BASE_PATH + "/PJ/" + Name + ".csv", sep=";", decimal=",", encoding='cp1252')
    PJ[PJ['Carac']==Carac]['ValeurCarac']=Valeur
    PJ.to_csv(BASE_PATH + "/PJ/" + Name + ".csv", sep=";", decimal=",", encoding='cp1252')


def Analayse(PJ):
    TempPJ = PJ.copy()
    TempPJ=TempPJ.sort_values('Valeur', ascending=False)
    TempPJ = TempPJ.drop(columns=["Augmente","Experience","Metier","Type"])
    return TempPJ.reset_index(drop=True)

def Optimisation(PJ,Seuil,Opti):
    if Opti==2:  ###Optimisation maximale, on ne développe que les compétences déjà élevées
        while PJ[PJ['Valeur'] >= Seuil].empty:
            Seuil=Seuil-1
        return PJ[PJ['Valeur']>=Seuil]
    if Opti==0: ##Aucune optimisation on retourne simplement la fiche telle qu'elle est
        return PJ
    if Opti==1:  ##Optimisation intermediaire, on ne développe que les compétences supérieure à 0
        return PJ[PJ['Valeur'] >= 1]