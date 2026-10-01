# -*- coding: utf-8 -*-
"""
Gestion de la navigation maritime.

Responsabilités de Navigation :
    - calculer l'écart de route du navire 1 ;
    - détecter et résoudre les hauts-fonds ;
    - détecter et résoudre les tempêtes ;
    - calculer une poursuite entre deux navires ;
    - gérer les opérations d'escale directement liées à la navigation.

La classe Voyage orchestre la traversée.
La classe Navire représente les navires et leurs caractéristiques.
Navigation se concentre donc sur les événements et calculs nautiques.

Une couche de compatibilité conserve les anciennes fonctions de module
(Tempest(...), TestNavigation(...), etc.) afin de ne pas casser immédiatement
le reste du projet.
"""

from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd
from tkinter import messagebox

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
NB = 182
SUPERFICIE = 106460000 / 2
NB_DAYS_OF_CYCLONE = 59
NB_DAYS_OF_TEMPEST = 27
SURFACE = np.pi * 750 * 750
PROBA_TEMPETE_BASE = round(SUPERFICIE / SURFACE * NB / NB_DAYS_OF_CYCLONE)
ENCODAGE = "cp1252"
SEPARATEUR = ";"
DECIMAL = ","


@dataclass
class Navigation:
    """Résultat générique d'une opération de navigation."""

    texte: str = ""
    variation_distance: float = 0.0
    statut: str = "OK"
    donnees: dict[str, Any] = field(default_factory=dict)


