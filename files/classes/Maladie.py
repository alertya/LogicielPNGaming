import os
import time
import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt
from tkinter import messagebox




# ----------------- FONCTIONS DE BASE ---------------- #



def convert_float_to_int_list(fl):
    """Convertit une liste de float en int en tenant compte d'une chance aléatoire."""
    return [int(x + 1 if (x % 1 * 100 <= random.randint(1, 99) and x % 1 != 0) else x) for x in fl]

# ----------------- POINTS DE VIE ---------------- #

def calcul_pv(DF):
    """Assigne les PV max en fonction du type de personnage."""
    DF['PVMax'] = np.random.normal(5, 0.5, len(DF))
    mask_soldat = DF['Type'] == 'Soldat'
    mask_autres = DF['Type'].isin(['Esclave', 'Indien'])

    DF.loc[mask_soldat, 'PVMax'] = np.random.normal(6, 0.6, mask_soldat.sum())
    DF.loc[mask_autres, 'PVMax'] = np.random.normal(5.5, 0.55, mask_autres.sum())

    DF['PVMax'] = DF['PVMax'].clip(5, 8)
    DF['PVMax'] = convert_float_to_int_list(DF['PVMax'])
    return DF['PVMax']

# ----------------- MALADIES ---------------- #

def reconnaissance_malade_equipage(name):
    """Vérifie si un malade est détecté dans l'équipage."""
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    df = Equipage.HommesValides(df)

    proba_detection = 0
    for type_ in ['Medecin', 'Chirurgien', 'Herboriste']:
        for _, row in df[df['Type'] == type_].iterrows():
            proba_detection += lancer_de(row['Medecine'], 0)[0] * 20

    for malade in df['Maladie'].notna():
        if random.random() > proba_detection / len(df):
            return 0
    return 1





def evolution_maladie(nb_jours, name):
    """Fait évoluer les maladies existantes dans l'équipage."""
    text = ''
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    maladies = pd.read_csv(BASE_PATH+"/Maladie.csv", sep=";", decimal=",", encoding="cp1252")
    df["Maladie"] = df["Maladie"].astype(str)
    df.loc[df['Famine'] < -29, 'Maladie'] = 'Famine'

    for _ in range(nb_jours):
        df['Cycle'] -= 1
        for idx in df[(df['Maladie'].notna()) & (df['Cycle'] == 0)].index:
            mal_nom = df.loc[idx, 'Maladie']
            mal = maladies[maladies['Maladie'] == mal_nom].iloc[0]
            df.loc[idx, 'Cycle'] = mal['Cycle']
            if mal['PopulationFragile'] == "Européens":
                mal['Virulence'] -= 2
            if mal['PopulationResistante'] == "Européens":
                mal['Virulence'] += 2

            # Lancer de dés pour savoir si la maladie progresse, régresse ou tue
            contraction = lancer_de(2, mal['Virulence'])[0]
            # Si le lancer est < 1, la maladie progresse
            if contraction <= 0:
                df.loc[idx, 'EtatMaladie'] += mal['ReductionEtat']
                # Limiter la gravité au maximum défini
                df.loc[idx, 'EtatMaladie'] = max(df.loc[idx, 'EtatMaladie'], mal['GraviteMax'])
                print(df.loc[idx, 'EtatMaladie'])
                # Vérification si le personnage meurt
                if df.loc[idx, 'EtatMaladie'] < -5:
                    print("MORT DE MALADIE \n \n")
                    text += f"Un homme a succombé de la {mal_nom}\n"
                    messagebox.showinfo("Info", f"Un homme a succombé de la {mal_nom}")

            # Si le lancer est > 1, la maladie régresse
            elif contraction > 1:
                df.loc[idx, 'EtatMaladie'] += 1

                # Si l'état redevient sain (zéro), guéri
                if df.loc[idx, 'EtatMaladie'] == 0:
                    df.loc[idx, 'Maladie'] = ''
                    text += f"Un homme s'est rétabli de la {mal_nom}\n"
                    messagebox.showinfo("Info", f"Un homme s'est rétabli de la {mal_nom}")
        Vivant=len(df[df['EtatMaladie'] > -6])
        AncienV=len(df)
        Mor=AncienV-Vivant
        df = df[df['EtatMaladie'] > -6]
        if Mor>0:
            messagebox.showinfo("Info", f"Des hommes ont succombé à des maladies")
    df.to_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252", index=False)
    return text


