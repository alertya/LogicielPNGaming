
import numpy as np
import random
import warnings
import time
import csv
import re
import os
import sys
import math
import tkinter as tk
from tkinter import ttk
import pandas as pd

import pandas as pd
from config import *
import matplotlib.pyplot as plt

def ListeRegions():
    df=pd.read_csv(BASE_PATH+"/ListeRegions.csv",sep=";",encoding="cp1252")
    return df['RegionsCommerciale'].tolist()
def ListesZones():
    Des=pd.read_csv(BASE_PATH+"/DeRencontre.csv", sep=";", decimal=",", encoding="cp1252")
    return Des["Zone"].tolist()
def ListesPort():
    Des = pd.read_csv(BASE_PATH + "/DeRencontre.csv", sep=";", decimal=",", encoding="cp1252")
    AExclure = ['Mer', 'côte', 'route', 'forain']

    # Liste originale
    zones = Des["Zone"].dropna().astype(str).tolist()

    # Filtrage : garder seulement les zones qui ne contiennent aucun mot interdit
    zones_filtrees = [z for z in zones if not any(mot.lower() in z.lower() for mot in AExclure)]

    return zones_filtrees
def TypeIndivuduals():
    TempDF=pd.read_csv(BASE_PATH+"/ListeProf.csv",sep=";",decimal=",",encoding="cp1252")

    return TempDF['Type'].tolist()
###Return the files in the specific Folder paramater with the specific Extension parameter
def ListFiles(Folder, Extension):
    arr_txt = [x for x in os.listdir(Folder) if x.endswith("." + str(Extension))]
    return arr_txt
def ListeCompetences():
    TempDF=pd.read_csv(BASE_PATH+"/ListeProf.csv",sep=";",decimal=",",encoding="cp1252")
    Comps=TempDF.columns[1:]
    Comps=Comps.tolist()
    Comps.remove("Salaire")
    Comps.remove("Employeur")
    return Comps
def ListeCompetencesCombat():
    Comps=ListeCompetences()
    Combats=Comps[59:69]
    return Combats
def ListNavire(Folder,Extension):
    Files= ListFiles(Folder,Extension)
    Navires = [s for s in Files if "EQUIPAGE" not in s]
    if not(Navires):
        Navires=['Veuillez generer un navire (possible via une simulation de rencontre en mer ou manuellement)']
    return Navires
def ListEquipage(Folder,Extension):
    Files= ListFiles(Folder,Extension)
    Equips = [s for s in Files if "EQUIPAGE" in s]
    if not (Equips):
        Equips = ['Veuillez generer un equipage']
    return Equips

def ListMarchandise(Folder,Extension):
    Files= ListFiles(Folder,Extension)
    Equips = [s for s in Files]
    if not (Equips):
        Equips = ['Veuillez generer une liste de marchandise']
    return Equips
def create_entry(root,name ,value_default,row,column,**kwargs):
    script_label = tk.Label(root, text=name)
    script_label.grid(row=row, column=column)
    Value=tk.StringVar()
    Value.set(value_default)
    script_entry = tk.Entry(root,textvariable=Value,**kwargs)

    script_entry.grid(row=row, column=column+1)
    return script_label,script_entry

def create_list_equipage(root,name ,listing,row,column,**kwargs):
    script_label = tk.Label(root, text=name)
    script_label.grid(row=row, column=column)
    script_list = ttk.Combobox(root, values=ListEquipage(EQUIPAGE_PATH,"csv"),postcommand=lambda: script_list.configure(values=ListEquipage(EQUIPAGE_PATH,"csv")),**kwargs)
    script_list['state']='readonly'
    script_list.grid(row=row, column=column+1)
    script_list.current(0)
    script_list.update()
    return script_label,script_list

def create_list_marchandise(root,name ,listing,row,column,**kwargs):
    script_label = tk.Label(root, text=name)
    script_label.grid(row=row, column=column)
    script_list = ttk.Combobox(root, values=ListMarchandise(MARCHANDISE_PATH,"csv"),postcommand=lambda: script_list.configure(values=ListMarchandise(MARCHANDISE_PATH,"csv")),**kwargs)
    script_list['state']='readonly'
    script_list.grid(row=row, column=column+1)
    script_list.current(0)
    script_list.update()
    return script_label,script_list
####Combobos Entry without postcommand
def create_list_static(root,name ,listing,row,column,**kwargs):
    script_label = tk.Label(root, text=name)
    script_label.grid(row=row, column=column)
    script_list = ttk.Combobox(root, values=listing,**kwargs)
    script_list['state']='readonly'
    script_list.grid(row=row, column=column+1)
    script_list.current(0)
    return script_label,script_list
