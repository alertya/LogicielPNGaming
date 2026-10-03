"""
moteur_interface.py
--------------------
Ce fichier définit LE CONTRAT entre l'interface graphique (app.py) et ton
moteur de calcul. L'interface ne connaît RIEN du fonctionnement interne de
ton jeu : elle appelle uniquement les méthodes ci-dessous.

Pour brancher ton propre moteur :
  1. Crée une classe qui hérite de `MoteurBase`.
  2. Implémente les 4 méthodes (get_instances, get_donnees, get_actions,
     executer_action) en te connectant à tes propres structures de données.
  3. Dans main.py, remplace `MoteurExemple()` par ta propre classe.

L'interface reconstruit automatiquement l'affichage à partir de ce que ces
méthodes renvoient : tu n'as jamais besoin de toucher au code de app.py.

------------------------------------------------------------------------
Rappel de la structure des onglets (définie dans app.py -> ONGLETS) :

    Journal de bord   -> Journal, Générer
    Navire            -> Afficher, Générer, Actions
    Equipage          -> Afficher, Générer, Recruter, Actions
    Marchandises      -> Afficher, Générer, Vendre/Acheter, Actions
    Escale            -> Afficher, Générer, Actions
    Infirmerie        -> Afficher, Actions
    Reset             -> Actions

Cas particulier "Journal de bord" -> "Générer" :
    Ce sous-onglet est affiché par un formulaire dédié (panneau_generation.py)
    plutôt que par le rendu générique liste déroulante/tableau. Il permet de
    construire un trajet étape par étape puis appelle `creer_trajet(...)`
    (voir plus bas). Les méthodes `get_instances/get_donnees/get_actions`
    ne sont donc jamais appelées pour ce sous-onglet précis.

Cas particulier "Equipage" -> "Générer" et "Navire" -> "Générer" :
    Même principe : formulaires dédiés (panneau_generation_equipage.py et
    panneau_generation_navire.py) qui appellent respectivement
    `generer_equipage(...)` et `generer_navire(...)` ci-dessous. Les listes
    déroulantes de ces formulaires viennent de `get_types_equipage()`,
    `get_types_navire()` et `get_regions_navire()`.

Sous-onglet "Actions" (présent sur chaque onglet vertical) :
    Boutons d'action rapide propres à chaque onglet vertical, listés dans
    `ACTIONS_PAR_ONGLET` ci-dessous (repris de ListeFeatures.xlsx). Pour
    ajouter/retirer un bouton, il suffit de modifier cette constante — pas
    besoin de toucher à app.py.
------------------------------------------------------------------------
"""

from __future__ import annotations
import copy
import copy

import random

import pandas as pd

import utils
from typing import Any, Dict, List, Optional, Union

import config

import os

from classes.Equipage import Equipage
from classes.Navire import Navire
from classes.Marchandise import Marchandise

import numpy as np


# Type d'une "fiche" de données que l'interface sait afficher automatiquement :
#  - un dict simple  -> affiché en liste clé / valeur
#  - une liste de dict -> affichée sous forme de tableau (mêmes colonnes)
#  - une chaîne / liste de chaînes -> affichée comme du texte (ex : journal de bord)
DonneesAffichables = Union[Dict[str, Any], List[Dict[str, Any]], str, List[str], None]

