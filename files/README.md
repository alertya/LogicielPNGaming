# Interface — Compagnie des Mers (Tkinter)

Interface graphique type "jeu vidéo de gestion", générée à partir de la
structure d'onglets définie dans `Interface.xlsx` :

| Onglet vertical | Onglets horizontaux |
|---|---|
| Journal de bord | Journal, Générer |
| Navire | Afficher, Générer, Actions |
| Equipage | Afficher, Générer, Recruter, Actions |
| Marchandises | Afficher, Générer, Vendre/Acheter, Actions |
| Escale | Afficher, Générer, Actions |
| Infirmerie | Afficher, Actions |
| Reset | Actions |

## Lancer l'interface

```bash
python main.py
```

Aucune dépendance externe : uniquement `tkinter`, inclus dans Python standard
(sous Linux, si besoin : `sudo apt install python3-tk`).

Au lancement, l'interface tourne avec un **moteur d'exemple**
(`MoteurExemple` dans `moteur_interface.py`) contenant des données factices,
pour que tu puisses voir immédiatement le rendu.

## Fichiers

- `theme.py` — couleurs / polices, à personnaliser librement.
- `donnees_reference.py` — listes déroulantes et table Zone → dés, extraites
  de ton fichier Excel (Régions, Zones maritimes, Tailles de port).
- `moteur_interface.py` — **le contrat** entre l'interface et ton moteur
  (`MoteurBase`), + un moteur d'exemple (`MoteurExemple`) avec une
  simulation de voyage jour par jour.
- `panneau_generation.py` — le formulaire dynamique de création de trajet
  (onglet Journal de bord → Générer), avec bouton **+ Ajouter une étape**.
- `panneau_generation_equipage.py` — formulaire de création d'équipage
  (onglet Equipage → Générer).
- `panneau_generation_navire.py` — formulaire de création de navire
  (onglet Navire → Générer).
- `app.py` — l'interface graphique elle-même (onglets verticaux/horizontaux,
  liste déroulante d'instance, affichage automatique, boutons d'action).
  **Tu n'as normalement pas besoin d'y toucher.**
- `main.py` — point d'entrée, choisit quel moteur brancher.

## Journal de bord

### Sous-onglet "Journal"

Affiche, pour le navire sélectionné dans la liste déroulante :
- le jour de voyage courant et l'année historique,
- l'étape en cours et la progression (milles nautiques parcourus / distance totale),
- les événements du jour (navigation, rencontres, arrivées à une escale...).

Le bouton **"Passer au jour de navigation suivant"** appelle
`moteur.avancer_jour(navire)`, qui fait progresser le voyage d'un jour (voir
`MoteurExemple.avancer_jour` pour un exemple : avancée de 100 milles
nautiques/jour, tirage de rencontre basé sur `ChanceRencontreAventurier` /
`DeAventurier` / `CompetenceVigie`, passage automatique à l'étape suivante).

**C'est ici que tu dois brancher tes vraies règles de jeu** (vitesse réelle
du navire, table de rencontre complète avec `DeMarchand`, effets d'une
rencontre, etc.) — l'exemple fourni est volontairement simple.

### Sous-onglet "Générer"

Formulaire pour construire un trajet maritime, étape par étape :

- **Navire** et **Année historique** (en haut, valables pour tout le trajet).
- Une carte par **étape**, avec le bouton **"+ Ajouter une étape"** en bas
  pour en ajouter autant que nécessaire, et **"✕ Retirer cette étape"** sur
  chaque carte pour la supprimer. Chaque étape reprend les paramètres du
  fichier Excel :
  - **Région** (liste déroulante, 39 régions du monde du XVIIIe)
  - **Zone maritime** (liste déroulante — met à jour automatiquement les
    valeurs "Dé marchand" / "Dé aventurier" affichées, via la table de
    `donnees_reference.ZONE_DES`)
  - **Taille du port d'escale** (liste déroulante, ou "Aucune (pas d'escale)")
  - **Distance** (milles nautiques), **Chance de rencontre (aventurier)**,
    **Compétence de vigie** — saisie numérique
  - **Escale — recrutement / commerce / réparation** — saisie numérique (0/1)
- Le bouton **"Créer le trajet"** appelle `moteur.creer_trajet(navire, annee,
  etapes)` puis bascule automatiquement sur le sous-onglet "Journal" pour
  montrer le jour 1 du voyage nouvellement créé.

Pour ajuster les listes déroulantes (régions, zones, tailles de port) ou la
table des dés, modifie uniquement `donnees_reference.py` — tout le reste
(formulaire, moteur) s'appuie dessus automatiquement.

## Equipage → Générer

Formulaire (`panneau_generation_equipage.py`) pour créer un équipage :

- **Nom de l'équipage** (texte), **Type** (liste déroulante — valeurs
  uniques de la colonne `Type` de `data/ListeProf.csv`), **Nombre de
  personnes** (saisie numérique).
- Une saisie numérique par typologie : **Calfat, Coq, Charpentier,
  Chirurgien, Pilote, Soldat, Voilier**.
