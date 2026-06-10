from modele.case import Case


class Motif:
    """
    Représente un motif de la grille de jeu.
    Un motif est une zone délimitée contenant un groupe de cases.
    Un motif de taille N doit contenir exactement tous les chiffres de 1 à N.
    """

    def __init__(self, nom: str, cases: list[Case]):
        """
        Initialise un nouveau motif.

        :param nom: Identifiant ou nom unique du motif
        :param cases: Liste des objets Case qui composent ce motif
        """
        self.nom = nom
        self.cases = cases

    @property
    def taille(self) -> int:
        """
        Calcule le nombre de cases qui composent ce motif.

        :return: Nombre de cases du motif.
        """
        return len(self.cases)

    def valeurs_utilisees(self) -> set[int]:
        """
        Détermine l'ensemble des valeurs non nulles (déjà jouées) au sein de ce motif.
        Les cases vides (valeur = 0) sont ignorées.

        :return: Un ensemble (set) contenant les chiffres déjà posés.
        """
        # On extrait les valeurs des cases du motif en excluant les cases vides (0)
        chiffres_poses = set()
        
        for case in self.cases:
            if not case.est_vide():
                chiffres_poses.add(case.valeur)
                
        return chiffres_poses

    def est_valide(self) -> bool:
        """
        Vérifie si le motif respecte les contraintes de validité (sans doublons).
        Les valeurs doivent également toutes être comprises entre 1 et la taille du motif.
        Les cases vides sont ignorées lors de cette validation partielle.

        :return: True si le motif ne contient aucun doublon ni valeur hors limites, False sinon.
        """
        # Récupération de toutes les valeurs non nulles
        valeurs = []
        for case in self.cases:
            if not case.est_vide():
                valeurs.append(case.valeur)

        # Vérification 1 : Absence de doublons
        # Si la longueur de la liste est différente de la taille du set, il y a un doublon
        sans_doublon = (len(valeurs) == len(set(valeurs)))

        # Vérification 2 : Valeurs autorisées entre 1 et N (taille du motif)
        valeurs_correctes = True
        for v in valeurs:
            if not (1 <= v <= self.taille):
                valeurs_correctes = False
                break

        return sans_doublon and valeurs_correctes

    def est_complet(self) -> bool:
        """
        Vérifie si le motif est entièrement et correctement rempli.
        Il doit contenir exactement tous les chiffres de 1 à N (taille du motif).

        :return: True si le motif est complet et correct, False sinon.
        """
        # Récupération et tri de toutes les valeurs des cases du motif
        valeurs = []
        for case in self.cases:
            valeurs.append(case.valeur)
        
        valeurs_triees = sorted(valeurs)

        # Création de la liste attendue : [1, 2, ..., N]
        sequence_attendue = list(range(1, self.taille + 1))

        return valeurs_triees == sequence_attendue

    def __repr__(self) -> str:
        """
        Représentation textuelle du motif.
        """
        return f"Motif(nom='{self.nom}', cases_comptees={self.taille})"