def create_list_navire(root,name ,listing,row,column,**kwargs):
    script_label = tk.Label(root, text=name)
    script_label.grid(row=row, column=column)
    script_list = ttk.Combobox(root, values=ListNavire(NAVIRE_PATH,"csv"),postcommand=lambda: script_list.configure(values=ListNavire(NAVIRE_PATH,"csv")),**kwargs)
    script_list['state']='readonly'
    script_list.grid(row=row, column=column+1)
    script_list.current(0)
    return script_label,script_list


def ConcatAvecColonne(df1, df2):
    all_cols = list(set(df1.columns).union(df2.columns))
    for df in [df1, df2]:
        for col in all_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[all_cols]
    return pd.concat([df1, df2], ignore_index=True)

def ListeMarchandiseUnique():
    Marchandise=pd.read_csv(BASE_PATH+"/Marchandises.csv",sep=";",decimal=",",encoding="cp1252")
    Marchandise=Marchandise['Cargaison']
    Marchandise=Marchandise.to_list()

    Marchandise = [str(elem) for elem in Marchandise]


    Marchandise_SansChiffre = list(set(Marchandise))
    # Tri alphabétique insensible à la casse
    Marchandise_SansChiffre.sort(key=lambda x: (str(x).lower() if x is not None else ""))
    # Supprimer les chiffres de chaque chaîne

    return Marchandise_SansChiffre

def afficher_donnees(self, liste):
    self.listebox.delete("0.0", "end")
    for item in liste:
        self.listebox.insert("end", f"- {item}\n")

def mettre_a_jour_liste(self, event=None):
    recherche = self.entry_recherche.get().lower()
    filtres = [item for item in self.donnees if recherche in item.lower()]
    self.afficher_donnees(filtres)




def ConvertListFloatToListInt(fl_list):
    # Appliquer la transformation conditionnelle
    updated = [
        x + 1 if (x % 1 * 100 <= random.randint(1, 99)) and (x % 1 * 100 != 0) else x
        for x in fl_list
    ]
    # Convertir les résultats en entiers
    result = [int(x) for x in updated]
    return result

def ConvertFloatToInt(x):
    if (x % 1 * 100 <= random.randint(1, 99)) and (x % 1 * 100 != 0):
        x += 1
    return int(x)

def Test(Nb,Bonus):
    Success=0
    for k in range(Nb):
        Success=0
        if Nb==0:
            Test=random.choice(range(12))+1
            if Test>9:
                Success=-1
            elif Test==1:
                Success=2
            elif Test<=5+Bonus:
                Success=1
        elif k>0:
            for h in range(k):
                Test=random.choice(range(10))+1
                if Test==1:
                    if Success==-1:
                        Success=0
                    else:
                        Success=Success+2
                elif Test<=5+Bonus:
                    if Success==-1:
                        Success=0
                    Success=Success+1
                elif Test>9 and Success<1:
                    Success=-1
    return Success

def MaxGauss(Mean,Std,Recur):
    Result=-np.inf
    if Recur >0:
        Temp=np.random.normal(Mean,Std,Recur)
        Result=max(Temp)
    return Result
def MinGauss(Mean,Std,Recur):
    Result=np.inf
    if Recur >0:
        Temp=np.random.normal(Mean,Std,Recur)
        Result=min(Temp)
    return Result


def ListVoilure():
    return ['SurToile','Normal','SousToile']

def ListAllure():
    Allure=["Pres",'Largue',"Grand largue","Vent arriere"]
    return Allure


def VideFichierSaufEntete(file_path):
    # Chemin du fichier CSV

    # Lire les en-têtes
    with open(file_path, mode='r', newline='', encoding='cp1252') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Lire uniquement la première ligne

    # Réécrire le fichier avec uniquement les en-têtes
    with open(file_path, mode='w', newline='', encoding='cp1252') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
def SuppressionColonneUnnamed(file_path):
    # Lire le fichier et ignorer les colonnes Unnamed
    df = pd.read_csv(file_path,sep=";",decimal=",",encoding='cp1252')

    # Supprimer les colonnes dont le nom commence par "Unnamed"
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

    # Réécrire le fichier sans les colonnes Unnamed
    df.to_csv(file_path, index=False,sep=";",decimal=",",encoding='cp1252')
