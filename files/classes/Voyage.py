# -*- coding: utf-8 -*-
"""
Gestion d'une traversée maritime.

Responsabilités de Voyage :
    - piloter la traversée du navire 1 ;
    - avancer jour après jour ;
    - demander à Navigation de résoudre les aléas nautiques
      (navigation, hauts-fonds, tempêtes) ;
    - déclencher les rencontres avec un navire 2 ;
    - instancier/générer le navire 2 via la classe Navire ;
    - orchestrer l'interaction avec le navire 2.

Les règles de génération du navire, de son équipage, du combat naval et
les règles de navigation restent dans les modules spécialisés existants.
"""

import csv
import math
import os
import random
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import utils
from config import *
import Navigation
import Maladie
import Equipage
import CalculMarchandise
import Navire


# ---------------------------------------------------------------------------
# Constantes de voyage conservées depuis l'ancien module
# ---------------------------------------------------------------------------
NB_JOUR_BASE = 6
COMPETENCE_VIGIE_BASE = 2
NB = 182
NBSSS = 2
SUPERFICIE = 106460000 / 2
NB_DAYS_OF_CYCLONE = 59
NB_DAYS_OF_TEMPEST = 27
SURFACE = np.pi * 750 * 750
SEUIL_MARCHAND = 4
DE_MARCHAND = 20
SEUIL_AVENTURIER = 4
DE_AVENTURIER = 40
MUNITIONS = ["Boulets", "Rames", "Mitraille"]
PROBA_TEMPETE = round(SUPERFICIE / SURFACE * NB / NB_DAYS_OF_CYCLONE)


@dataclass
class Voyage:
    """Evénement enregistré pendant la traversée."""

    jour: int
    type: str
    texte: str
    donnees: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultatVoyage:
    """Etat final d'une traversée."""

    statut: str
    jour_fin: int
    distance_restante: float
    cout_base: float
    cout_salaire: float
    cout_ration: float
    texte: str
    evenements: list[Voyage] = field(default_factory=list)


