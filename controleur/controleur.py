import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modele.case import Case
from modele.grille import Grille
from vue.vue import VueNeonaure
from PyQt6.QtWidgets import QApplication

# --------------------------------------------------------------------------------
# --- class Controleur
# --------------------------------------------------------------------------------

class Controleur() :
    
    # constructeur 
    #def __init__(self) -> None : 
        
        # attributs 
        #self.modele = None
        #self.vue = None
        
    def __init__(self, chemin_json: str) -> None:
        self.modele = Grille.depuis_json(chemin_json)
        appartenance = {(c.x, c.y): m.nom for m in self.modele.motifs for c in m.cases}
        valeurs = {(c.x, c.y): c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
        self.vue = VueNeonaure(appartenance, valeurs)
    
        # signaux de la vue au controleur 
        self.vue.sauvegarderClicked.connect(self.sauvegarder)
        #self.vue.resoudreClicked.connect(self.resoudre)
        #self.vue.resetClicked.connect(self.reset)
        #self.vue.changerGrilleClicked.connect(self.changer_grille)
        #self.vue.remplirClicked.connect(self.remplir)
        #self.vue.supprimerClicked.connect(self.supprimer)
        #self.vue.chargerSauvegarderClicked.connect(self.chargerSauvegarder)
        
        # self.vue.niveauClicked.connect(self.niveau)
        
        
    """def sauvegarder(self, chemin : str) -> None : 
        if self.modele and chemin :
            self.modele.sauvegarder(chemin)"""
           
           
    def sauvegarder(self) -> None:
        from PyQt6.QtWidgets import QFileDialog
        chemin, _ = QFileDialog.getSaveFileName(self.vue, "Sauvegarder", "", "JSON (*.json)")
        if self.modele and chemin:
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
            
    def chargerSauvegarder(self, chemin : str) -> None : 
        """Charger un fichier JSON depuis le fichier sauvegarder"""
        if self.modele : 
            self.modele.charger_sauvegarde(chemin)
            # appeler vue !!!!
            
            
    # def niveau(self, niveau : int) -> None :
    #     """Choisir un niveau"""
    #     if self.modele : 
    #         self.modele.
    
# -------------------------------------------------------------------------- #
# --- Main YAY!! : test du controleur
# -------------------------------------------------------------------------- #
# if __name__ == "__main__" :
    
#     print("TEST : class controleur")
    
#     app = QApplication(sys.argv)
    
#     control = Controleur()
    
#     sys.exit(app.exec())