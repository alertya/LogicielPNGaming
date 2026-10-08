"""
main.py
-------
Point d'entrée de l'application.

Pour brancher TON moteur de calcul :
    1. Crée ton propre module (ex: mon_moteur.py) avec une classe
       héritant de `MoteurBase` (voir moteur_interface.py pour le contrat
       à respecter : get_instances / get_donnees / get_actions / executer_action).
    2. Remplace l'import et l'instanciation ci-dessous.

Tant que tu n'as pas encore de moteur, ce fichier utilise `MoteurExemple`
(données factices) pour que tu puisses lancer et tester l'interface
immédiatement avec : python main.py
"""
print()
from app import App

from moteur_interface import MoteurExemple

import config
# ---------------------------------------------------------------------
# ⬇  Remplace cette ligne par ton propre moteur quand il sera prêt :
#
#     from mon_moteur import MonMoteur
#     moteur = MonMoteur()
# ---------------------------------------------------------------------

moteur = MoteurExemple()
if __name__ == "__main__":
    print("Calcul generation interface moteur-graphisme")
    app = App(moteur)
    print("Affichage écran")
    app.mainloop()




