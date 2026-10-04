import tkinter as tk
from PIL import Image, ImageTk
import math


class CarteHex(tk.Canvas):

    def __init__(self, parent, rayon=40, largeur=15, hauteur=15):
        super().__init__(
            parent,
            width=1000,
            height=700,
            bg="#6EB5FF",
            highlightthickness=0
        )

        self.pack(fill="both", expand=True)

        self.rayon = rayon
        self.largeur = largeur
        self.hauteur = hauteur

        self.centre_x = 500
        self.centre_y = 350

        self.tokens = {}

        self.dessiner_grille()

    # ----------------------------------------------------
    # Conversion Hex -> Pixel
    # ----------------------------------------------------

    def hex_vers_pixel(self, q, r):

        x = self.centre_x + self.rayon * math.sqrt(3) * (q + r / 2)
        y = self.centre_y + self.rayon * 1.5 * r

        return x, y

    # ----------------------------------------------------
    # Conversion Pixel -> Hex (approximation)
    # ----------------------------------------------------

    def pixel_vers_hex(self, x, y):

        x -= self.centre_x
        y -= self.centre_y

        q = (math.sqrt(3) / 3 * x - 1 / 3 * y) / self.rayon
        r = (2 / 3 * y) / self.rayon

        return round(q), round(r)

    # ----------------------------------------------------
    # Dessin d'un hexagone
    # ----------------------------------------------------

    def dessiner_hexagone(self, cx, cy):

        points = []

        for i in range(6):

            angle = math.radians(60 * i - 30)

            px = cx + self.rayon * math.cos(angle)
            py = cy + self.rayon * math.sin(angle)

            points.extend((px, py))

        self.create_polygon(
            points,
            outline="black",
            fill="#A8D5A2"
        )

    # ----------------------------------------------------
    # Dessin de la grille
    # ----------------------------------------------------

    def dessiner_grille(self):

        for q in range(-self.largeur, self.largeur + 1):

            for r in range(-self.hauteur, self.hauteur + 1):

                x, y = self.hex_vers_pixel(q, r)

                self.dessiner_hexagone(x, y)

    # ----------------------------------------------------
    # Ajout d'un navire
    # ----------------------------------------------------


    # ----------------------------------------------------
    # Rotation
    # ----------------------------------------------------

    def tourner_navire(self, nom, direction):

        token = self.tokens[nom]

        token["direction"] = direction

        image = token["image"].rotate(
            direction * 60,
            expand=True
        )

        token["photo"] = ImageTk.PhotoImage(image)

        self.itemconfigure(
            token["item"],
            image=token["photo"]
        )

    # ----------------------------------------------------
    # Début drag
    # ----------------------------------------------------

    def debut_drag(self, event, nom):

        self.drag_x = event.x
        self.drag_y = event.y

    # ----------------------------------------------------
    # Drag
    # ----------------------------------------------------

    def drag(self, event, nom):

        dx = event.x - self.drag_x
        dy = event.y - self.drag_y

        self.move(
            self.tokens[nom]["item"],
            dx,
            dy
        )

        self.drag_x = event.x
        self.drag_y = event.y

    # ----------------------------------------------------
    # Fin drag
    # ----------------------------------------------------

    def fin_drag(self, event, nom):

        q, r = self.pixel_vers_hex(event.x, event.y)

        self.tokens[nom]["q"] = q
        self.tokens[nom]["r"] = r

        x, y = self.hex_vers_pixel(q, r)

        self.coords(
            self.tokens[nom]["item"],
            x,
            y
        )


###########################################################
# Fenêtre de démonstration
###########################################################

class FenetreCourse(tk.Tk):

    def __init__(self):

        super().__init__()

        self.geometry("1000x800")

        self.title("Course Poursuite")

        self.carte = CarteHex(self)

        # poursuivant au centre
        self.carte.ajouter_navire(
            "Poursuivant",
            "navire.png",
            0,
            0
        )

        # poursuivi à Dx=3 Dy=-2
        self.carte.ajouter_navire(
            "Poursuivi",
            "navire.png",
            3,
            -2
        )

        self.carte.tourner_navire(
            "Poursuivant",
            2
        )

        self.carte.tourner_navire(
            "Poursuivi",
            5
        )

    def dessiner_navire(self, nom, q, r, direction, couleur="red"):
        x, y = self.hex_vers_pixel(q, r)

        angle = math.radians(direction * 60 - 90)

        longueur = self.rayon * 0.8

        x2 = x + longueur * math.cos(angle)
        y2 = y + longueur * math.sin(angle)

        item = self.create_line(
            x,
            y,
            x2,
            y2,
            width=4,
            fill=couleur,
            arrow=tk.LAST
        )

        self.tokens[nom] = {
            "item": item,
            "q": q,
            "r": r,
            "direction": direction
        }

    def tourner_navire(self, nom, direction):
        token = self.tokens[nom]

        token["direction"] = direction

        x, y = self.hex_vers_pixel(token["q"], token["r"])

        angle = math.radians(direction * 60 - 90)

        longueur = self.rayon * 0.8

        x2 = x + longueur * math.cos(angle)
        y2 = y + longueur * math.sin(angle)

        self.coords(
            token["item"],
            x, y,
            x2, y2
        )

    def deplacer_navire(self, nom, q, r):
        self.tokens[nom]["q"] = q
        self.tokens[nom]["r"] = r

        self.tourner_navire(
            nom,
            self.tokens[nom]["direction"]
        )

    def ajouter_navire(self, nom, q, r, direction=0, couleur="red"):
        x, y = self.hex_vers_pixel(q, r)

        angle = math.radians(direction * 60 - 90)
        longueur = self.rayon * 0.8

        x2 = x + longueur * math.cos(angle)
        y2 = y + longueur * math.sin(angle)

        item = self.create_line(
            x,
            y,
            x2,
            y2,
            width=4,
            fill=couleur,
            arrow=tk.LAST
        )

        self.tokens[nom] = {
            "item": item,
            "q": q,
            "r": r,
            "direction": direction
        }

if __name__ == "__main__":

    app = FenetreCourse()

    app.mainloop()