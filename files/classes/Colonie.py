# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 13:09:55 2023

@author: USER
"""
from ComputeFunction import Maladie

# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 18:24:24 2021

@author: USER
"""

import time as time
import os as os
import pandas as pd
import numpy as np
import sys
import math
import matplotlib.pyplot as plt
import random
from Maladie import *
os.chdir(os.path.abspath(os.path.dirname(__file__)))



Name="Test_EQUIPAGE.csv"
PriorityRole=['Charpenterie','Medecine','Herboristerie','Artisanat','Chirurgie','Survie','Chasse','Peche','Cuisine','Hache','Agriculture']
Comps=['Role','EtatMaladie','Cycle','Maladie','Attitude','Larcins']
Roles={"Chirurgien": ['Chirurgie'],"Medecin":["Medecine"],"Herboriste":['Herboristerie'],"Charpentier":['Charpenterie'],
       "Explorateur":["Survie","Geographie"],"Artisan":['Artisanat'],"Scientifique":['Science'],
        "Voleur":['Athletisme','Discretion','Larcins'],"Chasseur1":['Chasse','Mousquet'],
       "Chasseur2":['Chasse',"Jet1"],"Bucheron":['Hache'],"Agriculteur":['Agriculture'],"Soldat":['Mousquet','Sabre'],"Garde_Sentinelle":['Vigilance'],"Garde_Poursuiveur":['Athletisme'],"Instituteur":['Enseignement'],"Pretre":['Religion'],"Cuisinier":['Cuisine'],"Pecheur":['Peche']}
def Save(TempDF, Name):
    TempDF.to_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252", index=False)


def AttributeRole(NameFile,Roles,Seuil):
    TempDF = pd.read_csv("Colonie/" + NameFile, sep=";", decimal=",", encoding="cp1252")
    Roles = dict(reversed(Roles.items()))
    # Initialisation de la colonne 'ScoreRole'
    TempDF['ScoreRole'] = 0

    # Parcours des rôles et de leurs composants pour calculer les moyennes et mettre à jour les rôles
    for key, value in Roles.items():
        somme = 0
        for comp in value:
            somme += TempDF[comp]
        moy = somme / len(value)
        TempDF.loc[moy >= Seuil, 'Role'] = key
        TempDF.loc[moy >= Seuil, 'ScoreRole'] = moy
    TempDF = TempDF.loc[:, ~TempDF.columns.str.contains('^Unnamed')]
    for key in Roles.keys():
        print(key+" :" +str(len(TempDF[TempDF['Role']==key])))
    TempDF.to_csv("Colonie/"+ NameFile, sep=";", decimal=",", encoding="cp1252", index=False)
AttributeRole(Name,Roles,2)
def MaxGauss(Mean, Std, Recur):
    Result = -np.inf
    if Recur > 0:
        Temp = np.random.normal(Mean, Std, Recur)
        Result = max(Temp)
    return Result


def MinGauss(Mean, Std, Recur):
    Result = np.inf
    if Recur > 0:
        Temp = np.random.normal(Mean, Std, Recur)
        Result = min(Temp)
    return Result


def ConvertListFloatToListInt(Fl):
    Test = Fl

    Fl = [(x + 1 if (x % 1 * 100 <= random.randint(1, 99)) and (x % 1 * 100 != 0) else x) for x in Test]
    FL = [int(Fl) for Fl in Fl]
    return FL


os.chdir(os.path.abspath(os.path.dirname(__file__)))


#############WHAT DO U WANT TO DO ?
def CalculPointDeVie(DF):
    DF['PVMax'] = np.random.normal(5, abs(5 / 10), (len(DF)))
    x = len(DF[DF.Type == 'Soldat'])
    if x != 0:
        DF.loc[DF['Type'] == 'Soldat']['PVMax'] = np.random.normal(6, abs(6 / 10), x)
    x = len(DF[(DF.Type == 'Esclave') | (DF.Type == 'Indien')])
    if x != 0:
        DF[(DF.Type == 'Esclave') | (DF.Type == 'Indien')]['PVMax'] = np.random.normal(5.5, abs(5.5 / 10), x)
    DF[DF['PVMax'] < 5]['PVMax'] = 5
    DF[DF['PVMax'] > 8]['PVMax'] = 8
    DF['PVMax'] = ConvertListFloatToListInt(DF['PVMax'])
    return DF['PVMax']

def LancerDe(col,Bonus):
    ActCourte = 0
    ActLongue = 0
    Total = 0
    Success = 0
    NbCrit = 0
    NbEchec = 0
    NbSimple = 0
    NbDouble = 0
    NbTriple = 0
    if col == 0:
        Test = random.choice(range(12)) + 1
        if Test > 9:
            Success = -1
        elif Test == 1:
            Success = 2
        elif Test <= 5:
            Success = 1
    elif col > 0:
        for h in range(col):
            Test = random.choice(range(10)) + 1
            if Test == 1:
                if Success == -1:
                    Success = 0
                Success = Success + 2
            elif Test <= 5+Bonus:
                if Success == -1:
                    Success = 0
                Success = Success + 1
            elif Test > 9 and Success < 1:
                Success = -1
    ActCourte = 4 - Success + ActCourte
    ActLongue = 7 - Success + ActLongue
    if Success == -1:
        NbCrit += 1
    if Success == 0:
        NbEchec += 1
    if Success == 1:
        NbSimple += 1
    if Success == 2:
        NbDouble += 1
    if Success > 2:
        NbTriple += 1

    Total = Total + Success
    Text = "La personne a effectue " + str(Total) + " succes et un total de " + str(
        ActCourte) + " actions courtes et de" + str(ActLongue) + " actions longues"
    return Total, Text