class Voyage:
    """
    Modélise la traversée d'un navire 1.

    ``Voyage`` ne représente pas un navire. Il orchestre un trajet.

    Paramètres
    ----------
    navire1 : str | pd.DataFrame | pd.Series | dict
        Le navire joueur / navire qui effectue la traversée. Une chaîne
        correspond au nom du fichier CSV présent dans NAVIRE_PATH.
    distance : float
        Distance initiale à parcourir en milles nautiques.
    region : str
        Région maritime d'arrivée / de rencontre.
    zone : str
        Zone maritime utilisée par Navigation et les rencontres.
    competence_vigie : int
        Niveau de vigilance de la vigie.
    compagnie_commerciale : str
        Compagnie utilisée pour générer les navires marchands rencontrés.
    """

    def __init__(
        self,
        navire1: Any,
        distance: float,
        region: str,
        zone: str,
        competence_vigie: int = COMPETENCE_VIGIE_BASE,
        compagnie_commerciale: str = "Defaut",
        proba_tempete: int = PROBA_TEMPETE,
    ) -> None:
        self.navire1 = navire1
        self.distance_initiale = float(distance)
        self.distance_restante = float(distance)
        self.region = region
        self.zone = zone
        self.competence_vigie = competence_vigie
        self.compagnie_commerciale = compagnie_commerciale
        self.proba_tempete = proba_tempete

        # Etat courant de la traversée
        self.jour = 1
        self.heure = None
        self.statut = "PREPARE"
        self.texte = ""
        self.evenements: list[Voyage] = []

        # Navires
        self.navire1_df = self._charger_navire(navire1)
        self.navire2: Optional[pd.DataFrame] = None
        self.rencontre_courante: Optional[dict[str, Any]] = None

        # Comptabilité du voyage
        self.cout_base = 0.0
        self.cout_ration = 0.0
        self.cout_salaire = 0.0

        # Le coût de l'équipement est engagé au début du voyage.
        nb_hommes = int(self._valeur_navire1("Equipage", 0) or 0)
        _, _, self.cout_base = self.CalculVoyage(1, nb_hommes)

    # ------------------------------------------------------------------
    # Etat / utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def ConvertFloatToInt(valeur: float) -> int:
        """Convertit un flottant en entier par arrondi probabiliste."""
        valeur = float(valeur)
        partie_decimale = valeur % 1
        de = random.randrange(100)
        if partie_decimale and de <= partie_decimale * 100:
            valeur += 1
        return int(math.trunc(valeur))

    @staticmethod
    def _premiere_ligne(data: Any) -> pd.Series:
        """Retourne une représentation ``Series`` d'un navire."""
        if isinstance(data, pd.DataFrame):
            if data.empty:
                raise ValueError("Le DataFrame du navire est vide.")
            return data.iloc[0]
        if isinstance(data, pd.Series):
            return data
        if isinstance(data, dict):
            return pd.Series(data)
        raise TypeError(f"Type de navire non supporté : {type(data)!r}")

    def _charger_navire(self, navire: Any) -> pd.DataFrame:
        """Charge le navire 1 depuis un objet ou son fichier de sauvegarde."""
        if isinstance(navire, pd.DataFrame):
            return navire.copy()
        if isinstance(navire, pd.Series):
            return navire.to_frame().T
        if isinstance(navire, dict):
            return pd.DataFrame([navire])
        if isinstance(navire, str):
            chemins = [
                os.path.join(NAVIRE_PATH, navire),
                os.path.join(NAVIRE_PATH, f"{navire}.csv"),
            ]
            for chemin in chemins:
                if os.path.exists(chemin):
                    return pd.read_csv(
                        chemin,
                        sep=";",
                        decimal=",",
                        encoding="cp1252",
                    )
            raise FileNotFoundError(
                f"Impossible de trouver le navire 1 : {navire!r} dans {NAVIRE_PATH!r}."
            )
        raise TypeError(
            "navire1 doit être un nom de fichier, un DataFrame, une Series ou un dict."
        )

    def _valeur_navire1(self, colonne: str, defaut: Any = None) -> Any:
        if colonne not in self.navire1_df.columns:
            return defaut
        return self.navire1_df.iloc[0][colonne]

    @property
    def nom_navire1(self) -> str:
        return str(
            self._valeur_navire1(
                "Name",
                self._valeur_navire1("Nom", self.navire1 if isinstance(self.navire1, str) else "Navire1"),
            )
        )

    @property
    def nom_fichier_navire1(self) -> str:
        """Nom utilisé par les modules historiques (souvent sans chemin)."""
        if isinstance(self.navire1, str):
            return os.path.basename(self.navire1)
        equipage_nom = self._valeur_navire1("Name", None)
        if equipage_nom:
            return f"{equipage_nom}.csv"
        return f"{self.nom_navire1}.csv"

    def _ajouter_evenement(
        self,
        type_evenement: str,
        texte: str,
        donnees: Optional[dict[str, Any]] = None,
    ) -> None:
        self.evenements.append(
            Voyage(
                jour=self.jour,
                type=type_evenement,
                texte=texte,
                donnees=donnees or {},
            )
        )
        self.texte += texte
        if not texte.endswith("\n"):
            self.texte += "\n"

    # ------------------------------------------------------------------
    # Coûts
    # ------------------------------------------------------------------

    def CalculVoyage(self, nb_jours: int, nb_hommes: int) -> tuple[str, float, float]:
        """Calcule les coûts fixes et les rations d'une traversée."""
        cout_vivre = 1 / 150
        cout_rhum = 10 / 150
        solde = 0.31
        cout_sabre = 1
        cout_mousquet = 10
        cout_munition = 0.2

        cout_base = (
            cout_sabre * nb_hommes
            + cout_mousquet * nb_hommes
            + cout_munition * nb_hommes
        )
        cout_ration = (
            cout_rhum * nb_hommes * nb_jours
            + cout_vivre * nb_hommes * nb_jours
        )

        texte = (
            "\nCout traversee :\n"
            f"Cout vivre : {cout_vivre * nb_jours * nb_hommes}\n"
            f"Cout rhum : {cout_rhum * nb_jours * nb_hommes}\n"
            f"Cout sabre : {cout_sabre * nb_hommes}\n"
            f"Cout fusil : {cout_mousquet * nb_hommes}\n"
            f"Munition : {cout_munition * nb_hommes}\n"
            f"Cout solde journalier : {solde * nb_hommes}\n"
            f"Cout ration : {cout_ration}\n"
            f"Cout base : {cout_base}\n"
        )
        return texte, cout_ration, cout_base

    def _calculer_couts_journalier(self) -> None:
        nb_hommes = int(self._valeur_navire1("Equipage", 0) or 0)
        salaire_total = 0.0
        equipage_nom = self._valeur_navire1("EquipageNom", None)

        if equipage_nom:
            try:
                salaire_total = float(Equipage.AttributionSalaireParRole(equipage_nom)) / 30
            except Exception:
                salaire_total = 0.0

        cout_vivre = 1 / 150
        cout_rhum = 10 / 150
        self.cout_ration += (cout_vivre + cout_rhum) * nb_hommes
        self.cout_salaire += salaire_total

    # ------------------------------------------------------------------
    # Aléas de navigation
    # ------------------------------------------------------------------

    def _tester_navigation(self) -> str:
        """Demande à Navigation de calculer l'erreur de route."""
        try:
            erreur = Navigation.TestNavigation(self.nom_fichier_navire1)
        except Exception as exc:
            return f"Erreur lors du test de navigation : {exc}\n"

        try:
            erreur = float(erreur)
        except (TypeError, ValueError):
            erreur = 0.0

        self.distance_restante += erreur
        if erreur > 0:
            return f"Erreur de navigation : +{erreur:.2f} milles.\n"
        if erreur < 0:
            return f"Bonne navigation : {erreur:.2f} milles économisés.\n"
        return "Navigation sans écart significatif.\n"

    def _tester_hauts_fonds(self) -> str:
        """Laisse Navigation gérer le test hydrographique."""
        try:
            texte = Navigation.TestHydrographie(self.nom_fichier_navire1, self.zone)
        except Exception as exc:
            texte = f"Erreur lors du test des hauts-fonds : {exc}\n"
        return str(texte) + ("" if str(texte).endswith("\n") else "\n")

    def _tester_tempete(self) -> tuple[str, float]:
        """Effectue un seul test de tempête pour la journée."""
        try:
            resultat = Navigation.Tempest(
                self.nom_fichier_navire1,
                self.proba_tempete,
                self.jour,
            )
            texte = str(resultat[0])
            variation_distance = float(resultat[1])
        except Exception as exc:
            texte = f"Erreur lors du test de tempête : {exc}\n"
            variation_distance = 0.0

        if not texte.endswith("\n"):
            texte += "\n"
        self.distance_restante += variation_distance
        return texte, variation_distance

    def _navire_coule(self, texte: str) -> bool:
        return "coule" in texte.lower()

    # ------------------------------------------------------------------
    # Rencontre avec un navire 2
    # ------------------------------------------------------------------

    def _creer_generateur_navire(self) -> Any:
        """Instancie la classe Navire utilisée pour générer le navire 2.

        Le module Navire historique utilise encore une instance comme
        gestionnaire de génération. Cette méthode isole ce détail de
        compatibilité dans Voyage.
        """
        return Navire.Navire(0, "Rencontre", f"Voyage_{self.jour}")

    def _instancier_navire2(
        self,
        type_rencontre: str,
        compagnie: str,
        sauvegarder: bool = True,
    ) -> tuple[Any, str]:
        """Génère le navire 2 via la classe Navire."""
        identifiant = f"{self.jour}_{type_rencontre.upper()}_{self.region}_{self.zone}"
        generateur = self._creer_generateur_navire()

        if hasattr(generateur, "RencontreNavire"):
            navire2, texte = generateur.RencontreNavire(
                identifiant,
                self.region,
                sauvegarder,
                compagnie,
            )
        else:
            raise AttributeError(
                "La classe Navire ne possède pas la méthode RencontreNavire attendue."
            )

        self.navire2 = navire2.copy() if isinstance(navire2, pd.DataFrame) else navire2
        return navire2, str(texte)

    def DistanceVision(self, coeff: float, competence_vigie: int) -> tuple[str, float]:
        dmax = (5 + coeff) / 1.82
        reussite = utils.Test(competence_vigie, 0)
        if reussite < 0:
            distance = utils.MinGauss(dmax / 2, dmax / 4, 1)
        else:
            distance = utils.MaxGauss(dmax / 2, dmax / 4, reussite + 1)
        angle = round(random.uniform(0, 360), 2)
        texte = f"Situe a {distance} miles nautiques\nA {angle} degrés du navire\n"
        return texte, distance

    def ReconnaissanceNavire(self, vigilance: int, navire: Any) -> str:
        texte = "Votre vigie a aperçu un navire avec :\n"
        navire_serie = self._premiere_ligne(navire)
        categories = ["CategorieNavire", "NbCanons", "NbMats", "Longueur"]

        for colonne in categories:
            if colonne not in navire_serie.index:
                continue
            succes = utils.Test(vigilance, 0)
            valeur = navire_serie[colonne]
            estimation = utils.MaxGauss(valeur, valeur / 2, succes)
            texte += f" - {colonne} : {estimation}\n"
        return texte

    def CalculInteretCombat(self, navire_pirate: Any, navire_pj: Any) -> int:
        pirate = self._premiere_ligne(navire_pirate)
        pj = self._premiere_ligne(navire_pj)
        ratio = pirate["ValeurCombat"] / pj["ValeurCombat"]
        seuil_marchandise = 30

        if ratio >= 0.8 and (pirate["TonnageMax"] - pirate["Tonnage"]) > seuil_marchandise / ratio:
            return 1
        return 0

    def BonusVisionHauteurMat(self, categorie_navire: int) -> int:
        bonus = {
            0: 5,
            1: 8,
            2: 10,
            3: 18,
        }
        return bonus.get(int(categorie_navire), 0)

    def rencontrer_navire(
        self,
        type_rencontre: str,
        compagnie: Optional[str] = None,
        sauvegarder: bool = True,
        interaction: Optional[str] = None,
        afficher_fenetre: bool = True,
    ) -> dict[str, Any]:
        """Crée un navire 2 et prépare/interprète la rencontre."""
        compagnie = compagnie or self.compagnie_commerciale
        navire2, texte = self._instancier_navire2(type_rencontre, compagnie, sauvegarder)

        texte_reconnaissance = self.ReconnaissanceNavire(self.competence_vigie, navire2)
        categorie_navire1 = self._valeur_navire1("CategorieNavire", 0)
        coeff_vision = self.BonusVisionHauteurMat(categorie_navire1)
        texte_distance, distance_contact = self.DistanceVision(
            coeff_vision,
            self.competence_vigie,
        )

        interet = 0
        try:
            if "Pirate" in str(self._premiere_ligne(navire2).get("Allegence", "")):
                interet = self.CalculInteretCombat(navire2, self.navire1_df)
        except Exception:
            interet = 0

        texte_final = (
            f"\nRENCONTRE AVEC UN NAVIRE — JOUR {self.jour}\n"
            + texte
            + "\n"
            + texte_distance
            + texte_reconnaissance
        )

        self.rencontre_courante = {
            "jour": self.jour,
            "type": type_rencontre,
            "navire2": navire2,
            "distance": distance_contact,
            "interet": interet,
            "texte": texte_final,
        }
        self._ajouter_evenement("RENCONTRE_NAVIRE", texte_final, self.rencontre_courante)

        if interaction is not None:
            resultat_interaction = self.interagir_navire2(interaction, afficher_fenetre=False)
        elif afficher_fenetre:
            self.FormulaireRencontre(
                self.navire1_df,
                navire2,
                distance_contact,
                texte_final,
                interet,
            )
            resultat_interaction = None
        else:
            resultat_interaction = None

        return {
            "navire2": navire2,
            "distance": distance_contact,
            "interet": interet,
            "texte": texte_final,
            "interaction": resultat_interaction,
        }

    def interagir_navire2(self, choix: str, afficher_fenetre: bool = True) -> str:
        """Applique un choix au navire 2 courant."""
        if self.rencontre_courante is None or self.navire2 is None:
            return "Aucun navire 2 n'est actuellement en interaction.\n"

        resultat = self.ChoixRencontre(
            self.navire1_df,
            self.navire2,
            self.rencontre_courante["distance"],
            choix,
            self.rencontre_courante["interet"],
            afficher_fenetre=afficher_fenetre,
        )
        self._ajouter_evenement(
            "INTERACTION_NAVIRE",
            resultat,
            {"choix": choix},
        )
        return resultat

    def ChoixRencontre(
        self,
        navire_pj: Any,
        navire_pnj: Any,
        distance: float,
        choix: str,
        interet: int,
        afficher_fenetre: bool = True,
    ) -> str:
        """Résout l'interaction sans modifier les responsabilités de Navigation."""
        pnj = self._premiere_ligne(navire_pnj)
        texte = ""

        if choix == "NeRienFaire":
            if interet == 0:
                texte += "Vous ne faites rien, le navire s'éloigne et vous continuez votre trajet.\n"
            else:
                texte += "Le navire semble intéressé et se rapproche de vous.\n"

        elif choix == "Poursuivre":
            try:
                Navigation.CoursePoursuite(3, distance)
            except Exception as exc:
                texte += f"La poursuite n'a pas pu être calculée : {exc}\n"
            else:
                texte += "Vous poursuivez votre route / manœuvrez pour conserver l'écart.\n"

        elif choix in {"Attaquer", "Combattre"}:
            nom_pnj = pnj.get("Name", pnj.get("Nom", "navire ennemi"))
            texte += (
                f"Vous avez choisi d'attaquer le {nom_pnj}.\n"
                "Veuillez utiliser le système de bataille navale pour sélectionner "
                "les navires combattants et les munitions.\n"
            )

        elif choix == "Commercer":
            commerce_capitaine = utils.Compute(1)
            reussite_commerce = utils.Test(commerce_capitaine, 0)
            allegiance = str(pnj.get("Allegence", ""))

            if "Pirate" in allegiance or "Interlope" in allegiance:
                taux_vente = 80 - reussite_commerce * 10
                taux_achat = 100 + reussite_commerce * 10
                texte += (
                    "Vous pouvez acheter ou vendre des marchandises au capitaine.\n"
                    f"Vente : {taux_vente}% ; achat : {taux_achat}%.\n"
                )
            else:
                resultat = random.randint(1, 10)
                if resultat < 2:
                    texte += "Le capitaine n'est pas intéressé par le commerce. Vous poursuivez votre trajet.\n"
                else:
                    texte += (
                        "Le capitaine demande les papiers de provenance de vos marchandises "
                        "et peut vous conseiller le port le plus proche.\n"
                    )

        else:
            texte += f"Choix de rencontre inconnu : {choix}.\n"

        if afficher_fenetre:
            try:
                messagebox.showinfo("Résultat", texte)
            except Exception:
                pass
        return texte

    # ------------------------------------------------------------------
    # Boucle principale de la traversée
    # ------------------------------------------------------------------

    def vitesse_navire1(self) -> float:
        vitesse = self._valeur_navire1("Vitesse moyenne", 0)
        try:
            vitesse = float(vitesse)
        except (TypeError, ValueError):
            vitesse = 0.0
        if vitesse <= 0:
            raise ValueError("Le navire 1 doit avoir une 'Vitesse moyenne' positive.")
        return vitesse

    def _chance_rencontre_aventurier(self) -> bool:
        return random.randrange(int(DE_AVENTURIER)) + 1 <= SEUIL_AVENTURIER

    def _chance_rencontre_marchand(self) -> bool:
        return random.randrange(int(DE_MARCHAND)) + 1 <= SEUIL_MARCHAND

    def _rencontre_du_jour(self) -> None:
        """Détermine si un navire 2 doit être généré aujourd'hui."""
        if self._chance_rencontre_aventurier():
            self.rencontrer_navire(
                "AVENTURIER",
                compagnie="Pirate",
                sauvegarder=True,
                interaction=None,
                afficher_fenetre=True,
            )

        if self._chance_rencontre_marchand():
            self.rencontrer_navire(
                "MARCHAND",
                compagnie=self.compagnie_commerciale,
                sauvegarder=True,
                interaction=None,
                afficher_fenetre=True,
            )

    def _verifier_fin_apres_evenement(self) -> bool:
        if self.distance_restante <= -998:
            self.statut = "NAUFRAGE"
            return True
        if self.distance_restante <= 0:
            self.statut = "ARRIVE"
            return True
        return False

    def avancer_un_jour(self, rencontres: bool = True) -> bool:
        """Exécute une journée de traversée.

        Retourne ``True`` si le voyage continue, ``False`` s'il est terminé.
        """
        if self.statut not in {"PREPARE", "EN_COURS"}:
            return False

        self.statut = "EN_COURS"
        self._calculer_couts_journalier()

        vitesse = self.vitesse_navire1()
        self.distance_restante -= vitesse

        self._ajouter_evenement(
            "JOURNEE",
            (
                f"Rapport du jour {self.jour}.\n"
                f"Distance parcourue : {vitesse:.2f} milles.\n"
                f"Distance restante avant aléas : {self.distance_restante:.2f} milles.\n"
            ),
        )

        # Maladie de l'équipage
        equipage_nom = self._valeur_navire1("EquipageNom", None)
        if equipage_nom:
            try:
                texte_maladie = Maladie.test_maladie(1, 1, equipage_nom)
                self._ajouter_evenement("MALADIE", str(texte_maladie) + "\n")
            except Exception as exc:
                self._ajouter_evenement("MALADIE", f"Test de maladie indisponible : {exc}\n")

        # Navigation puis hauts-fonds / récifs puis tempête.
        self._ajouter_evenement("NAVIGATION", self._tester_navigation())
        self._ajouter_evenement("HYDROGRAPHIE", self._tester_hauts_fonds())

        texte_tempete, variation_tempete = self._tester_tempete()
        self._ajouter_evenement(
            "TEMPETE",
            texte_tempete,
            {"variation_distance": variation_tempete},
        )

        if self._navire_coule(texte_tempete):
            self.statut = "NAUFRAGE"
            self.distance_restante = -999
            self._ajouter_evenement("FIN", "Le navire 1 a coulé. FIN DU VOYAGE.\n")
            return False

        if self._verifier_fin_apres_evenement():
            self._ajouter_evenement("ARRIVEE", "Vous êtes arrivé à destination.\n")
            return False

        if rencontres:
            self._rencontre_du_jour()
            if self.statut == "NAUFRAGE":
                return False

        self.jour += 1
        return True

    def demarrer(
        self,
        rencontres: bool = True,
        nb_jours_max: Optional[int] = None,
    ) -> ResultatVoyage:
        """Lance toute la traversée jusqu'à l'arrivée, un naufrage ou la limite."""
        self.statut = "PREPARE"
        jours_executes = 0

        while self.statut in {"PREPARE", "EN_COURS"} and self.distance_restante > 0:
            if nb_jours_max is not None and jours_executes >= nb_jours_max:
                self.statut = "INTERRUPTU"
                break

            continue_voyage = self.avancer_un_jour(rencontres=rencontres)
            jours_executes += 1
            if not continue_voyage:
                break

        if self.statut == "EN_COURS" and self.distance_restante <= 0:
            self.statut = "ARRIVE"

        try:
            texte_salaire = f"\nLe voyage aura coûté au total {self.cout_salaire:.2f} en salaires.\n"
        except Exception:
            texte_salaire = ""
        self.texte += texte_salaire

        return ResultatVoyage(
            statut=self.statut,
            jour_fin=self.jour,
            distance_restante=self.distance_restante,
            cout_base=self.cout_base,
            cout_salaire=self.cout_salaire,
            cout_ration=self.cout_ration,
            texte=self.texte,
            evenements=self.evenements.copy(),
        )

    # ------------------------------------------------------------------
    # Compatibilité avec l'ancien point d'entrée RMarchand
    # ------------------------------------------------------------------

    def RMarchand(
        self,
        SeuilMa: int,
        DeMa: int,
        SeuilAv: int,
        DeAv: int,
        Distance: float,
        CompVigie: int,
        Region: str,
        Name1: str,
        Zone: str,
        CompagnieCommerciale: str,
    ) -> tuple[float, float, str]:
        """Compatibilité avec l'ancien appel.

        Les paramètres historiques sont conservés pour éviter de casser les
        anciennes interfaces. La logique est maintenant pilotée par l'objet
        Voyage lui-même.
        """
        self.distance_restante = float(Distance)
        self.region = Region
        self.zone = Zone
        self.competence_vigie = CompVigie
        self.compagnie_commerciale = CompagnieCommerciale

        # Si Name1 est fourni différent du navire chargé, on recharge le navire 1.
        if Name1 != self.nom_fichier_navire1 and Name1 != self.nom_navire1:
            self.navire1 = Name1
            self.navire1_df = self._charger_navire(Name1)

        resultat = self.demarrer(rencontres=True)
        return self.cout_base, self.cout_salaire, resultat.texte

    # ------------------------------------------------------------------
    # Interface graphique de choix d'interaction
    # ------------------------------------------------------------------

    def FormulaireRencontre(
        self,
        navire_pj: Any,
        navire_pnj: Any,
        distance: float,
        texte: str,
        interet: int,
    ) -> None:
        """Affiche la fenêtre d'interaction avec le navire 2."""
        root = tk.Toplevel()
        root.title("Rencontre navale")
        root.geometry("700x300")

        label = tk.Label(
            root,
            text=texte,
            wraplength=650,
            justify="left",
        )
        label.pack(pady=20, padx=10)

        frame_actions = tk.Frame(root)
        frame_actions.pack(pady=10)

        actions = [
            "NeRienFaire",
            "Poursuivre",
            "Attaquer",
            "Commercer",
        ]

        def executer_choix(choix: str) -> None:
            texte_resultat = self.ChoixRencontre(
                navire_pj,
                navire_pnj,
                distance,
                choix,
                interet,
                afficher_fenetre=False,
            )
            try:
                messagebox.showinfo("Résultat", texte_resultat)
            except Exception:
                pass
            root.destroy()

        for action in actions:
            bouton = tk.Button(
                frame_actions,
                text=action,
                command=lambda choix=action: executer_choix(choix),
            )
            bouton.pack(side="left", padx=5)

        root.grab_set()
        root.wait_window()

    def Choice_Rencontre(
        self,
        title: str,
        message: str,
        options: list[str],
    ) -> str:
        """Version CustomTkinter conservée pour compatibilité."""
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        app = ctk.CTk()
        app.withdraw()
        popup = ctk.CTkToplevel(app)
        popup.title(title)
        popup.geometry("600x400")
        popup.grab_set()

        choice = ctk.StringVar(value="")
        label = ctk.CTkLabel(
            popup,
            text=message,
            wraplength=500,
            justify="center",
        )
        label.pack(pady=20, padx=10)

        frame = ctk.CTkFrame(popup)
        frame.pack(pady=10)

        for option in options:
            def handler(value=option) -> None:
                choice.set(value)
                popup.destroy()

            button = ctk.CTkButton(
                frame,
                text=option,
                command=handler,
                width=100,
            )
            button.pack(side="left", padx=10)

        popup.wait_window()
        resultat = choice.get()
        try:
            app.destroy()
        except Exception:
            pass
        return resultat


# ---------------------------------------------------------------------------
# Exemple d'utilisation (désactivé)
# ---------------------------------------------------------------------------
# voyage = Voyage(
#     navire1="MonNavire.csv",
#     distance=120,
#     region="Atlantique",
#     zone="Zone1",
#     competence_vigie=2,
# )
# resultat = voyage.demarrer()
# print(resultat.texte)