print("F")
class MoteurBase:
    """
    Classe abstraite (contrat). Hérite de cette classe pour brancher ton
    moteur de calcul. Ne pas instancier directement.
    """

    def get_instances(self, onglet: str, sous_onglet: Optional[str]) -> List[str]:
        """
        Renvoie la liste des noms d'instances à proposer dans la liste
        déroulante en haut de l'écran, pour l'onglet/sous-onglet donné.

        Exemples :
          - onglet="Navire", sous_onglet="Afficher"  -> ["Le Vengeur", "L'Aurore"]
          - onglet="Equipage", sous_onglet="Recruter" -> ["Port de Tortuga"]
          - onglet="Journal de bord"                  -> []  (pas de dropdown)
          - onglet="Reset"                             -> []  (action globale)

        Renvoyer une liste vide masque automatiquement la liste déroulante.
        """
        raise NotImplementedError

    def get_donnees(
        self, onglet: str, sous_onglet: Optional[str], instance: Optional[str]
    ) -> DonneesAffichables:
        """
        Renvoie les données à afficher dans le panneau principal pour
        l'instance sélectionnée (ou None si aucune instance/dropdown vide).

        Formats acceptés (l'interface s'adapte automatiquement) :
          - dict            -> tableau clé / valeur (ex : caractéristiques du navire)
          - list[dict]      -> tableau à colonnes (ex : liste de l'équipage)
          - str / list[str] -> texte brut (ex : journal de bord, message de log)
          - None            -> affiche un message "aucune donnée"
        """
        raise NotImplementedError

    def get_actions(
        self, onglet: str, sous_onglet: Optional[str], instance: Optional[str]
    ) -> List[str]:
        """
        Renvoie la liste des boutons d'action à afficher en bas du panneau
        pour ce contexte (ex : ["Générer"], ["Recruter", "Renvoyer"],
        ["Réinitialiser"]...). Renvoyer [] n'affiche aucun bouton
        (utile pour un onglet purement "Afficher").
        """
        raise NotImplementedError

    def executer_action(
        self,
        onglet: str,
        sous_onglet: Optional[str],
        instance: Optional[str],
        action: str,
    ) -> str:
        """
        Appelée quand l'utilisateur clique sur un bouton d'action.
        Doit exécuter la logique dans ton moteur puis renvoyer un message
        (str) qui sera affiché à l'utilisateur (résultat, confirmation,
        erreur...).
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Méthodes spécifiques à l'onglet "Journal de bord"
    # ------------------------------------------------------------------ #
    def get_navires(self) -> List[str]:
        """
        Renvoie la liste des navires de la flotte. Utilisée pour :
          - la liste déroulante d'instance du sous-onglet "Journal"
          - le sélecteur de navire du formulaire "Générer"
        """
        raise NotImplementedError

    def creer_trajet(self, navire: str, annee_historique: int, etapes: List[Dict[str, Any]]) -> str:
        """
        Crée (ou remplace) le trajet prévu pour `navire`, à partir de la
        liste ordonnée `etapes` construite par le formulaire "Générer".
        Chaque étape est un dict avec les clés :
            Region, ZoneMaritime, TaillePortEscale, Distance,
            ChanceRencontreAventurier, CompetenceVigie,
            EscaleRecrutement, EscaleCommerce, EscaleReparation,
            DeMarchand, DeAventurier
        Doit réinitialiser le journal de bord du navire au jour 1.
        Renvoie un message de confirmation affiché dans la barre de statut.
        """
        raise NotImplementedError

    def avancer_jour(self, navire: str) -> str:
        """
        Fait avancer le voyage de `navire` d'un jour de navigation :
        progression le long de l'étape courante, passage à l'étape
        suivante une fois la distance parcourue, tirage éventuel d'une
        rencontre, etc. Renvoie un résumé des événements du jour (celui-ci
        doit aussi être conservé pour être ré-affiché par get_donnees).
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Méthodes spécifiques à l'onglet "Equipage" -> "Générer"
    # ------------------------------------------------------------------ #
    def get_types_equipage(self) -> List[str]:
        """
        Renvoie la liste des types d'équipage proposés dans la liste
        déroulante du formulaire (colonne "Type" de data/ListeProf.csv).
        """
        raise NotImplementedError

    def generer_equipage(
        self, nom: str, type_equipage: str, nombre: int, effectifs: Dict[str, int]
    ) -> str:
        """
        Génère un équipage de `nombre` personnes et l'enregistre en CSV
        (séparateur ";", décimal ",", encodage "cp1252") sous
        data/Equipage/<nom>.csv.

        `effectifs` est un dict {typologie: nombre} pour les typologies
        saisies dans le formulaire : Calfat, Coq, Charpentier, Chirurgien,
        Pilote, Soldat, Voilier.

        Renvoie un message de confirmation affiché dans la barre de statut.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Méthodes spécifiques à l'onglet "Navire" -> "Générer"
    # ------------------------------------------------------------------ #
    def get_types_navire(self) -> List[str]:
        """
        Renvoie la liste des types de navire proposés dans la liste
        déroulante du formulaire (colonne "Typologie" de
        data/RencontreNavire.csv).
        """
        raise NotImplementedError

    def get_regions_navire(self) -> List[str]:
        """
        Renvoie la liste des régions d'origine proposées dans la liste
        déroulante du formulaire (colonne "Regions" de data/ListeRegions.csv).
        """
        raise NotImplementedError

    def generer_navire(self, nom: str, type_navire: str, region: str) -> str:
        """
        Génère un navire et l'enregistre en CSV (séparateur ";", décimal ",",
        encodage "cp1252") sous data/Navire/<nom>.csv.
        Renvoie un message de confirmation affiché dans la barre de statut.
        """
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Boutons d'action rapide par onglet vertical (extraits de ListeFeatures.xlsx)
# ---------------------------------------------------------------------------
# Ces actions apparaissent sur le sous-onglet "Actions" de chaque onglet
# vertical. Modifie cette liste pour ajouter/retirer un bouton — l'interface
# s'adapte automatiquement, aucune autre modification n'est nécessaire.
# ---------------------------------------------------------------------------
ACTIONS_PAR_ONGLET: Dict[str, List[str]] = {
    "Navire": ["Combattre", "Poursuite"],
    "Equipage": ["Bataille terrestre", "Test compétence"],
    "Marchandises": ["Vendre","Acheter"],
    "Escale": ["Recruter au port", "Réparer navire", "Trouver marchand", "Enquêter"],
    "Infirmerie": ["Voir blessé/malade", "Sacrifier blessé"],
    "Reset": ["Supprimer toutes les données (Navire, Equipage, Escale, Voyage)"],
}

# ---------------------------------------------------------------------------
# Typologies d'équipage saisies individuellement dans le formulaire
# "Equipage" -> "Générer" (voir panneau_generation_equipage.py)
# ---------------------------------------------------------------------------
TYPOLOGIES_EQUIPAGE: List[str] = [
    "Calfat", "Coq", "Charpentier", "Chirurgien", "Pilote", "Soldat", "Voilier",
]


# ---------------------------------------------------------------------------
# MOTEUR D'EXEMPLE
# ---------------------------------------------------------------------------
# Implémentation factice, uniquement pour que l'interface soit testable
# immédiatement "out of the box". Remplace-la par ta propre classe dans
# main.py dès que ton moteur de calcul est prêt.
# ---------------------------------------------------------------------------
DISTANCE_PAR_JOUR_NM = 100  # milles nautiques parcourus par jour par défaut (exemple)


class MoteurExemple(MoteurBase):
    # Données de départ, conservées à part pour pouvoir tout réinitialiser
    # via l'action "Supprimer toutes les données..." de l'onglet Reset.
    _NAVIRES_INITIAUX = {
        "Le Vengeur": {"Coque": "82%", "Voiles": "100%", "Canons": 12, "Vitesse": "8 nœuds"},
        "L'Aurore": {"Coque": "100%", "Voiles": "90%", "Canons": 8, "Vitesse": "10 nœuds"},
    }
    _EQUIPAGE_INITIAL = {
        "Le Vengeur": [
            {"Nom": "Jack Renard", "Rôle": "Capitaine", "Santé": "Bonne"},
            {"Nom": "Anne Cros", "Rôle": "Canonnier", "Santé": "Blessée"},
        ],
        "L'Aurore": [
            {"Nom": "Tom Belair", "Rôle": "Second", "Santé": "Bonne"},
        ],
    }

    def __init__(self):
        # self._voyages[navire] = {
        #     "annee_historique": int,
        #     "etapes": [étape, ...],
        #     "etape_idx": int,               # étape en cours (index dans "etapes")
        #     "avancement_nm": int,           # milles nautiques parcourus dans l'étape courante
        #     "jour": int,                    # jour de voyage courant
        #     "journal": {jour: [evenements]} # historique des événements par jour
        # }
        self._voyages: Dict[str, Dict[str, Any]] = {}
        self._navires = Navire("Sloop","NavireTest","Brésil")
        self._equipage= Equipage(10,"Matelot","EquipageTest")
        self._marchandise=Marchandise()
        # NB : ChargerEquipages() peuple self._equipage lui-même (il ne
        # renvoie rien) — on l'appelle donc sans réaffecter self._equipage.

    def _get_instances_dossier(self, nom_dossier):
        dossier = os.path.join(config.BASE_PATH, nom_dossier)

        if not os.path.isdir(dossier):
            return []

        return sorted(
            os.path.splitext(f)[0]
            for f in os.listdir(dossier)
            if f.lower().endswith(".csv")
        )

    def get_instances(self, onglet, sous_onglet):

        if onglet == "Journal de bord":
            return self._get_instances_dossier("Navire") if sous_onglet == "Journal" else []

        if onglet == "Navire":
            return self._get_instances_dossier("Navire")

        if onglet == "Equipage":
            return self._get_instances_dossier("Equipage")

        if onglet == "Marchandises":
            return self._get_instances_dossier("Marchandise")

        if onglet in ("Escale", "Infirmerie"):
            return self._get_instances_dossier("PNJ")

        if onglet == "Reset":
            return []

        return []

    def get_donnees(self, onglet, sous_onglet, instance):
        if onglet == "Journal de bord" and sous_onglet == "Journal":
            return self._journal_du_jour(instance)
        if onglet == "Navire" and sous_onglet == "Afficher":
            return self._navires.charger_depuis_csv(instance)
        if onglet == "Equipage" and sous_onglet == "Afficher":
            return self._equipage.charger_depuis_csv(instance)
        if onglet == "Marchandises":
            return self._marchandise.charger_depuis_csv(instance)
        return f"(Exemple) Pas encore de données pour {onglet} / {sous_onglet} / {instance}"

    def get_actions(self, onglet, sous_onglet, instance):
        if onglet == "Journal de bord" and sous_onglet == "Journal":
            return ["Passer au jour de navigation suivant"]
        if sous_onglet == "Actions":
            return ACTIONS_PAR_ONGLET.get(onglet, [])
        if sous_onglet in ("Générer", "Recruter", "Vendre/Acheter"):
            return [sous_onglet]
        return []

    def executer_action(self, onglet, sous_onglet, instance, action):
        if onglet == "Journal de bord" and sous_onglet == "Journal" and action == "Passer au jour de navigation suivant":
            return self.avancer_jour(instance)
        if onglet == "Reset" and sous_onglet == "Actions":
            return self._reset_toutes_les_donnees()
        # Les autres actions (Combattre, Réparer navire, Recruter au port...) sont
        # de simples exemples : implémente ici la vraie logique de ton moteur.
        return f"(Exemple) Action « {action} » exécutée pour « {instance} » dans l'onglet « {onglet} »."

    def _reset_toutes_les_donnees(self) -> str:
        self._voyages = {}
        self._navires = copy.deepcopy(self._NAVIRES_INITIAUX)
        self._equipage = copy.deepcopy(self._EQUIPAGE_INITIAL)
        return "Toutes les données (Navire, Equipage, Escale, Voyage) ont été réinitialisées."

    # ------------------------------------------------------------------ #
    # Journal de bord / trajet
    # ------------------------------------------------------------------ #
    def get_navires(self) -> List[str]:
        return list(self._navires.keys())

    def creer_trajet(self, navire, annee_historique, etapes):
        if not navire:
            return "Aucun navire sélectionné."
        if not etapes:
            return "Le trajet doit contenir au moins une étape."

        premiere = etapes[0]
        self._voyages[navire] = {
            "annee_historique": annee_historique,
            "etapes": etapes,
            "etape_idx": 0,
            "avancement_nm": 0,
            "jour": 1,
            "journal": {
                1: [
                    f"Départ du voyage (année {annee_historique}). "
                    f"Cap sur « {premiere['Region']} » "
                    f"({premiere['Distance']} milles nautiques à parcourir)."
                ]
            },
        }
        return f"Trajet créé pour « {navire} » : {len(etapes)} étape(s), destination initiale « {premiere['Region']} »."

    def avancer_jour(self, navire: str) -> str:
        voyage = self._voyages.get(navire)
        if not voyage:
            return "Aucun trajet actif pour ce navire — utilise l'onglet « Générer » pour en créer un."

        etapes = voyage["etapes"]
        idx = voyage["etape_idx"]
        if idx >= len(etapes):
            return "Le voyage est déjà terminé : toutes les étapes ont été parcourues."

        etape = etapes[idx]
        voyage["jour"] += 1
        jour = voyage["jour"]
        evenements: List[str] = []

        voyage["avancement_nm"] += DISTANCE_PAR_JOUR_NM
        evenements.append(
            f"Navigation « {etape['ZoneMaritime']} » en direction de « {etape['Region']} » : "
            f"{DISTANCE_PAR_JOUR_NM} milles nautiques parcourus "
            f"({min(voyage['avancement_nm'], etape['Distance'])}/{etape['Distance']})."
        )

        # --- Exemple de tirage de rencontre --------------------------------------
        # Logique volontairement simple, à remplacer par tes propres règles :
        # probabilité = ChanceRencontreAventurier / DeAventurier, réduite par
        # la compétence de vigie.
        try:
            de_aventurier = int(etape.get("DeAventurier") or 0)
        except (TypeError, ValueError):
            de_aventurier = 0
        chance = int(etape.get("ChanceRencontreAventurier") or 0)
        vigie = int(etape.get("CompetenceVigie") or 0)

        if de_aventurier > 0 and chance > 0:
            tirage = random.randint(1, de_aventurier)
            seuil = max(0, chance - vigie)
            if tirage <= seuil:
                evenements.append("⚠️ Une voile suspecte a été repérée à l'horizon !")

        # --- Arrivée à l'étape suivante --------------------------------------------
        if voyage["avancement_nm"] >= etape["Distance"]:
            voyage["avancement_nm"] = 0
            voyage["etape_idx"] += 1
            if etape["TaillePortEscale"] != "Aucune (pas d'escale)":
                evenements.append(f"⚓ Arrivée à l'escale : « {etape['Region']} » ({etape['TaillePortEscale']}).")
            else:
                evenements.append(f"Cap suivant atteint : « {etape['Region']} » (pas d'escale prévue ici).")
            if voyage["etape_idx"] >= len(etapes):
                evenements.append("🏁 Le trajet prévu est terminé.")

        voyage["journal"][jour] = evenements
        return " ".join(evenements)

    def _journal_du_jour(self, navire: Optional[str]) -> List[str]:
        voyage = self._voyages.get(navire) if navire else None
        if not voyage:
            return ["Aucun trajet actif pour ce navire.", "Rends-toi dans l'onglet « Générer » pour en créer un."]

        etapes = voyage["etapes"]
        idx = voyage["etape_idx"]
        if idx < len(etapes):
            etape = etapes[idx]
            ligne_etape = (
                f"Étape en cours : {etape['Region']} "
                f"({voyage['avancement_nm']}/{etape['Distance']} milles nautiques parcourus)"
            )
        else:
            ligne_etape = "Voyage terminé — toutes les étapes ont été parcourues."

        lignes = [
            f"Jour {voyage['jour']}  —  Année historique {voyage['annee_historique']}",
            ligne_etape,
            "— Événements du jour —",
        ]
        lignes.extend(voyage["journal"].get(voyage["jour"], ["(rien à signaler)"]))
        return lignes

    def ChargerEquipages(self):

        dossier = os.path.join(config.BASE_PATH, "Equipage")

        self._equipage = {}

        if not os.path.isdir(dossier):
            # Le dossier n'existe pas encore (premier lancement) : on le
            # crée pour que generer_equipage() puisse y écrire plus tard,
            # et on repart sur un équipage vide plutôt que de planter.
            os.makedirs(dossier, exist_ok=True)
            return

        for fichier in os.listdir(dossier):

                if not fichier.lower().endswith(".csv"):
                    continue

                chemin = os.path.join(dossier, fichier)

                df = pd.read_csv(
                    chemin,
                    sep=";",
                    decimal=",",
                    encoding="cp1252"
                )

                nom = os.path.splitext(fichier)[0]
                type_equipage = df["Type"].iloc[0]
                self._equipage[nom] = Equipage.Charger(
                    df,
                    Name=nom
                )

    # ------------------------------------------------------------------ #
    # Listes de référence pour les formulaires "Générer"
    # ------------------------------------------------------------------ #
    @staticmethod
    def _lire_colonne_csv(chemin: str, colonne: str) -> List[str]:
        """
        Lit une colonne d'un CSV (séparateur ";", décimal ",", cp1252) et
        renvoie ses valeurs uniques, triées. Renvoie [] si le fichier ou la
        colonne est introuvable, plutôt que de faire planter l'interface.
        """
        if not os.path.isfile(chemin):
            print(f"[MoteurExemple] Fichier introuvable : {chemin}")
            return []
        try:
            df = pd.read_csv(chemin, sep=";", decimal=",", encoding="cp1252")
        except Exception as e:
            print(f"[MoteurExemple] Erreur de lecture de {chemin} : {e}")
            return []
        if colonne not in df.columns:
            print(f"[MoteurExemple] Colonne « {colonne} » absente de {chemin}")
            return []
        return sorted(df[colonne].dropna().astype(str).unique().tolist())

    # ------------------------------------------------------------------ #
    # Equipage -> Générer
    # ------------------------------------------------------------------ #
    def get_types_equipage(self) -> List[str]:
        chemin = os.path.join(config.BASE_PATH, "ListeProf.csv")
        return self._lire_colonne_csv(chemin, "Type")

    def generer_equipage(self, nom, type_equipage, nombre, effectifs):

        equipage = Equipage.generer(
            nom,
            type_equipage,
            nombre,
            effectifs
        )

        self._equipage = equipage

        return f"Équipage {nom} généré."


    # ------------------------------------------------------------------ #
    # Navire -> Générer
    # ------------------------------------------------------------------ #
    def get_types_navire(self) -> List[str]:
        chemin = os.path.join(config.BASE_PATH, "RencontreNavire.csv")
        return self._lire_colonne_csv(chemin, "Nom")

    def get_regions_navire(self) -> List[str]:
        chemin = os.path.join(config.BASE_PATH, "ListeRegions.csv")
        return self._lire_colonne_csv(chemin, "RegionsCommerciale")

    def generer_navire(self, nom, type_navire, region):
        if not nom:
            return "Merci de saisir un nom de navire."

        dossier = os.path.join(config.BASE_PATH, "Navire")
        os.makedirs(dossier, exist_ok=True)

        ligne = {"Nom": nom, "Type": type_navire, "Region": region}
        df = pd.DataFrame([ligne])
        chemin = os.path.join(dossier, f"{nom}.csv")
        df.to_csv(chemin, sep=";", decimal=",", encoding="cp1252", index=False)

        # Fiche minimale pour affichage immédiat dans l'onglet Navire -> Afficher.
        # À remplacer par ta vraie génération (coque, canons, équipage...),
        # par exemple en appelant ta classe Navire.
        self._navires = Navire(type_navire,nom,region)

        return f"Navire « {nom} » ({type_navire}, origine {region}) généré et enregistré dans {chemin}."

    def get_actions(self, onglet, sous_onglet, instance):

        if sous_onglet != "Actions":
            return []

        if onglet == "Navire":
            navire = Navire.charger_depuis_csv(instance)
            return navire.get_actions() if navire else []

        if onglet == "Equipage":
            equipage = Equipage.charger_depuis_csv(instance)
            return equipage.get_actions() if equipage else []

        if onglet == "Marchandises":
            marchandise = Marchandise.charger_depuis_csv(instance)
            return marchandise.get_actions() if marchandise else []

        #if onglet == "Escale":
        #    escale = Escale.charger_depuis_csv(instance)
        #    return escale.get_actions() if escale else []

        if onglet == "Infirmerie":
            return self._navires[instance].Equipage.Infirmerie.get_actions()

        return []

    def executer_action(self, onglet, sous_onglet, instance, action,valeurs=None):

        if onglet == "Equipage":
            equipage = Equipage.charger_depuis_csv(instance)
            return equipage.executer_action(action,instance,valeurs)
        if onglet == "Navire":
            navire = Navire.charger_depuis_csv(instance)
            return navire.executer_action(action,instance,valeurs)
        if onglet == "Marchandises":
            marchandise = Marchandise.charger_depuis_csv(instance)
            return marchandise.executer_action(action,instance,valeurs)

        return ""

    def get_boutons_action(self, onglet, instance, action):

        if onglet == "Equipage":
            equipage = Equipage.charger_depuis_csv(instance)
            return equipage.get_boutons(action) if equipage else []

        if onglet == "Navire":
            navire = Navire.charger_depuis_csv(instance)
            return navire.get_boutons(action) if navire else []
        if onglet == "Marchandises":
            marchandise = Marchandise.charger_depuis_csv(instance)
            return marchandise.get_boutons(action) if marchandise else []

        return []

    def get_formulaire_action(self, onglet: str, action: str):
        return

    def charger_marchandise(self, nom):
        return Marchandise.charger_depuis_csv(nom)

    def get_types_membre(self):
        df = pd.read_csv(
            config.BASE_PATH + "/ListeProf.csv",
            sep=";",
            decimal=",",
            encoding="cp1252"
        )

        return sorted(df["Type"].dropna().unique().tolist())

    def Recrute(self, Nb, Type, Bonus):

        Pond = pd.read_csv(
            config.BASE_PATH + "/ListeProf.csv",
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
            # Initialisation des PV
            membre.PVMax = random.randint(5, 8)
            membre.PV = membre.PVMax
            # Calculs individuels
            self.ScoreMembre(membre)
            self.AttributeGroupeMembre(membre)

            self.Membres.append(membre)
            self.AjoutTrait()
        self.ValeurCombat = self.CalculCombatEquipage()

        return Temp

    def CombatNaval(self,navire1, munition1,bonus1, navire2, munition2,bonus2):

        texte = ""

        degat1, recharge1 = self.DegatsNavire(
            navire1,
            navire2,
            munition1,bonus1
        )

        degat2, recharge2 = self.DegatsNavire(
            navire2,
            navire1,
            munition2,bonus2
        )

        texte += (
            f"{navire1.Name} a besoin de {recharge1} tours "
            "pour recharger sa prochaine batterie.\n"
        )

        texte += (
            f"{navire2.Name} a besoin de {recharge2} tours "
            "pour recharger sa prochaine batterie.\n"
        )

        print(f"{navire1.Name} a besoin de {recharge1} tours pour recharger.")
        print(f"{navire2.Name} a besoin de {recharge2} tours pour recharger.")

        # Le navire 1 subit les dégâts du navire 2
        if navire1.Equipage.Nombre > 0:

            perte1, temp = self.PerteNavire(
                navire1,
                degat2,
                munition2
            )

            texte += temp + "\n"

            texte += navire1.Equipage.Attitude(
                -perte1 / navire1.Equipage.Nombre * 50
            )[1]

        else:

            texte += f"{navire1.Name} a été décimé.\n"

        # Le navire 2 subit les dégâts du navire 1
        if navire2.Equipage.Nombre > 0:

            perte2, temp = self.PerteNavire(
                navire2,
                degat1,
                munition1
            )

            texte += temp + "\n"

            texte += navire2.Equipage.Attitude(
                -perte2 / navire2.Equipage.Nombre * 50
            )[1]

        else:

            texte += f"{navire2.Name} a été décimé.\n"

        Texte+=f"{navire1.Name} a perdu {perte1} hommes"
        Texte+=f"{navire2.Name} a perdu {perte2} hommes"

        return texte

    def Reparer(self):
        ReparationCoque=self.StructureCoque/self.StructureCoqueMax
        ReparationVoile=self.StructureVoile/self.StructureVoileMax
        CoutReparation=self.CoutSansCanon*(ReparationVoile+ReparationCoque)/2
        self.StructureVoile=self.StructureVoileMax
        self.StructureCoque=self.StructureCoqueMax
        CompCharpentier=utils.Compute(1)
        TempsEnJourReparation=utils.TestValeurNonNumerique(CompCharpentier,0)[0]
        return CoutReparation,TempsEnJourReparation