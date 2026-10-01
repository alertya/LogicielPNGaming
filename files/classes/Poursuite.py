import math
import matplotlib.pyplot as plt

# --- Paramètres initiaux ---
vent_angle = 0  # direction du vent en degrés (nord)
dt = 1  # intervalle de temps par pas (en minutes)

# vitesses max par allure (facteur de vitesse maximale)
ALLURES = {
    "pres": 0.6,
    "travers": 0.8,
    "largue": 1.0,
    "arriere": 0.5,
}

def deg_to_rad(deg):
    return deg * math.pi / 180

def rad_to_deg(rad):
    return (rad * 180 / math.pi) % 360

def angle_diff(a1, a2):
    d = (a2 - a1 + 180) % 360 - 180
    return abs(d)

def allure_vers_vitesse(angle_au_vent):
    angle = abs(angle_au_vent % 360)
    if angle < 50:
        return ALLURES["pres"]
    elif angle < 100:
        return ALLURES["travers"]
    elif angle < 140:
        return ALLURES["largue"]
    else:
        return ALLURES["arriere"]

def avancer(x, y, cap, vitesse):
    rad = deg_to_rad(cap)
    dx = vitesse * math.cos(rad)
    dy = vitesse * math.sin(rad)
    return x + dx, y + dy

# --- Initialisation des navires ---
poursuivant = {
    "x": 0,
    "y": 0,
    "vitesse_max": 10,  # en noeuds
}

target = {
    "x": 5,
    "y": 15,
    "cap": 30,         # cap constant
    "vitesse": 6        # en noeuds
}

# --- Simulation ---
positions_p = [(poursuivant["x"], poursuivant["y"])]
positions_t = [(target["x"], target["y"])]

dist = lambda: math.hypot(target["x"] - poursuivant["x"], target["y"] - poursuivant["y"])

while dist() > 0.5 or dt <100:
    # 1. Calculer l'angle entre poursuivant et cible
    dx = target["x"] - poursuivant["x"]
    dy = target["y"] - poursuivant["y"]
    angle_vers_cible = rad_to_deg(math.atan2(dy, dx))

    # 2. Calculer angle au vent pour cet angle
    angle_au_vent = angle_diff(vent_angle, angle_vers_cible)

    # 3. Déterminer la meilleure allure possible (en réel : bordé si vent trop de face)
    vitesse_relative = allure_vers_vitesse(angle_au_vent)
    vitesse_effective = poursuivant["vitesse_max"] * vitesse_relative * dt / 60  # conversion minute

    # 4. Avancer le poursuivant vers la cible
    poursuivant["x"], poursuivant["y"] = avancer(poursuivant["x"], poursuivant["y"], angle_vers_cible, vitesse_effective)
    positions_p.append((poursuivant["x"], poursuivant["y"]))

    # 5. Avancer la cible
    vitesse_cible = target["vitesse"] * dt / 60  # conversion
    target["x"], target["y"] = avancer(target["x"], target["y"], target["cap"], vitesse_cible)
    positions_t.append((target["x"], target["y"]))

# --- Affichage ---
xp, yp = zip(*positions_p)
xt, yt = zip(*positions_t)

plt.plot(xp, yp, label="Poursuivant", color="blue")
plt.plot(xt, yt, label="Cible", color="red")
plt.scatter([xp[0]], [yp[0]], label="Départ", marker="o", color="blue")
plt.scatter([xt[0]], [yt[0]], label="Cible initiale", marker="x", color="red")
plt.legend()
plt.axis("equal")
plt.title("Simulation de poursuite maritime")
plt.xlabel("x (milles nautiques)")
plt.ylabel("y (milles nautiques)")
plt.grid(True)
plt.show()
