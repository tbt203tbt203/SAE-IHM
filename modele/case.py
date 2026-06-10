class Case:
    """
    Représente une case individuelle de la grille de jeu.
    Chaque case est identifiée par ses coordonnées (x, y).
    """

    def __init__(self, x: int, y: int, valeur: int = 0):
        """
        Initialise une nouvelle case.

        :param x: La coordonnée horizontale (colonne) de la case.
        :param y: La coordonnée verticale (ligne) de la case.
        :param valeur: La valeur initiale de la case (0 signifie que la case est vide).
        """
        # Position de la case dans la grille
        self.x = x
        self.y = y
        self._valeur = valeur
        self.fixe = (valeur != 0)  # case pré-remplie par le puzzle, non modifiable

    @property
    def valeur(self) -> int:
        """
        Getter pour accéder à la valeur actuelle de la case.
        
        :return: L'entier contenu dans la case.
        """
        return self._valeur

    @valeur.setter
    def valeur(self, v: int):
        """
        Setter pour modifier la valeur de la case.
        Lève une erreur si on tente de modifier une case fixe définie par défaut.

        :param nouvelle_valeur: Le nouveau chiffre à placer dans la case.
        """
        if self.fixe:
            raise ValueError(f"La case ({self.x},{self.y}) est fixe et ne peut pas être modifiée")
        self._valeur = v

    def est_vide(self) -> bool:
        """
        Indique si la case est actuellement vide (valeur égale à 0).

        :return: True si la case est vide, False sinon.
        """
        return self._valeur == 0

    def __repr__(self) -> str:
        """
        Représentation textuelle de la case pour faciliter le débogage.
        Les cases fixes sont signalées par un astérisque (*).
        """
        marqueur_fixe = "*" if self.fixe else ""
        return f"Case(x={self.x}, y={self.y}, valeur={self._valeur}{marqueur_fixe})"
