import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modele.case import Case
from modele.grille import Grille
from vue.vue import VueNeonaure, VueGrilleAvecSaisie
from PyQt6.QtWidgets import QApplication, QFileDialog

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
        self.vue.resoudreClicked.connect(self.resoudre)
        self.vue.resetClicked.connect(self.reset)
        self.vue.changerGrilleClicked.connect(self.changer_grille)
        self.vue.chargerSauvegarderClicked.connect(self.chargerSauvegarder)
        self.vue.grille.caseModifiee.connect(self.modifierCase)
        self.vue.supprimerClicked.connect(self.supprimer)
        # self.vue.niveauClicked.connect(self.niveau)
           
           
    def sauvegarder(self) -> None:
        """Sauvegarder la grille dans le dossier sauvegarder"""
        chemin, _ = QFileDialog.getSaveFileName(self.vue, "Sauvegarder", os.path.join(sys.path[0], "sauvegarder"), "JSON (*.json)")
        if self.modele and chemin:
            self.modele.sauvegarder(chemin)
            
                            
    def resoudre(self) -> None : 
        """Résout la grille et mettre à jour la vue"""
        if self.modele : 
            self.modele.resoudre()
            valeurs = {(c.x, c.y): c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
            self.vue.mettre_a_jour(valeurs)
        
        
    def reset(self) -> None:
        """Reset la grille"""
        if self.modele:
            self.modele.reset()
            valeurs = {(c.x, c.y): c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
            self.vue.mettre_a_jour(valeurs)
            
        
    def changer_grille(self) -> None : 
        """Charge une autre grille depuis le dossier Annexes"""
        chemin, _ = QFileDialog.getOpenFileName(self.vue, "Charger", os.path.join(sys.path[0], "Annexes"), "JSON (*.json)")
        if chemin : 
            self.modele = Grille.depuis_json(chemin)
            appartenance = {(c.x, c.y) : m.nom for m in self.modele.motifs for c in m.cases}
            valeurs = {(c.x, c.y) : c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
            
            self.vue.grille.caseModifiee.disconnect(self.modifierCase)
            self.vue.grille = VueGrilleAvecSaisie(appartenance, valeurs)
            self.vue.setCentralWidget(self.vue.grille)
            self.vue.grille.caseModifiee.connect(self.modifierCase)
        
        
    def modifierCase(self, x: int, y: int, texte: str) -> None:
        """Remplir ou Éffacer une case"""
        if self.modele : 
            if texte == "" :
                self.modele.effacer_valeur(x, y)
            elif texte.isdigit() :
                try : 
                    self.modele.poser_valeur(x, y, int(texte))
                except ValueError : 
                    pass
                
            valide = self.modele.voisinage_valide(x, y)
            self.vue.colorier_case(x, y, valide)
        
            
    # def chargerSauvegarder(self) -> None:
    #     """Charger un fichier depuis le dossier sauvegarder"""
    #     chemin, _ = QFileDialog.getOpenFileName(self.vue, "Charger", os.path.join(sys.path[0], "sauvegarder"), "JSON (*.json)")
    #     if chemin : 
    #         self.modele = Grille.charger_sauvegarde(chemin)
    #         appartenance = {(c.x, c.y) : m.nom for m in self.modele.motifs for c in m.cases}
    #         valeurs = {(c.x, c.y) : c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
            
    #         self.vue.grille.caseModifiee.disconnect(self.modifierCase)
    #         self.vue.grille = VueGrilleAvecSaisie(appartenance, valeurs)
    #         self.vue.setCentralWidget(self.vue.grille)
    #         self.vue.grille.caseModifiee.connect(self.modifierCase)
            
            
    def chargerSauvegarder(self) -> None:
        """Charger une sauvegarde (progression) sur la grille en cours"""
        chemin, _ = QFileDialog.getOpenFileName(self.vue, "Charger", os.path.join(sys.path[0], "sauvegarder"), "JSON (*.json)")
        if self.modele and chemin:
            self.modele.charger_sauvegarde(chemin)
            valeurs = {(c.x, c.y): c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
            self.vue.mettre_a_jour(valeurs)
            
            
    def supprimer(self) -> None :
        """Supprimer un fichier dans le dossier sauvegarder"""
        chemin, _ = QFileDialog.getOpenFileName(self.vue, "Supprimer", os.path.join(sys.path[0], "sauvegarder"), "JSON (*.json)")
        if chemin : 
            os.remove(chemin)
        
        
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