class Navigation:
    """
    Modélise les règles de navigation d'un navire.

    ``Navigation`` n'est pas le navire lui-même : elle applique les règles
    nautiques à un navire existant. Un navire peut être fourni au constructeur
    ou passé aux méthodes via son nom de fichier.

    Parameters
    ----------
    navire1 : optional
        Navire courant. Peut être un nom de fichier CSV, un DataFrame, une
        Series ou un dictionnaire.
    afficher_messages : bool
        Affiche ou non les fenêtres Tkinter historiques.
    """

    def __init__(self, navire1: Any = None, afficher_messages: bool = True):
        self.navire1 = navire1
        self.navire2: Any = None
        self.afficher_messages = afficher_messages
        self.jour = 1
        self.zone = None
        self.evenements: list[Navigation] = []

    # ------------------------------------------------------------------
    # Etat et accès aux données
    # ------------------------------------------------------------------

    @staticmethod
    def _premiere_ligne(data: Any) -> pd.Series:
        if isinstance(data, pd.DataFrame):
            if data.empty:
                raise ValueError("Le DataFrame est vide.")
            return data.iloc[0]
        if isinstance(data, pd.Series):
            return data
        if isinstance(data, dict):
            return pd.Series(data)
        raise TypeError(f"Type de donnée non supporté : {type(data)!r}")

    @staticmethod
    def _charger_navire(navire: Any) -> pd.DataFrame:
        if isinstance(navire, pd.DataFrame):
            return navire.copy()
        if isinstance(navire, pd.Series):
            return navire.to_frame().T
        if isinstance(navire, dict):
            return pd.DataFrame([navire])
        if isinstance(navire, str):
            nom = os.path.basename(navire)
            candidats = [
                os.path.join(NAVIRE_PATH, nom),
                os.path.join(NAVIRE_PATH, f"{nom}.csv") if not nom.lower().endswith(".csv") else None,
            ]
            for chemin in candidats:
                if chemin and os.path.exists(chemin):
                    return pd.read_csv(
                        chemin,
                        sep=SEPARATEUR,
                        decimal=DECIMAL,
                        encoding=ENCODAGE,
                    )
            raise FileNotFoundError(
                f"Navire introuvable : {navire!r} dans {NAVIRE_PATH!r}."
            )
        raise TypeError("Le navire doit être un nom de fichier, DataFrame, Series ou dict.")

    def _nom_navire(self, navire: Any = None) -> str:
        navire = self.navire1 if navire is None else navire
        if isinstance(navire, str):
            return os.path.basename(navire)
        try:
            row = self._premiere_ligne(navire)
            return str(row.get("Name", row.get("Nom", "Navire1")))
        except Exception:
            return "Navire1.csv"

    def _enregistrer(self, resultat: Navigation) -> Navigation:
        self.evenements.append(resultat)
        return resultat

    def _message(self, titre: str, texte: str) -> None:
        if self.afficher_messages:
            try:
                messagebox.showinfo(titre, texte)
            except Exception:
                # Le moteur peut être exécuté sans interface graphique.
                pass

    @staticmethod
    def _nom_equipage(navire_df: pd.DataFrame) -> Optional[str]:
        if "EquipageNom" not in navire_df.columns or navire_df.empty:
            return None
        valeur = navire_df.iloc[0]["EquipageNom"]
        if pd.isna(valeur):
            return None
        return str(valeur)

    def _charger_equipage(self, navire_df: pd.DataFrame) -> Optional[pd.DataFrame]:
        nom = self._nom_equipage(navire_df)
        if not nom:
            return None
        chemin = os.path.join(EQUIPAGE_PATH, nom)
        if not os.path.exists(chemin):
            return None
        return pd.read_csv(
            chemin,
            sep=SEPARATEUR,
            decimal=DECIMAL,
            encoding=ENCODAGE,
        )

    def _sauver_navire(self, nom_navire: str, navire_df: pd.DataFrame) -> None:
        path = os.path.join(NAVIRE_PATH, os.path.basename(nom_navire))
        navire_df.to_csv(path, sep=SEPARATEUR, decimal=DECIMAL, encoding=ENCODAGE, index=False)

    def _sauver_equipage(self, navire_df: pd.DataFrame, equipage: Optional[pd.DataFrame]) -> None:
        if equipage is None:
            return
        nom = self._nom_equipage(navire_df)
        if not nom:
            return
        path = os.path.join(EQUIPAGE_PATH, nom)
        equipage.to_csv(path, sep=SEPARATEUR, decimal=DECIMAL, encoding=ENCODAGE, index=False)

    # ------------------------------------------------------------------
    # Tests élémentaires
    # ------------------------------------------------------------------

    @staticmethod
    def lancer_de(valeur: Any, bonus: int = 0) -> Any:
        """Utilise le système de test central du projet."""
        return utils.Test(valeur, bonus)

    @staticmethod
    def _resultat_test(resultat: Any) -> int:
        if isinstance(resultat, (tuple, list)):
            return int(resultat[0])
        return int(resultat)

    # ------------------------------------------------------------------
    # Tempêtes / avaries
    # ------------------------------------------------------------------

    def Tempest(self, Name1: Any = None, Proba: int = PROBA_TEMPETE_BASE, NbJour: Optional[int] = None):
        """
        Teste la survenue d'une tempête pour un jour donné.

        Retourne ``(texte, variation_distance)`` pour rester compatible avec
        ``Voyage``.
        """
        nom_navire = self._nom_navire(Name1)
        navire_df = self._charger_navire(Name1 if Name1 is not None else self.navire1)
        jour = self.jour if NbJour is None else NbJour
        self.jour = jour

        texte = ""
        variation_distance = 0.0

        try:
            proba = max(1, int(Proba))
        except (TypeError, ValueError):
            proba = 1

        if random.randint(0, proba) <= 1:
            texte += f"Affrontement d'une tempête au bout de {jour} jours\n"
            manoeuvre = navire_df.iloc[0].get("Manoeuvre", 0)
            reussite = self._resultat_test(self.lancer_de(manoeuvre))

            if reussite > 1:
                avarie = -1
            else:
                avarie = 0 if reussite == 1 else (1 if reussite == 0 else 2)

            vitesse = float(navire_df.iloc[0].get("Vitesse moyenne", 0) or 0)
            resultat_avarie = self.AvarieResultat(avarie, nom_navire, vitesse)
            texte += resultat_avarie[0]
            variation_distance += float(resultat_avarie[1])

            self._message("Info", texte)

        self._sauver_navire(nom_navire, navire_df)
        equipage = self._charger_equipage(navire_df)
        self._sauver_equipage(navire_df, equipage)

        return texte, variation_distance

    def AvarieResultat(self, Avarie: int, Name1: Any, VitesseMoyenne: float):
        """Résout les conséquences d'une tempête."""
        nom_navire = self._nom_navire(Name1)
        navire_df = self._charger_navire(Name1 if Name1 is not None else self.navire1)
        equipage = self._charger_equipage(navire_df)

        texte = ""
        degat = 0
        distance = 0.0
        de = random.randint(1, 6)

        if equipage is None:
            # Sans fichier d'équipage, on applique seulement les dégâts coque/voile.
            equipage = pd.DataFrame()

        nom_equipage = self._nom_equipage(navire_df)

        def action_equipage(action: str, groupe: str = "Equipage", bonus: int = 0):
            if not nom_equipage:
                return 0, 0
            try:
                return FonctionEquipage.ActionEquipage(
                    action, groupe, bonus, nom_equipage
                )
            except Exception:
                return 0, 0

        if Avarie == 0:
            if de == 1 and nom_equipage:
                try:
                    FonctionEquipage.Perte(1, nom_equipage)
                except Exception:
                    pass

            elif de == 2:
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = self.PerteNavire(nom_navire, structure / 10 * 2, "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            elif de == 3 and nom_equipage:
                try:
                    FonctionEquipage.Tues(1, nom_equipage)
                    FonctionEquipage.Perte(3, nom_equipage)
                except Exception:
                    pass
                texte += "VOUS AVEZ PERDU UN MEMBRE D'EQUIPAGE DURANT LA TEMPETE\n"

            elif de == 4:
                _, moyen = action_equipage("Charpenterie", "Charpentier", 0)
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = self.PerteNavire(nom_navire, structure / 10 * 3 - moyen, "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            else:
                _, moyen = action_equipage("VirementBord", "Equipage", -2)
                if moyen == 0:
                    distance += VitesseMoyenne
                elif moyen < 0:
                    _, moyen_voile = action_equipage("ReduireVoilure")
                    if moyen_voile < 2:
                        _, moyen_hache = action_equipage("Hache")
                        if moyen_hache < 2:
                            _, moyen_mat = action_equipage("Hache")
                            _, construction = action_equipage("ConstructionNavire")
                            distance += VitesseMoyenne * (7 - construction)
                            if moyen_mat < 2:
                                voile = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                                coque = float(navire_df.iloc[0].get("StructureCoque", 0) or 0)
                                _, tmp = self.PerteNavire(nom_navire, voile, "Voile")
                                _, tmp2 = self.PerteNavire(nom_navire, coque, "Coque")
                                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT ET DE LA COQUE\n" + tmp + tmp2

        elif Avarie == 1:
            if de == 1:
                if nom_equipage:
                    try:
                        FonctionEquipage.Tues(3, nom_equipage)
                        FonctionEquipage.Perte(20, nom_equipage)
                    except Exception:
                        pass
                texte += "VOUS AVEZ PERDU TROIS MEMBRES D'EQUIPAGE DURANT LA TEMPETE ET BLESSE D'AUTRES\n"

            elif de == 2:
                calibre = float(navire_df.iloc[0].get("Calibre", 1) or 1)
                # Protection contre la boucle infinie de l'ancien code.
                iterations = 0
                moyen = 0
                while moyen < calibre / 6 and iterations < 20:
                    _, gain = action_equipage("EmbarquerMarchandise")
                    moyen += gain
                    iterations += 1
                structure = float(navire_df.iloc[0].get("StructureCoque", 0) or 0)
                _, tmp = self.PerteNavire(nom_navire, structure / 10 * 2, "Coque")
                if nom_equipage:
                    try:
                        FonctionEquipage.Perte(1, nom_equipage)
                    except Exception:
                        pass
                texte += "VOUS AVEZ BLESSE UN MEMBRE D'EQUIPAGE DURANT LA TEMPETE ET UNE PARTIE DE LA COQUE\n" + tmp

            elif de == 3:
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = self.PerteNavire(nom_navire, structure / 10 * 4, "Voile")
                if nom_equipage:
                    try:
                        FonctionEquipage.Perte(structure / 10 * 4, nom_equipage)
                    except Exception:
                        pass
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            elif de == 4:
                _, moyen = action_equipage("VirementBord")
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = self.PerteNavire(nom_navire, structure / 10 * 4 * (4 - moyen), "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            else:
                _, moyen = action_equipage("ReparationsFortune")
                degat, tmp = self.PerteNavire(nom_navire, 5 - moyen, "Coque")
                texte += "VOUS AVEZ PERDU UNE PARTIE DE LA COQUE\n" + tmp

        elif Avarie == 2:
            _, moyen = action_equipage("ReparationsFortune")
            degat, tmp = self.PerteNavire(nom_navire, 5 - moyen, "Coque")
            texte += "VOUS AVEZ PERDU UNE PARTIE DE LA COQUE\n" + tmp

            if moyen == 0:
                distance += VitesseMoyenne
            elif moyen < 0:
                _, moyen_voile = action_equipage("ReduireVoilure")
                if moyen_voile < 2:
                    _, moyen_hache = action_equipage("Hache")
                    if moyen_hache < 2:
                        _, construction = action_equipage("ConstructionNavire")
                        distance += VitesseMoyenne * (7 - construction)

        # On recharge les données pour vérifier l'état final.
        navire_final = self._charger_navire(nom_navire)
        equipage_final = self._charger_equipage(navire_final)
        self._sauver_navire(nom_navire, navire_final)
        self._sauver_equipage(navire_final, equipage_final)

        if "StructureCoque" in navire_final.columns and navire_final.iloc[0]["StructureCoque"] <= 0:
            distance = -99999999999999999999999
            texte += "LE NAVIRE A COULE. FIN DU VOYAGE.\n"

        return texte, distance

    def PerteNavire(self, Navire: Any, Pertes: float, TypeMunition: str):
        """Applique des pertes structurelles ou d'équipage au navire."""
        nom_navire = self._nom_navire(Navire)
        df = self._charger_navire(Navire if not isinstance(Navire, str) or os.path.exists(Navire) else nom_navire)
        pertes = max(0, int(Pertes))
        texte = "\n"

        if TypeMunition == "Voile":
            if "StructureVoile" in df.columns:
                avant = float(df.at[0, "StructureVoile"])
                df.at[0, "StructureVoile"] = max(0, avant - pertes)
            texte += f"{nom_navire} a perdu {pertes} points de structure en voile.\n"

        elif TypeMunition == "Coque":
            if "StructureCoque" in df.columns:
                avant = float(df.at[0, "StructureCoque"])
                df.at[0, "StructureCoque"] = max(0, avant - pertes)
            texte += f"{nom_navire} a perdu {pertes} points de structure en coque.\n"

        elif TypeMunition == "Mitraille":
            equipage_nom = self._nom_equipage(df)
            if equipage_nom:
                try:
                    FonctionEquipage.Tues(pertes, equipage_nom)
                except Exception:
                    pass
            if "Equipage" in df.columns:
                df.at[0, "Equipage"] = max(0, float(df.at[0, "Equipage"]) - pertes)
            texte += f"{nom_navire} a perdu {pertes} hommes.\n"

        else:
            texte += f"Type de munition inconnu : {TypeMunition}.\n"

        if "StructureCoque" in df.columns and df.at[0, "StructureCoque"] <= 0:
            texte += f"{nom_navire} A COULE, VOUS VOUS ETES ECHOUE.\n"
            pertes = 999

        if "StructureVoile" in df.columns and df.at[0, "StructureVoile"] <= 0:
            texte += f"{nom_navire} a dématé.\n"

        self._sauver_navire(nom_navire, df)
        equipage = self._charger_equipage(df)
        self._sauver_equipage(df, equipage)

        return pertes, texte

    # ------------------------------------------------------------------
    # Hauts-fonds / hydrographie
    # ------------------------------------------------------------------

    def HautsFonds(self, Name1: Any, Recif: bool):
        """Résout le passage sur un haut-fond ou un récif."""
        nom_navire = self._nom_navire(Name1)
        navire = self._charger_navire(Name1)
        manoeuvre = navire.iloc[0].get("Manoeuvre", 0)
        reussite = self._resultat_test(self.lancer_de(manoeuvre))

        bonus = 5 if Recif else 3
        degat = reussite
        try:
            degat += int(utils.ConvertSuccessToAction(reussite)[0])
        except Exception:
            pass
        degat += bonus

        _, tmp = self.PerteNavire(nom_navire, degat, "Coque")
        texte = (
            tmp
            + f"LE NAVIRE A TOUCHE UN HAUT FOND ET A PERDU {degat} AU NIVEAU DE LA COQUE\n"
        )
        self._message("Info", texte)
        return texte

    def TestNavigation(self, Name: Any = None):
        """Calcule l'écart quotidien de navigation."""
        nom_navire = self._nom_navire(Name)
        navire = self._charger_navire(Name if Name is not None else self.navire1)
        equipage = self._charger_equipage(navire)

        if equipage is None:
            return 0.0

        pilotes = equipage[equipage["Type"] == "Pilote"] if "Type" in equipage.columns else pd.DataFrame()
        if pilotes.empty:
            detection = -1
        else:
            detection = -9999
            essais = 0
            while detection == -9999 and essais < 100:
                for _, row in pilotes.iterrows():
                    detection = max(
                        detection,
                        self._resultat_test(utils.Test(row.get("Navigation", 0), 2)),
                    )
                    if detection == 1:
                        detection = -9999
                        break
                essais += 1
            if detection == -9999:
                detection = 0

        if detection > 0:
            try:
                theta = utils.MinGauss(7.5, 1.5, detection)
            except Exception:
                theta = 0.0
        else:
            try:
                theta = utils.MaxGauss(7.5, 1.5, abs(detection) + 1)
            except Exception:
                theta = 0.0

        print(f"FIN DE CALCUL DE NAVIGATION ({nom_navire})\n")
        return float(theta)

    def TestHydrographie(self, Name: Any = None, Zone: str = ""):
        """Teste la présence d'un pilote et détermine le risque de haut-fond."""
        nom_navire = self._nom_navire(Name)
        navire = self._charger_navire(Name if Name is not None else self.navire1)
        equipage = self._charger_equipage(navire)
        texte = ""

        detection: Optional[int] = None
        recif = 1

        if "Mer" in Zone:
            detection = 2
        elif any(x in Zone.lower() for x in ["route", "large"]):
            recif = 0

        if detection is None:
            pilotes = (
                equipage[equipage["Type"] == "Pilote"]
                if equipage is not None and "Type" in equipage.columns
                else pd.DataFrame()
            )

            if pilotes.empty:
                detection = -1
                texte += "ATTENTION, vous n'avez pas de pilote à bord, votre navire risque fort de sombrer\n"
                self._message("Info", texte)
            else:
                detection = -9999
                essais = 0
                while detection == -9999 and essais < 100:
                    for _, row in pilotes.iterrows():
                        detection = max(
                            detection,
                            self._resultat_test(utils.Test(row.get("Navigation", 0), 2)),
                        )
                        if detection == 1:
                            detection = -9999
                            recif = 1 if any(x in Zone.lower() for x in ["côte", "mouillage", "port"]) else 0
                            break
                    essais += 1
                if detection == -9999:
                    detection = 0

        if detection < 1:
            texte += self.HautsFonds(nom_navire, bool(recif))

        print(texte)
        print("FIN DE CALCUL D'HYDROGRAPHIE\n")
        return texte

    # ------------------------------------------------------------------
    # Poursuite
    # ------------------------------------------------------------------

    def CoursePoursuite(
        self,
        HeureAvantNuit: int,
        Distance: float,
        AllurePoursuivant: str,
        AllurePoursuive: str,
        NavirePoursuivant_file: str,
        NavirePoursuive_file: str,
        VoilurePoursuivant: str,
        VoilurePoursuive: str,
    ):
        """Simule une poursuite entre deux navires."""
        poursuivant = self._charger_navire(NavirePoursuivant_file)
        poursuivi = self._charger_navire(NavirePoursuive_file)
        ep_poursuivant = self._charger_equipage(poursuivant)
        ep_poursuivi = self._charger_equipage(poursuivi)

        def vitesse(navire: pd.DataFrame, allure: str, voilure: str) -> float:
            valeur = float(navire.iloc[0].get(allure, 0) or 0)
            if voilure == "SousToile":
                valeur -= 1
            elif voilure == "SurToile":
                valeur += 1
            return valeur

        vp = vitesse(poursuivant, AllurePoursuivant, VoilurePoursuivant)
        vf = vitesse(poursuivi, AllurePoursuive, VoilurePoursuive)

        def bonus(equipage: Optional[pd.DataFrame], navire: pd.DataFrame) -> int:
            nom = self._nom_equipage(navire)
            if not nom:
                return 0
            try:
                valeur = FonctionEquipage.ActionEquipage("Poursuite", "Equipage", 0, nom)[1]
                return int(utils.ConvertFloatToInt(valeur))
            except Exception:
                return 0

        bp = bonus(ep_poursuivant, poursuivant)
        bf = bonus(ep_poursuivi, poursuivi)

        distance = float(Distance)
        compteur = 0
        while distance > 0 and compteur < 100:
            tp = self._resultat_test(utils.Test(poursuivant.iloc[0].get("Manoeuvre", 0), bp))
            tf = self._resultat_test(utils.Test(poursuivi.iloc[0].get("Manoeuvre", 0), bf))
            compteur += 1
            distance -= (vp + tp) - (vf + tf)

            if compteur > int(HeureAvantNuit) * 2:
                return (
                    f"Le navire n'a pas réussi la poursuite avant la nuit. Distance restante : {distance:.2f} milles.",
                    distance,
                )
            if distance <= 0.3:
                return (
                    f"Le navire a rattrapé sa cible en {compteur / 2:.1f} heures, il peut aborder ou canonner.",
                    0,
                )

        return "Le navire poursuivi a réussi sa fuite.", distance

    # ------------------------------------------------------------------
    # Ecart quotidien
    # ------------------------------------------------------------------

    def CalculEcartJourneeNavigation(self, VitesseJour: float, Name: str):
        """Calcule les composantes longitudinales et latérales de l'écart."""
        ecart_moyen = min(0.05 * float(VitesseJour), 15)
        equipage = pd.read_csv(
            os.path.join(EQUIPAGE_PATH, Name),
            sep=SEPARATEUR,
            decimal=DECIMAL,
            encoding=ENCODAGE,
        )
        pilotes = equipage[equipage["Type"] == "Pilote"] if "Type" in equipage.columns else pd.DataFrame()

        if pilotes.empty:
            detection = -1
        else:
            detection = -9999
            essais = 0
            while detection == -9999 and essais < 100:
                for _, row in pilotes.iterrows():
                    detection = max(
                        detection,
                        self._resultat_test(utils.Test(row.get("Navigation", 0), 2)),
                    )
                essais += 1

        if detection < 0:
            drift = utils.MaxAbsGauss(0, ecart_moyen, 2)
        elif detection > 0:
            drift = utils.MinAbsGauss(0, ecart_moyen, detection + 1)
        else:
            drift = utils.MinGauss(0, ecart_moyen, 1)

        drift = float(drift)
        argument = max(0.0, float(VitesseJour) ** 2 - drift ** 2)
        distx = math.sqrt(argument)
        return distx, drift

    # ------------------------------------------------------------------
    # Escale
    # ------------------------------------------------------------------

    def Escale(
        self,
        Zone: str,
        TaillePort: Any,
        NavireName: str,
        Recrute: bool,
        Commerce: bool,
        Reparation: bool,
    ):
        """Gère les actions nautiques réalisées pendant une escale."""
        nb_jours = random.randint(5, 10)
        marchandises = CalculMarchandise.CoursMarchandise(nb_jours, Zone, TaillePort)
        navire = self._charger_navire(NavireName)
        equipage = self._charger_equipage(navire)
        cout = 0.0
        tmp = 0
        texte = ""

        if Recrute and equipage is not None:
            try:
                maitre = FonctionEquipage.GeneratePJDataframe(1, "MaitreEquipage", "Test", 0, 1, 0).iloc[0]
                homme_manquant = int(navire.iloc[0].get("EquipMax", 0)) - len(equipage)
                if homme_manquant > 0:
                    FonctionEquipage.Recrute(
                        homme_manquant,
                        "Matelot",
                        os.path.basename(NavireName).removesuffix(".csv"),
                        0,
                    )
                    tmp = utils.TestValeurNonNumerique(maitre["MeneurHommes"], 0)[1]
                nb_jours = max(nb_jours, tmp)
            except Exception as exc:
                texte += f"Recrutement impossible : {exc}\n"

        if Commerce:
            try:
                texte, capacite_achat, capacite_vente = CalculMarchandise.TrouverMarchand(Zone)
            except Exception as exc:
                texte += f"Commerce indisponible : {exc}\n"

        if Reparation:
            try:
                charpentier = FonctionEquipage.GeneratePJDataframe(
                    1, "Charpentier", "Test", 0, 1, 0
                ).iloc[0]
                degats_coque = int(navire.iloc[0].get("StructureCoqueMax", 0) - navire.iloc[0].get("StructureCoque", 0))
                degats_voile = int(navire.iloc[0].get("StructureVoileMax", 0) - navire.iloc[0].get("StructureVoile", 0))

                for _ in range(max(0, degats_coque)):
                    navire.iloc[0, navire.columns.get_loc("StructureCoque")] += 1
                    cout += 200
                    tmp += utils.TestValeurNonNumerique(charpentier["Charpenterie"], 0)[0]
                for _ in range(max(0, degats_voile)):
                    navire.iloc[0, navire.columns.get_loc("StructureVoile")] += 1
                    cout += 200
                    tmp += utils.TestValeurNonNumerique(charpentier["Charpenterie"], 0)[0]

                nb_jours = max(nb_jours, tmp)
                self._sauver_navire(os.path.basename(NavireName), navire)
            except Exception as exc:
                texte += f"Réparation impossible : {exc}\n"

        return cout, nb_jours, texte


# ===========================================================================
# COMPATIBILITE AVEC L'ANCIEN CODE PROCEDURAL
# ===========================================================================

_navigation_par_defaut = Navigation()


def Tempest(Name1, Proba, NbJour):
    return _navigation_par_defaut.Tempest(Name1, Proba, NbJour)


def AvarieResultat(Avarie, Name1, VitesseMoyenne):
    return _navigation_par_defaut.AvarieResultat(Avarie, Name1, VitesseMoyenne)


def HautsFonds(Name1, Recif):
    return _navigation_par_defaut.HautsFonds(Name1, Recif)


def TestNavigation(Name):
    return _navigation_par_defaut.TestNavigation(Name)


def TestHydrographie(Name, Zone):
    return _navigation_par_defaut.TestHydrographie(Name, Zone)


def CoursePoursuite(
    HeureAvantNuit,
    Distance,
    AllurePoursuivant,
    AllurePoursuive,
    NavirePoursuivant_file,
    NavirePoursuive_file,
    VoilurePoursuivant,
    VoilurePoursuive,
):
    return _navigation_par_defaut.CoursePoursuite(
        HeureAvantNuit,
        Distance,
        AllurePoursuivant,
        AllurePoursuive,
        NavirePoursuivant_file,
        NavirePoursuive_file,
        VoilurePoursuivant,
        VoilurePoursuive,
    )


def CalculEcartJourneeNavigation(VitesseJour, Name):
    return _navigation_par_defaut.CalculEcartJourneeNavigation(VitesseJour, Name)


def Escale(Zone, TaillePort, NavireName, Recrute, Commerce, Reparation):
    return _navigation_par_defaut.Escale(
        Zone,
        TaillePort,
        NavireName,
        Recrute,
        Commerce,
        Reparation,
    )