- Le bouton **"Générer l'équipage"** appelle `moteur.generer_equipage(nom,
  type, nombre, effectifs)`, qui enregistre le résultat dans
  `data/Equipage/<nom>.csv` (séparateur `;`, décimal `,`, encodage
  `cp1252`), puis bascule sur "Afficher" pour le montrer immédiatement.

Dans `MoteurExemple`, la ligne CSV générée contient `Nom, Type, Nombre`,
une colonne par typologie saisie, et `Matelot` pour le reste de l'effectif
non affecté à une typologie précise — à adapter selon tes propres règles de
génération (répartition des compétences, etc.).

## Navire → Générer

Formulaire (`panneau_generation_navire.py`) pour créer un navire :

- **Nom du navire** (texte).
- **Type de navire** (liste déroulante — valeurs uniques de la colonne
  `Typologie` de `data/RencontreNavire.csv`).
- **Région d'origine** (liste déroulante — valeurs uniques de la colonne
  `Regions` de `data/ListeRegions.csv`).
- Le bouton **"Générer le navire"** appelle `moteur.generer_navire(nom,
  type, region)`, qui enregistre le résultat dans `data/Navire/<nom>.csv`
  (mêmes séparateur/décimal/encodage), puis bascule sur "Afficher".

Dans `MoteurExemple`, la fiche générée est minimale (`Nom, Type, Region`) —
c'est le bon endroit pour brancher ta vraie génération de navire (coque,
canons, équipage initial...), par exemple en appelant ta classe `Navire`.

Pour ces deux formulaires, si un fichier CSV source ou une colonne
attendue est introuvable, la liste déroulante correspondante reste vide et
un avertissement s'affiche dans le panneau plutôt que de faire planter
l'interface.

## Boutons d'action par onglet vertical

Chaque onglet vertical dispose désormais d'un sous-onglet **"Actions"**
(repris de `ListeFeatures.xlsx`) qui affiche des boutons d'action rapide,
propres au navire (ou à la cale, pour Marchandises) sélectionné :

| Onglet | Actions |
|---|---|
| Navire | Combattre, Poursuite |
| Equipage | Bataille terrestre, Test compétence |
| Marchandises | Vendre à un marchand |
| Escale | Recruter au port, Réparer navire, Trouver marchand, Enquêter |
| Infirmerie | Voir blessé/malade, Sacrifier blessé |
| Reset | Supprimer toutes les données (Navire, Equipage, Escale, Voyage) |

Cette liste vit dans la constante `ACTIONS_PAR_ONGLET` en haut de
`moteur_interface.py` — pour ajouter, renommer ou retirer un bouton, il
suffit de modifier cette constante, rien d'autre à toucher côté interface.

Dans `MoteurExemple`, seule l'action de Reset a une vraie implémentation
(elle réinitialise navires/équipages/voyages à leur état de départ) ; les
autres renvoient un message d'exemple générique — à toi de brancher tes
propres règles dans `executer_action(...)`.

## Brancher ton propre moteur de calcul

1. Crée un fichier, par ex. `mon_moteur.py` :

```python
from moteur_interface import MoteurBase

class MonMoteur(MoteurBase):
    def get_instances(self, onglet, sous_onglet):
        # renvoie la liste des noms à afficher dans la liste déroulante
        ...

    def get_donnees(self, onglet, sous_onglet, instance):
        # renvoie un dict (fiche), une liste de dict (tableau),
        # une chaîne/liste de chaînes (texte), ou None
        ...

    def get_actions(self, onglet, sous_onglet, instance):
        # renvoie la liste des boutons d'action à proposer
        ...

    def executer_action(self, onglet, sous_onglet, instance, action):
        # exécute l'action dans ton moteur, renvoie un message de résultat
        ...
```

2. Dans `main.py`, remplace :

```python
from moteur_interface import MoteurExemple
moteur = MoteurExemple()
```

par :

```python
from mon_moteur import MonMoteur
moteur = MonMoteur()
```

L'interface n'a besoin d'aucune autre modification : elle s'adapte
automatiquement aux données renvoyées par ton moteur.

## Ajouter un nouvel onglet ou sous-onglet

Modifie simplement le dictionnaire `ONGLETS` en haut de `app.py` :

```python
ONGLETS = {
    "Journal de bord": [],
    "Navire": ["Afficher", "Générer"],
    ...
    "Nouvel onglet": ["Sous-onglet A", "Sous-onglet B"],
}
```

Ton moteur recevra alors ces nouveaux noms dans `onglet` / `sous_onglet`.

## Formats de données affichables automatiquement

`get_donnees(...)` peut renvoyer :

- **`dict`** → affiché comme une fiche clé/valeur (ex : caractéristiques d'un navire).
- **`list[dict]`** (mêmes clés) → affiché comme un tableau (ex : liste d'équipage).
- **`str`** ou **`list[str]`** → affiché comme du texte (ex : journal de bord).
- **`None`** → message "aucune donnée".

Aucune configuration supplémentaire n'est nécessaire côté interface.