def Test(Comp, Name, Bonus):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")
    Success = 0
    ActCourte = 0
    ActLongue = 0

    Total = 0
    NbCrit = 0
    NbEchec = 0
    NbSimple = 0
    NbDouble = 0
    NbTriple = 0
    for col in TempDF[Comp]:
        Success = 0
        if col == 0:
            Test = random.choice(range(12)) + 1
            if Test > 9:
                Success = -1
            elif Test == 1:
                if Bonus < -4:
                    Success = 0
                else:
                    Success = 2
            elif Test <= 5 + Bonus:
                Success = 1
        elif col > 0:
            for h in range(col):
                Test = random.choice(range(10)) + 1
                if Test == 1:
                    if Success == -1:
                        Success = 0
                    Success = Success + 2
                elif Test <= 5 + Bonus:
                    if Success == -1:
                        Success = 0
                    Success = Success + 1
                elif Test > 9 and Success < 1:
                    Success = -1

        ActCourte = 4 - Success + ActCourte
        ActLongue = 7 - Success + ActLongue
        if Success == -1:
            NbCrit += 1
        if Success == 0:
            NbEchec += 1
        if Success == 1:
            NbSimple += 1
        if Success == 2:
            NbDouble += 1
        if Success > 2:
            NbTriple += 1
        Total = Total + Success
    Text = "Le groupe a effectue " + str(NbCrit) + " echec critique en " + Comp + "\n" + "Le groupe a effectue " + str(
        NbEchec) + " echec simple en " + Comp + "\n" + "Le groupe a effectue " + str(
        NbSimple) + " reussite mitigé en " + Comp + "\n" + "Le groupe a effectue " + str(
        NbDouble) + " reussite double en " + Comp + "\n" + "Le groupe a effectue " + str(
        NbTriple) + " triple reussite ou plus en " + Comp + "\n" + "Pour un total de " + str(
        ActCourte) + " actions courtes " + Comp + " pour une moyenne de " + str(
        ActCourte / len(TempDF)) + "\n" + "Pour un total de " + str(
        ActLongue) + " actions longues " + Comp + " pour une moyenne de " + str(ActLongue / len(TempDF)) + "\n"
    return Total, Text


def Groupe(Seuil, Comp, Name, NouvName):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")

    TempDF['Groupe'] = TempDF['Groupe'].fillna("")
    TempDF.loc[(TempDF[Comp] >= Seuil) & (~TempDF['Groupe'].str.contains(NouvName)), 'Groupe'] = TempDF[
                                                                                                     'Groupe'] + "," + NouvName
    Resp = TempDF[TempDF[Comp] >= Seuil]
    Save(TempDF, Name)
    return Resp.to_string()


def Tues(Morts, Equipage):
    TempDF = pd.read_csv("Colonie/" + Equipage, sep=";", decimal=",", encoding="cp1252")
    arr_indices_top_drop = random.choices(TempDF.index, k=Morts)
    TempDF.drop(index=arr_indices_top_drop)
    TempDF.to_csv("Colonie/" + Equipage, sep=";", decimal=",", encoding="cp1252")
    return Morts


def Degats(Name, Comp, Bonus):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")
    Degats = 0
    if Comp != "":
        Len = len(TempDF.index)
        Degats, Text = Test(Comp, Name, Bonus)
    return Degats


def Perte(Degats, Name):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")
    Mort = 0
    for k in range(Degats):
        Extract = TempDF.sample()
        Extract['PV'] -= 1
        TempDF.loc[Extract.index, 'PV'] = int(Extract['PV'].iloc[0])
        if (int(Extract['PV'].iloc[0]) < 1) and (
                len(TempDF) > 0):  ##Si l'element selectonne a 0 PV, on le supprime du groupe
            TempDF = TempDF.drop(Extract.index)
            Mort += 1


        elif len(TempDF) < 1:
            TempDF = pd.DataFrame()
            print(Name + " a été decime")
    TempDF.to_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")

    return Mort


def SelectRandom(Name, Nb):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")
    Res = pd.DataFrame()
    for k in range(Nb):
        Res = Res._append(TempDF.sample())
    Text = Res.to_string()
    return Text


###Exemple, cl
def NommerRandom(Nom, Name):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252")
    dfupdate = TempDF.sample()
    dfupdate["Nom"] = Nom
    TempDF.update(dfupdate)
    TempDF.to_csv("Colonie/" + Name, sep=";", decimal=",", encoding="cp1252", index=False)


def AfficheColonne(Name, Comp):
    TempDF = pd.read_csv("Colonie/" + Name, sep=";", decimal=",", encoding='cp1252')
    print(TempDF[Comp].value_counts())
    return TempDF[Comp].value_counts().to_string()


def TestRole(Role,Name):
    Roles = pd.read_csv("RoleColonie.csv", sep=";", decimal=",", encoding="cp1252")
    TempDF = pd.read_csv("Colonie/"+Name, sep=";", decimal=",", encoding="cp1252")
    TempDF=TempDF[TempDF['Role']==Role]
    Comp=Roles[Roles['Role']==Role]['Competence']
    SuccesTotal=0
    Echec=0
    for k in range(len(TempDF)):
        Succes=LancerDe(TempDF[Comp].iloc[k],0)[0]
        SuccesTotal = SuccesTotal +Succes[0]
        if Succes<1:
            Echec=Echec+1
    return SuccesTotal,Echec
def TestSoins(Name):
    Chirurgie=TestRole("Chirurgien",Name)
    Medecine=TestRole("Medecin",Name)

NameFile="Test_EQUIPAGE.csv"
Days=10


Maladie.TestMaladie(1,True,NameFile)

