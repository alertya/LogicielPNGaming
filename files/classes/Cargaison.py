class Cargaison:

    def __init__(
        self,
        nom,
        region,
        volume,
        prix_penurie,
        prix_normal,
        prix_exces,
        densite,
        tonnage,
        mod_richesse_normal,
        mod_richesse_port,
        bonus_richesse_normal,
        bonus_richesse_port,
        id
    ):

        self.Cargaison = nom
        self.Region = region
        self.Volume = volume
        self.PrixPenurie = prix_penurie
        self.PrixNormal = prix_normal
        self.PrixExces = prix_exces
        self.Densite = densite
        self.Tonnage = tonnage
        self.ModRichesseNormal = mod_richesse_normal
        self.ModRichessePort = mod_richesse_port
        self.BonusRichesseNormal = bonus_richesse_normal
        self.BonusRichessePort = bonus_richesse_port
        self.ID = id