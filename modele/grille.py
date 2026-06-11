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
                
                
                
    # ================================================================== #
    # Chargement / Sauvegarde
    # ================================================================== #

    @classmethod
    def depuis_json(cls, chemin: str) -> "Grille":
        """
        Charge une grille de jeu à partir d'un fichier JSON.
        Le format attendu est : { "NomDuMotif": [[x, y, valeur], ...] }

        :param chemin: Le chemin vers le fichier JSON à charger.
        :return: Une instance de la classe Grille correspondante.
        """
        # Lecture du fichier JSON
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)

        motifs = []
        max_x = 0
        max_y = 0

        # Pour chaque motif défini dans le fichier JSON
        for nom, cellules in data.items():
            cases = []
            
            # Pour chaque cellule du motif, on crée l'objet Case correspondant
            for cell in cellules:
                x, y, valeur = cell
                cases.append(Case(x, y, valeur))
                
                # Mise à jour des dimensions maximales pour dimensionner la grille
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                
            # Création du motif et ajout à la liste
            motifs.append(Motif(nom, cases))

        # La largeur et la hauteur sont déduites des coordonnées maximales (+ 1 car indexation à 0)
        largeur_grille = max_x + 1
        hauteur_grille = max_y + 1

        return cls(largeur_grille, hauteur_grille, motifs)

    def sauvegarder(self, chemin: str) -> None:
        """
        Sauvegarde l'état actuel de la grille dans un fichier JSON.

        :param chemin: Le chemin vers le fichier JSON de destination.
        """
        # Reconstruction de la structure de données attendue
        data = {}
        for motif in self.motifs:
            cellules_motif = []
            for c in motif.cases:
                cellules_motif.append([c.x, c.y, c.valeur])
            data[motif.nom] = cellules_motif

        # Écriture dans le fichier
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    # ================================================================== #
    # Accès aux cases
    # ================================================================== #

    def get_case(self, x: int, y: int) -> Case | None:
        """
        Récupère la case située aux coordonnées (x, y).

        :param x: L'indice de colonne.
        :param y: L'indice de ligne.
        :return: L'objet Case correspondant, ou None si les coordonnées sont hors limites.
        """
        return self._cases.get((x, y))

    def get_voisins(self, x: int, y: int) -> list[Case]:
        """
        Retourne la liste des cases adjacentes à la position (x, y)
        en incluant les 8 directions (haut, bas, gauche, droite et diagonales).

        :param x: La coordonnée x de la case centrale.
        :param y: La coordonnée y de la case centrale.
        :return: Une liste de cases voisines existantes.
        """
        voisins = []
        
        # Parcours des décalages possibles sur X et Y (-1, 0, 1)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                # Ignore la case centrale
                if dx == 0 and dy == 0:
                    continue
                
                # Récupération de la case voisine si elle existe dans la grille
                case_voisine = self.get_case(x + dx, y + dy)
                if case_voisine:
                    voisins.append(case_voisine)
                    
        return voisins

    def motif_de(self, x: int, y: int) -> Motif | None:
        """
        Recherche et retourne le motif auquel appartient la case aux coordonnées (x, y).

        :param x: La coordonnée x de la case recherchée.
        :param y: La coordonnée y de la case recherchée.
        :return: L'objet Motif associé, ou None si non trouvé.
        """
        for motif in self.motifs:
            for case in motif.cases:
                if case.x == x and case.y == y:
                    return motif
        return None