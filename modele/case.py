class Case:
    """Une cellule de la grille, identifiée par ses coordonnées (x, y)."""

    def __init__(self, x: int, y: int, valeur: int = 0):
        self.x = x
        self.y = y
        self._valeur = valeur
        self.fixe = valeur != 0  # case pré-remplie par le puzzle, non modifiable

    @property
    def valeur(self) -> int:
        return self._valeur

    @valeur.setter
    def valeur(self, v: int):
        if self.fixe:
            raise ValueError(f"La case ({self.x},{self.y}) est fixe et ne peut pas être modifiée")
        self._valeur = v

    def est_vide(self) -> bool:
        return self._valeur == 0

    def __repr__(self) -> str:
        marqueur = "*" if self.fixe else ""
        return f"Case({self.x},{self.y},{self._valeur}{marqueur})"