# ----------------- LANCERS DE DÉS ---------------- #

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

# ----------------- AUTRES ---------------- #

def soins_equipage(_, __, equipage):
    """Soigne tout l'équipage à PVMax - 1."""
    df = pd.read_csv(EQUIPAGE_PATH+equipage, sep=";", decimal=",", encoding='cp1252')
    df['PV'] = df['PVMax'] - 1
    df.to_csv(EQUIPAGE_PATH+equipage, sep=";", decimal=",", encoding='cp1252')
    return df


def perte(degats, name):
    """Applique des pertes de PV. Supprime les morts."""
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    morts = 0
    for _ in range(degats):
        extract = df.sample()
        extract['PV'] -= 1
        idx = extract.index[0]
        df.loc[idx, 'PV'] = extract['PV'].values[0]
        if extract['PV'].values[0] < 1:
            df.drop(idx, inplace=True)
            morts += 1
    df.to_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252", index=False)
    return morts


def select_random(name, nb):
    """Sélectionne aléatoirement nb individus dans l'équipage."""
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    return df.sample(n=nb).to_string()


def preparation_repas_par_jour(name):
    """Calcule le nombre de repas préparés par les cuisiniers."""
    """On considère 8h de travail par jour avec un seuil de 5 repas par heure par succès par cuisinier"""
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    df = Equipage.HommesValides(df)
    repas = 0
    nb_repas_par_succes = 5
    for k in range(8):
        for type_ in ['Coq', 'Cuisinier']:
            for _, row in df[df['Type'] == type_].iterrows():
                repas += lancer_de(row['Cuisine'], 0)[0] * nb_repas_par_succes
    return repas


def ImpactFamine(name):
    """Calcule le nombre de repas préparés par les cuisiniers."""
    """On considère 8h de travail par jour avec un seuil de 5 repas par heure par succès par cuisinier"""
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    repas=preparation_repas_par_jour(name)
    if repas<len(df):
        Equipage.Attitude(name,-2*(1-repas/len(df)))

    for _ in range(len(df)-repas):
        # Check if TempDF still has members
        if len(df)<1:
           df  = pd.DataFrame()  # Reset TempDF if empty
           print(f"{name} a été décimé")
        break

        # Sample a single row
        Extract = df.sample()

        # Reduce PV and reflect back in TempDF
        new_pv = Extract['Famine'].iloc[0] - 1
        df.loc[Extract.index, 'Famine'] = new_pv
    df.to_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")

def test_maladie(nb_jours, endemique, name):
    """Teste la propagation de maladie dans un équipage."""
    text = evolution_maladie(nb_jours, name)
    df = pd.read_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252")
    df["Maladie"] = df["Maladie"].astype(str)
    maladies = pd.read_csv(BASE_PATH+"/Maladie.csv", sep=";", decimal=",", encoding="cp1252")
    maladies = maladies[maladies["Maladie"] != "Famine"]
    maladie = maladies.sample().iloc[0]
    chance = 140 if endemique else 600
    for k in df['Maladie'].dropna().unique():
        maladie=maladies[maladies['Maladie']==k].iloc[0]
        if(reconnaissance_malade_equipage(name) == 0 and maladie['Contamination']==1):
            chance=10
        elif maladie['Contamination']==0 :
            maladie = maladies.sample().iloc[0]
    for _ in range(nb_jours):
        for k in df.index:
            if random.randint(1, chance) == 1:
                if maladie['PopulationFragile'] == "Européens":
                    maladie['Virulence'] -= 2
                elif maladie['PopulationResistante'] == "Européens":
                    maladie['Virulence'] += 2

                if lancer_de(2, maladie['Virulence'])[0] < 2:
                    df.loc[k, 'Maladie'] = maladie['Maladie']
                    df.loc[k, 'EtatMaladie'] = maladie['EtatCrise']
                    df.loc[k, 'Cycle'] = maladie['Cycle']
                    print("Un homme a contracté la "+maladie['Maladie']+" \n")
                    text += "Un homme a contracté la "+maladie['Maladie']+" \n"
    df=df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.to_csv(os.path.join(EQUIPAGE_PATH, name), sep=";", decimal=",", encoding="cp1252", index=False)
    return text