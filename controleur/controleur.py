import sys
from modele.case import Case
from modele.grille import Grille

# --------------------------------------------------------------------------------
# --- class Controleur
# --------------------------------------------------------------------------------

class Controleur() :
    
    # constructeur 
    def __init__(self) -> None : 
        
        # attributs 
        self.modele = None
        self.vue = None
    
        # signaux de la vue au controleur 
        
        
    def sauvegarder(self, chemin : str) -> None : 
        """Sauvegarde la grille actuelle en JSON"""
        if self.modele : 
            self.modele.sauvegarder(chemin)
                
    def resoudre(self) -> None : 
        """Résout la grille et mettre à jour la vue"""
        if self.modele : 
            self.modele.resoudre()
            # appeler vue !!!!
        
    def reset(self) -> None : 
        """Remet la grille à l'état initial """
        if self.modele : 
            self.modele.reset()
            # appeler vue !!!!
        
    def changer_grille(self, chemin : str) -> None : 
        """Charge une autre grille depuis un fichier JSON"""
        self.modele = Grille.depuis_json(chemin)
        # appeler vue !!!!
        
    # à modifier plus tard pour la gestion d'erreur
    def remplir(self, case : Case, valeur : int) -> None : 
        """Mettre une valeur dans une case"""
        if self.modele : 
            try : 
                self.modele.poser_valeur(case.x, case.y, valeur)
                # appeler vue !!!!
                return True
            except ValueError : 
                return False
        return False
        
    def supprimer(self, case : Case) -> None :
        """Effacer une valeur dans une case"""
        if self.modele : 
            self.modele.effacer_valeur(case.x, case.y)
            # appeler vue !!!!