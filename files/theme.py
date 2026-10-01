"""
theme.py
--------
Constantes visuelles pour donner à l'interface une ambiance
"jeu vidéo de gestion" (capitainerie / navire marchand).

Modifie librement ces valeurs pour changer l'ambiance graphique
sans toucher au reste du code.
"""

# --- Couleurs générales ---------------------------------------------------
BG_ROOT = "#14100a"          # fond général de la fenêtre
BG_SIDEBAR = "#1d160d"       # fond de la colonne des onglets verticaux
BG_TOPBAR = "#241b10"        # fond de la barre des onglets horizontaux
BG_PANEL = "#2a2013"         # fond des panneaux de contenu
BG_INPUT = "#332612"         # fond des champs / listes déroulantes

FG_TEXT = "#f1e6c8"          # texte principal (parchemin clair)
FG_MUTED = "#b8a97e"         # texte secondaire
FG_TITLE = "#e8c874"         # titres / accents dorés

ACCENT = "#c9a227"           # doré, couleur d'accent principale
ACCENT_HOVER = "#e6bf3d"
ACCENT_ACTIVE = "#9c7c1d"

TAB_SELECTED_BG = "#3a2c14"
TAB_SELECTED_FG = "#f7e7ab"
TAB_IDLE_BG = "#1d160d"
TAB_IDLE_FG = "#c9bb92"

BORDER = "#4a3a1e"

SUCCESS = "#6fae4f"
ERROR = "#b3452e"

# --- Polices ----------------------------------------------------------------
FONT_TITLE = ("Georgia", 18, "bold")
FONT_SECTION = ("Georgia", 13, "bold")
FONT_TAB_V = ("Georgia", 12, "bold")
FONT_TAB_H = ("Georgia", 11)
FONT_TEXT = ("Georgia", 10)
FONT_TEXT_BOLD = ("Georgia", 10, "bold")
FONT_MONO = ("Consolas", 10)

# --- Dimensions ---------------------------------------------------------------
SIDEBAR_WIDTH = 190
TOPBAR_HEIGHT = 46
INSTANCE_BAR_HEIGHT = 44