###Supprime tous les fichiers génére dans tous les dossiers
def Reset():
    Folders = ["Equipage", "Marchandise", "Navire", "PNJ", "Rencontre"]
    FileConnaissance=os.path.join(BASE_PATH,"Connaissances.csv")
    print(FileConnaissance)
    VideFichierSaufEntete(FileConnaissance)
    SuppressionColonneUnnamed(FileConnaissance)
    for folder in Folders:
        folder=os.path.join(BASE_PATH+"/"+folder)
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Supprimé : {file_path}")
        else:
            print(f"Dossier introuvable : {folder}")

def ListCaracteristique():
    return ['Adaptabilite','Chance','Adresse','Erudition','Force','Charisme','Expression','Resistance']
def ListOriginesSociales():
    return ['Aleatoire','Amuseur','Armee','Bourgeois','Colon','Intellectuel','Malandrin','Marine','Noblesse','Paysan','Tribu']
def ListeEvenement():
    return ['Aleatoire','Amoureuse','Autoritaire','Choyee','Orpheline','Laborieuse','Rebelle','Solitaire','Mer','Turbulente']
def ListCategorieCompetence():
    return ['Connaissance','Technique','Maritime','Physique','Sociale','Combat']
def ListProfession(Origine):
    Metiers=pd.read_csv(BASE_PATH+"/Professions.csv",sep=";",decimal=",",encoding="cp1252")

    IndexStart=0
    IndexEnd=len(Metiers)
    if Origine=='Amuseur':

        IndexEnd=7
    if Origine=='Paysan':
        IndexStart = 7
        IndexEnd=13
    if Origine=='Bourgeois':
        IndexStart = 13
        IndexEnd=21
    if Origine=='Colon':
        IndexStart = 21
        IndexEnd=28
    if Origine=='Intellectuel':
        IndexStart = 28
        IndexEnd=34
    if Origine=='Malandrin':
        IndexStart = 34
        IndexEnd=45
    if Origine=='Marine':
        IndexStart = 45
        IndexEnd=64
    if Origine=='Armee':
        IndexStart = 64
        IndexEnd=78
    if Origine=='Noblesse':
        IndexStart = 78
        IndexEnd=83
    if Origine=='Tribu':
        IndexStart = 85
        IndexEnd=92
    Metiers=Metiers.columns
    Metiers=Metiers[IndexStart:IndexEnd]

    Metiers=list(Metiers)
    return Metiers




# Mise à jour dynamique des professions en fonction de l'origine
def update_profession(selected_origine, profession_widget):
    # Récupère la nouvelle liste selon l'origine
    new_prof_list = ListProfession(selected_origine)

    # Met à jour les options du menu déroulant
    profession_widget.configure(values=new_prof_list)

    # Sélectionne la première option automatiquement si dispo
    if new_prof_list:
        profession_widget.set(new_prof_list[0])
    else:
        profession_widget.set("")


def lancer_de(col, bonus):
    """Retourne le nombre de réussites en lançant des dés selon une compétence et un bonus."""
    col=int(col)
    success = 0
    if col == 0:
        test = random.randint(1, 12)
        if test == 1:
            success = 2
        elif test > 9:
            success = -1
        elif test <= 5:
            success = 1
    else:
        for _ in range(col):
            roll = random.randint(1, 10)
            if roll == 1:
                success = max(success, 0) + 2
            elif roll <= 5 + bonus:
                success = max(success, 0) + 1
            elif roll > 9 and success < 1:
                success = -1
    return success, f"{success} succès obtenus"


def TestValeurNonNumerique(Nb,Bonus):
    Succes=Test(Nb,Bonus)
    return 7-Succes,4-Succes


def Compute(Prof):
    Base = random.randint(1, 365)
    Metier = random.randint(1, 10)

    if Base < 190:
        Val = 0
    elif Base < 310:
        Val = 1
    elif Base < 355:
        Val = 2
    else:
        Val = 3
    if Metier <= 2:
        Bonus = 1
    elif Metier <= 6:
        Bonus = 2
    elif Metier <= 8:
        Bonus = 3
    else:
        Bonus = 4
    Res = Val + Prof * Bonus

    Rest = Res % 1

    if Rest > 0:
        Tes = random.randint(1, 10)
        if Tes > Res:
            Res = Res.astype(int)
        else:
            Res = Res.astype(int) + 1

    return int(Res)


def RandomNom():
    df=pd.read_csv(BASE_PATH+"/Prenoms.csv",sep=";",encoding="cp1252",decimal=",")
    Nom=df['Nom'].sample()
    Prenom=df['Prenom'].sample()
    return Prenom,Nom


def PaysToRegion(Pays):
    df=pd.read_csv(BASE_PATH+"/PaysRegion.csv",sep=";",encodinf="cp1252",decimal=",")
    df=df[df['Pays']==Pays]
    return df['Region'].iloc[0]