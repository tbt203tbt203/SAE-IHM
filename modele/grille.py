import json
from modele.case import Case
from modele.motif import Motif


class Grille:
    """
    Grille de jeu.
    Elle fait le lien entre toutes les cases et les motifs,
    gère les opérations de chargement/sauvegarde et applique les règles du jeu.
    """

    def __init__(self, largeur: int, hauteur: int, motifs: list[Motif]):
        """
        Initialise une nouvelle grille de jeu.

        :param largeur: Le nombre de colonnes de la grille.
        :param hauteur: Le nombre de lignes de la grille.
        :param motifs: La liste des motifs (régions) composant cette grille.
        """
        self.largeur = largeur
        self.hauteur = hauteur
        self.motifs = motifs

        self._cases: dict[tuple[int, int], Case] = {}
        
        for motif in motifs:
            for case in motif.cases:
                self._cases[(case.x, case.y)] = case