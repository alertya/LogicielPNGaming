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
from classes.Navire import Navire
from classes.Equipage import Equipage
import numpy as np
import pandas as pd
from tkinter import messagebox
import utils
import config
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
                os.path.join(config.config.NAVIRE_PATH, nom),
                os.path.join(config.config.NAVIRE_PATH, f"{nom}.csv") if not nom.lower().endswith(".csv") else None,
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
                f"Navire introuvable : {navire!r} dans {config.NAVIRE_PATH!r}."
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
        chemin = os.path.join(config.config.EQUIPAGE_PATH, nom)
        if not os.path.exists(chemin):
            return None
        return pd.read_csv(
            chemin,
            sep=SEPARATEUR,
            decimal=DECIMAL,
            encoding=ENCODAGE,
        )

    def _sauver_navire(self, nom_navire: str, navire_df: pd.DataFrame) -> None:
        path = os.path.join(config.NAVIRE_PATH, os.path.basename(nom_navire))
        navire_df.to_csv(path, sep=SEPARATEUR, decimal=DECIMAL, encoding=ENCODAGE, index=False)

    def _sauver_equipage(self, navire_df: pd.DataFrame, equipage: Optional[pd.DataFrame]) -> None:
        if equipage is None:
            return
        nom = self._nom_equipage(navire_df)
        if not nom:
            return
        path = os.path.join(config.EQUIPAGE_PATH, nom)
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

    def Tempest(self, nom_navire):
        navire = Navire.charger_depuis_csv(nom_navire)
        equipage = Equipage.charger_depuis_csv(navire.EquipageNom)

        texte = ""
        variation_distance = 0

        # 1 chance sur 40
        if random.randint(1, 40) != 1:
            return texte, variation_distance

        texte += "⛈️ Une tempête éclate !\n"

        # Test des hydrographes
        meilleur_test = -99

        for membre in equipage.Membres:
            if "Hydrographe" not in membre.Traits:
                continue

            test = utils.Test(membre.Hydrographie, 0)
            meilleur_test = max(meilleur_test, test)

        # Aucun hydrographe
        if meilleur_test == -99:
            meilleur_test = -1

        texte += f"Meilleur test Hydrographie : {meilleur_test}\n"

        if meilleur_test < 2:

            if meilleur_test > 0:
                avarie = 0
            elif meilleur_test == 0:
                avarie = 1
            else:
                avarie = 2

            txt, variation_distance = self.AvarieResultat(
                avarie,
                nom_navire,
                navire.VitesseMoyenne,navire.EquipageNom
            )
            texte += txt
        else:
            texte += "Les hydrographes anticipent la tempête et le navire l'évite.\n"

        navire.sauvegarder()
        equipage.Save(navire.EquipageNom)

        return texte

    def AvarieResultat(
            self,
            avarie: int,
            vitesse_moyenne: float,
            nom_navire: str,
            nom_equipage: str):
        """
        Résout les conséquences d'une tempête.
        """

        navire = Navire.charger_depuis_csv(nom_navire)
        equipage = Equipage.charger_depuis_csv(nom_equipage)

        texte = ""
        distance = 0
        de = random.randint(1, 6)

        if avarie == 0:

            if de == 1:
                equipage.Perte(1)

            elif de == 2:
                perte = navire.StructureVoile * 0.2
                _, tmp = navire.PerteNavire(nom_navire, perte, "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n"
                texte += tmp

            elif de == 3:
                equipage.Tues(1)
                equipage.Perte(3)
                texte += "VOUS AVEZ PERDU UN MEMBRE D'EQUIPAGE DURANT LA TEMPETE\n"

            elif de == 4:
                _, moyen = equipage.ActionEquipage("Charpenterie", "Charpentier")
                perte = max(0, navire.StructureVoile * 0.3 - moyen)
                _, tmp = navire.PerteNavire(nom_navire, perte, "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n"
                texte += tmp

            else:

                _, moyen = equipage.ActionEquipage("VirementBord", "Equipage", -2)

                if moyen == 0:
                    distance += vitesse_moyenne

                elif moyen < 0:

                    _, voilure = equipage.ActionEquipage("ReduireVoilure")

                    if voilure < 2:

                        _, hache = equipage.ActionEquipage("Hache")

                        if hache < 2:

                            _, mat = equipage.ActionEquipage("Hache")
                            _, construction = equipage.ActionEquipage("ConstructionNavire")

                            distance += vitesse_moyenne * (7 - construction)

                            if mat < 2:
                                _, tmp1 = navire.PerteNavire(
                                    nom_navire,
                                    navire.StructureVoile,
                                    "Voile"
                                )

                                _, tmp2 = navire.PerteNavire(
                                    nom_navire,
                                    navire.StructureCoque,
                                    "Coque"
                                )

                                texte += (
                                        "VOUS AVEZ PERDU UNE PARTIE DU MAT ET DE LA COQUE\n"
                                        + tmp1 + tmp2
                                )

        elif avarie == 1:

            if de == 1:

                equipage.Tues(3)
                equipage.Perte(20)

                texte += (
                    "VOUS AVEZ PERDU TROIS MEMBRES D'EQUIPAGE "
                    "DURANT LA TEMPETE ET BLESSE D'AUTRES\n"
                )

            elif de == 2:

                moyen = 0
                essais = 0

                while moyen < navire.Calibre / 6 and essais < 20:
                    _, gain = equipage.ActionEquipage("EmbarquerMarchandise")
                    moyen += gain
                    essais += 1

                _, tmp = navire.PerteNavire(
                    nom_navire,
                    navire.StructureCoque * 0.2,
                    "Coque"
                )

                equipage.Perte(1)

                texte += (
                    "VOUS AVEZ BLESSE UN MEMBRE D'EQUIPAGE "
                    "ET ENDOMMAGE LA COQUE\n"
                )
                texte += tmp

            elif de == 3:

                _, tmp = navire.PerteNavire(
                    nom_navire,
                    navire.StructureVoile * 0.4,
                    "Voile"
                )

                equipage.Perte(int(navire.StructureVoile * 0.4))

                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n"
                texte += tmp

            elif de == 4:

                _, moyen = equipage.ActionEquipage("VirementBord")

                perte = max(0, navire.StructureVoile * 0.4 * (4 - moyen))

                _, tmp = navire.PerteNavire(
                    nom_navire,
                    perte,
                    "Voile"
                )

                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n"
                texte += tmp

            else:

                _, moyen = equipage.ActionEquipage("ReparationsFortune")

                _, tmp = navire.PerteNavire(
                    nom_navire,
                    max(0, 5 - moyen),
                    "Coque"
                )

                texte += "VOUS AVEZ PERDU UNE PARTIE DE LA COQUE\n"
                texte += tmp

        elif avarie == 2:

            _, moyen = equipage.ActionEquipage("ReparationsFortune")

            _, tmp = navire.PerteNavire(
                nom_navire,
                max(0, 5 - moyen),
                "Coque"
            )

            texte += "VOUS AVEZ PERDU UNE PARTIE DE LA COQUE\n"
            texte += tmp

            if moyen == 0:
                distance += vitesse_moyenne

            elif moyen < 0:

                _, voilure = equipage.ActionEquipage("ReduireVoilure")

                if voilure < 2:

                    _, hache = equipage.ActionEquipage("Hache")

                    if hache < 2:
                        _, construction = equipage.ActionEquipage("ConstructionNavire")

                        distance += vitesse_moyenne * (7 - construction)

        # Recharge l'état du navire après les pertes
        navire = Navire.charger_depuis_csv(nom_navire)

        if navire.StructureCoque <= 0:
            texte += "LE NAVIRE A COULE. FIN DU VOYAGE.\n"
            distance = -999999999999999999

        navire.sauvegarder()
        equipage.sauvegarder()

        return texte, distance

        def action_equipage(action: str, groupe: str = "Equipage", bonus: int = 0):
            if not nom_equipage:
                return 0, 0
            try:
                return equipage.ActionEquipage(
                    action, groupe, bonus, nom_equipage
                )
            except Exception:
                return 0, 0

        if Avarie == 0:
            if de == 1 and nom_equipage:
                try:
                    equipage.Perte(1, nom_equipage)
                except Exception:
                    pass

            elif de == 2:
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = navire.PerteNavire(nom_navire, structure / 10 * 2, "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            elif de == 3 and nom_equipage:
                try:
                    equipage.Tues(1, nom_equipage)
                    equipage.Perte(3, nom_equipage)
                except Exception:
                    pass
                texte += "VOUS AVEZ PERDU UN MEMBRE D'EQUIPAGE DURANT LA TEMPETE\n"

            elif de == 4:
                _, moyen = action_equipage("Charpenterie", "Charpentier", 0)
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = navire.PerteNavire(nom_navire, structure / 10 * 3 - moyen, "Voile")
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
                                _, tmp = navire.PerteNavire(nom_navire, voile, "Voile")
                                _, tmp2 = navire.PerteNavire(nom_navire, coque, "Coque")
                                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT ET DE LA COQUE\n" + tmp + tmp2

        elif Avarie == 1:
            if de == 1:
                if nom_equipage:
                    try:
                        equipage.Tues(3, nom_equipage)
                        equipage.Perte(20, nom_equipage)
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
                _, tmp = navire.PerteNavire(nom_navire, structure / 10 * 2, "Coque")
                if nom_equipage:
                    try:
                        equipage.Perte(1, nom_equipage)
                    except Exception:
                        pass
                texte += "VOUS AVEZ BLESSE UN MEMBRE D'EQUIPAGE DURANT LA TEMPETE ET UNE PARTIE DE LA COQUE\n" + tmp

            elif de == 3:
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = navire.PerteNavire(nom_navire, structure / 10 * 4, "Voile")
                if nom_equipage:
                    try:
                        equipage.Perte(structure / 10 * 4, nom_equipage)
                    except Exception:
                        pass
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            elif de == 4:
                _, moyen = action_equipage("VirementBord")
                structure = float(navire_df.iloc[0].get("StructureVoile", 0) or 0)
                degat, tmp = navire.PerteNavire(nom_navire, structure / 10 * 4 * (4 - moyen), "Voile")
                texte += "VOUS AVEZ PERDU UNE PARTIE DU MAT\n" + tmp

            else:
                _, moyen = action_equipage("ReparationsFortune")
                degat, tmp = navire.PerteNavire(nom_navire, 5 - moyen, "Coque")
                texte += "VOUS AVEZ PERDU UNE PARTIE DE LA COQUE\n" + tmp

        elif Avarie == 2:
            _, moyen = action_equipage("ReparationsFortune")
            degat, tmp = navire.PerteNavire(nom_navire, 5 - moyen, "Coque")
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
        navire.sauvegarder()
        equipage.Save(equipage.Name)

        if "StructureCoque" in navire_final.columns and navire_final.iloc[0]["StructureCoque"] <= 0:
            distance = -99999999999999999999999
            texte += "LE NAVIRE A COULE. FIN DU VOYAGE.\n"

        return texte, distance


    # ------------------------------------------------------------------
    # Hauts-fonds / hydrographie
    # ------------------------------------------------------------------

    @staticmethod
    def HautsFonds(nom_navire, zone):
        navire = Navire.charger_depuis_csv(nom_navire)
        equipage = Equipage.charger_depuis_csv(navire.EquipageNom)

        texte = ""

        if zone.lower() in ("port", "près des côtes", "côte"):

            meilleur_test = -999

            # Tous les pilotes tentent le test
            for marin in equipage.Membres:
                if "Pilote" not in marin.Traits:
                    continue

                resultat = utils.Test(marin.Hydrographie, 0)[0]
                meilleur_test = max(meilleur_test, resultat)

            # Aucun pilote trouvé
            if meilleur_test == -999:
                meilleur_test = -1

            # Échec : haut-fond
            if meilleur_test < 2:
                perte = random.randint(1, 4)
                navire.StructureCoque = max(0, navire.StructureCoque - perte)
                texte += f"Le navire heurte un haut-fond (-{perte} coque).\n"

            else:
                texte += "Le pilote évite les hauts-fonds.\n"

        navire.sauvegarder()
        equipage.Save(equipage.Name)

        return texte

    def TestNavigation(self, nom_navire):
        """
        Retourne un modificateur de distance en %.
        100 = vitesse normale
        120 = +20%
        80 = -20%
        """
        navire = Navire.charger_depuis_csv(nom_navire)
        equipage = Equipage.charger_depuis_csv(navire.EquipageNom)

        meilleur_test = -999

        # Recherche du meilleur timonier
        for membre in equipage.Membres:
            if "Timonier" not in membre.Traits:
                continue

            resultat = utils.Test(membre.Navigation, 0)
            meilleur_test = max(meilleur_test, resultat)

        # Aucun timonier
        if meilleur_test == -999:
            return 75

        # Echec
        if meilleur_test <= 0:
            return random.randint(75, 100)

        # Réussite : un jet de 50-100 par succès, on garde le meilleur
        meilleur_bonus = 75
        for _ in range(meilleur_test):
            meilleur_bonus = max(meilleur_bonus, random.randint(75, 100))

        return meilleur_bonus

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
            pilotes = [
                membre
                for membre in equipage.Membres
                if "Navigateur" in membre.Traits
            ]

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
                valeur = equipage.ActionEquipage("Poursuite", "Equipage", 0, nom)[1]
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

    def CoursePoursuite(
            self,
            HeureAvantNuit,
            Dx,
            Dy,
            NavirePoursuivant_file,
            NavirePoursuive_file):

        poursuivant = Navire.charger_depuis_csv(NavirePoursuivant_file)
        poursuivi = Navire.charger_depuis_csv(NavirePoursuive_file)

        FenetreCourse(
            poursuivant,
            poursuivi,
            Dx,
            Dy,
            HeureAvantNuit
        )

        return texte, Distance

    def JourNavigation(self,NomNavire,NomEquipage,Zone):
        Text=""
        Text+=self.HautsFonds(NomNavire,Zone)
        Text+=self.Tempest(NomNavire)
        Pourcentage=self.TestNavigation(NomNavire)
        return Pourcentage

    def determiner_rencontre(self):

        if random.randint(1, 100) > 20:
            return None

        navire = Navire.generer_aleatoire(self.RegionCourante)

        return navire