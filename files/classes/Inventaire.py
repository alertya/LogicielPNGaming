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




class Inventaire:

    def __init__(self):
        self.Marchandises = {}
        self.nom="TestInventaire"

    def Ajouter(self, marchandise, quantite):
        if marchandise.Nom not in self.Marchandises:
            self.Marchandises[marchandise.Nom] = 0

        self.Marchandises[marchandise.Nom] += quantite

    def Supprimer(self, marchandise, quantite):
        nom = marchandise.Nom

        if nom not in self.Marchandises:
            return False

        if self.Marchandises[nom] < quantite:
            return False

        self.Marchandises[nom] -= quantite

        if self.Marchandises[nom] == 0:
            del self.Marchandises[nom]

        return True

    def Sauvegarder(self, Nom):

        donnees = []

        for nom, quantite in self.Marchandises.items():

            donnees.append({
                "Nom": nom,
                "Quantite": quantite
            })

        df = pd.DataFrame(donnees)

        df.to_csv(
            BASE_PATH+"/Marchandise/"+Nom+".csv",
            encoding="cp1252",
            decimal=",",
            sep=";",
            index=False
        )

    def Charger(self, Nom, marchandises):

            df = pd.read_csv(
                BASE_PATH+"/Marchandise/"+Nom+".csv",
                encoding="cp1252",
                decimal=",",
                sep=";"
            )

            self.Marchandises = {}

            for _, ligne in df.iterrows():

                nom = ligne["Nom"]
                quantite = int(ligne["Quantite"])

                if nom in marchandises:
                    self.Marchandises[nom] = quantite
    def Nommer(self,Nom):
        self.nom=Nom
        return self