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

    def sauvegarder(self, chemin: str, nom_fichier_original : str = "") -> None:
        """
        Sauvegarde l'état actuel de la grille dans un fichier JSON.

        :param chemin: Le chemin vers le fichier JSON de destination.
        """
        # Reconstruction de la structure de données attendue
        data = {
            "grille_originale" : nom_fichier_original,
            "coups_joueur": []
        }
        for motif in self.motifs:
            for c in motif.cases:
                # On ne sauvegarde  que les cases remplies par le joueur
                if not c.fixe and not c.est_vide():
                    data["coups_joueur"].append([c.x, c.y, c.valeur])

        # Écriture dans le fichier
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def reset(self) -> None:
        """
        Remet toutes les cases non fixes de la grille à leur état initial (vide, valeur 0).
        Les indices de départ (cases fixes) ne sont pas modifiés.
        """
        for case in self._cases.values():
            if not case.fixe:
                case._valeur = 0

    # def charger_sauvegarde(self, chemin_sauvegarde: str) -> None:
    #     """
    #     Charge un fichier de sauvegarde par-dessus la grille actuelle.
    #     Seules les cases non fixes reçoivent les valeurs enregistrées.
    #     Le fichier JSON doit respecter le format standard de grille.

    #     :param chemin_sauvegarde: Le chemin du fichier JSON de sauvegarde.
    #     """
    #     with open(chemin_sauvegarde, "r", encoding="utf-8") as f:
    #         data = json.load(f)

    #     # Parcours de chaque motif et des cellules enregistrées dans la sauvegarde
    #     for nom_motif, cellules in data.items():
    #         for cell in cellules:
    #             x, y, valeur = cell
    #             case = self.get_case(x, y)
                
    #             # On met à jour la valeur uniquement si la case existe et n'est pas fixe
    #             if case and not case.fixe:
    #                 case.valeur = valeur

            
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
    
    # ================================================================== #
    # Validation des règles du jeu
    # ================================================================== #

    def voisinage_valide(self, x: int, y: int) -> bool:
        """
        Vérifie la règle de voisinage pour la case (x, y).
        La valeur de cette case ne doit pas se retrouver dans ses 8 voisins directs.
        Si la case est vide, elle est considérée valide.

        :param x: La coordonnée x de la case à vérifier.
        :param y: La coordonnée y de la case à vérifier.
        :return: True si aucun problème de valeur n'est détecté avec les voisins, False sinon.
        """
        case = self.get_case(x, y)
        if not case or case.est_vide():
            return True

        # Récupération de l'ensemble des valeurs des voisins non vides
        valeurs_voisins = set()
        for v in self.get_voisins(x, y):
            if not v.est_vide():
                valeurs_voisins.add(v.valeur)

        # La règle est respectée si la valeur de la case n'est pas dans le set des voisins
        return case.valeur not in valeurs_voisins

    def est_valide(self) -> bool:
        """
        Vérifie si toutes les règles du jeu sont respectées sur l'ensemble de la grille.
        Contrôle la règle de voisinage pour chaque case et la validité de chaque motif.

        :return: True si la grille entière respecte les règles, False sinon.
        """
        # 1. Vérification de la règle de voisinage pour toutes les cases
        for (x, y) in self._cases:
            if not self.voisinage_valide(x, y):
                return False

        # 2. Vérification que chaque motif n'a pas de doublons ou de valeurs invalides
        tous_les_motifs_valides = all(m.est_valide() for m in self.motifs)
        
        return tous_les_motifs_valides



    def est_complete(self) -> bool:
        """
        Indique si la grille est entièrement remplie, valide et résolue.
        
        :return: True si toutes les cases sont remplies et la grille est valide, False sinon.
        """
        # Toutes les cases doivent être non vides
        toutes_remplies = all(not c.est_vide() for c in self._cases.values())
        
        # Tous les motifs doivent contenir exactement la séquence de 1 à N
        tous_motifs_complets = all(m.est_complet() for m in self.motifs)
        
        # La grille globale doit respecter les règles de voisinage
        grille_valide = self.est_valide()

        return toutes_remplies and tous_motifs_complets and grille_valide
    
    

    def valeur_valide_pour(self, x: int, y: int, valeur: int) -> bool:
        """
        Vérifie si `valeur` peut être posée en (x, y) sans créer de conflit
        (ni avec les 8 voisins, ni avec les autres cases du même motif).

        :param x: La coordonnée x de la case visée.
        :param y: La coordonnée y de la case visée.
        :param valeur: La valeur que l'on souhaite tester.
        :return: True si aucun conflit n'est détecté, False sinon.
        """
        # Conflit avec une autre case du même motif
        motif = self.motif_de(x, y)
        if motif:
            autres_valeurs = {
                c.valeur for c in motif.cases
                if (c.x, c.y) != (x, y) and not c.est_vide()
            }
            if valeur in autres_valeurs:
                return False

        # Conflit avec un voisin
        valeurs_voisins = {v.valeur for v in self.get_voisins(x, y) if not v.est_vide()}
        return valeur not in valeurs_voisins




    def cases_invalides(self) -> set[tuple[int, int]]:
        """
        Détermine les coordonnées de toutes les cases en conflit
        (voisinage identique ou doublon dans un motif).

        :return: Un ensemble de tuples (x, y) des cases en conflit.
        """
        invalides = set()

        #  Chiffre hors limite dans le motif
        for motif in self.motifs:
            for c in motif.cases:
                if not c.est_vide() and c.valeur > motif.taille:
                    invalides.add((c.x, c.y))
                    
        # Conflits de voisinage
        for (x, y), case in self._cases.items():
            if not case.est_vide() and not self.voisinage_valide(x, y):
                invalides.add((x, y))

        # Doublons au sein d'un même motif
        for motif in self.motifs:
            valeurs_vues: dict[int, tuple[int, int]] = {}
            for c in motif.cases:
                if c.est_vide():
                    continue
                if c.valeur in valeurs_vues:
                    invalides.add((c.x, c.y))
                    invalides.add(valeurs_vues[c.valeur])
                else:
                    valeurs_vues[c.valeur] = (c.x, c.y)

        return invalides

    # ================================================================== #
    # Actions du joueur
    # ================================================================== #

    def poser_valeur(self, x: int, y: int, valeur: int, strict: bool = False) -> None:
        """
        Permet à un joueur de poser une valeur dans une case spécifique.

        Lève une erreur si :
        - la case n'existe pas
        - la case est fixe (donnée du puzzle)
        - valeur n'est pas un entier
        - valeur n'est pas compris entre 1 et la taille du motif (N)
        - strict=True et valeur viole la règle de voisinage ou de motif

        :param x: La coordonnée x de la case.
        :param y: La coordonnée y de la case.
        :param valeur: La valeur entière à attribuer à la case.
        :param strict: Si True, refuse la pose en cas de conflit avec un voisin ou le motif.
        """
        case = self.get_case(x, y)
        if case is None:
            raise ValueError(f"La case ({x},{y}) n'existe pas dans la grille.")

        if not isinstance(valeur, int):
            raise TypeError(f"La valeur doit être un entier, reçu : {valeur!r}")

        # motif = self.motif_de(x, y)
        # taille = motif.taille if motif else max(self.largeur, self.hauteur)
        # if not (1 <= valeur <= taille):
        #     raise ValueError(f"La valeur doit être comprise entre 1 et {taille} pour cette case.")

        if strict and not self.valeur_valide_pour(x, y, valeur):
            raise ValueError(f"La valeur {valeur} entre en conflit avec un voisin ou le motif.")

        case.valeur = valeur  # lève ValueError si la case est fixe

    def effacer_valeur(self, x: int, y: int) -> None:
        """
        Efface la valeur d'une case si celle-ci n'est pas une case fixe.

        :param x: La coordonnée x de la case.
        :param y: La coordonnée y de la case.
        """
        case = self.get_case(x, y)
        if case and not case.fixe:
            case._valeur = 0



    # ------------------------------------------------------------------ #
    # Résolution par backtracking
    # ------------------------------------------------------------------ #

    def resoudre(self) -> bool:
        """Lance le solveur. Retourne True si une solution a été trouvée."""
        vides = [c for c in self._cases.values() if c.est_vide()]
        return self._backtrack(vides, 0)

    def _backtrack(self, vides: list[Case], index: int) -> bool:
        if index == len(vides):
            return True

        case = vides[index]
        motif = self.motif_de(case.x, case.y)
        taille = motif.taille if motif else max(self.largeur, self.hauteur)
        
        utilisees_motif = {c.valeur for c in motif.cases
                           if c.valeur != 0 and (c.x, c.y) != (case.x, case.y)}
        
        valeurs_voisins = {v.valeur for v in self.get_voisins(case.x, case.y) if not v.est_vide()}

        for valeur in range(1, taille + 1):
            if valeur in utilisees_motif:
                continue
            if valeur in valeurs_voisins:
                continue

            case._valeur = valeur  
            if self._backtrack(vides, index + 1):
                return True
            case._valeur = 0

        return False

    def __repr__(self) -> str:
        return f"Grille({self.largeur}x{self.hauteur}, {len(self.motifs)} motifs)"
    
    def resoudreTest(self) -> bool : 
        """Resoudre une grille en inspirant de la coloration du graphe"""
                    
        vides = [c for c in self._cases.values() if c.est_vide()]
        vides.sort(key=lambda c: len(self.get_voisins(c.x, c.y)), reverse=True)
        
        return self._backtrack(vides, 0)
    
    def construire_graphe(self) -> dict : 
        """Construit le graphe d'adjacence de la grille"""
        graphe = {}
        for (x, y) in self._cases : 
            graphe[(x, y)] = [
                (v.x, v.y) for v in self.get_voisins(x, y)
            ]
        return graphe

    def trier_par_degre(self, graphe : dict) -> list :
        """Trie les cases vides par nombre de voisins de décroissant"""
        vides = [c for c in self._cases.values() if c.est_vide()]
        return sorted(vides, 
                     key=lambda c: len(graphe[(c.x, c.y)]),
                        reverse=True)
           
    def resoudre_coloration(self) -> bool :
        """Résout la grille en utilisant l'ordre coloration"""
        graphe = self.construire_graphe()
        vides = self.trier_par_degre(graphe)
        return self._backtrack(vides, 0)