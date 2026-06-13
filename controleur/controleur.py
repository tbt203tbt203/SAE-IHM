import os, sys, json
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
        self.fichier_original = os.path.basename(chemin_json)
        self.modele = Grille.depuis_json(chemin_json)
        self._nom_grille = os.path.basename(chemin_json)  #titre
        appartenance = {(c.x, c.y): m.nom for m in self.modele.motifs for c in m.cases}
        valeurs = {(c.x, c.y): c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
        self.vue = VueNeonaure(appartenance, valeurs)
        self.vue.set_titre(self._nom_grille)          #titre
    
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
            self.modele.sauvegarder(chemin, self.fichier_original)
            
                            
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
            self._nom_grille = os.path.basename(chemin)  #titre
            self.vue.set_titre(self._nom_grille)          #titre
            self.fichier_original = os.path.basename(chemin)
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
            elif texte.isdigit() and int(texte) !=0:
                try : 
                    self.modele.poser_valeur(x, y, int(texte))
                except ValueError : 
                    return
                
            invalides = self.modele.cases_invalides()

            self.vue.colorier_case(x, y, (x, y) not in invalides)
            
            for voisin in self.modele.get_voisins(x, y):
                self.vue.colorier_case(voisin.x, voisin.y, (voisin.x, voisin.y) not in invalides)

            motif = self.modele.motif_de(x, y)
            if motif:
                for case in motif.cases:
                    self.vue.colorier_case(case.x, case.y, (case.x, case.y) not in invalides)
            
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
            
            
    # def chargerSauvegarder(self) -> None:
    #     """Charger une sauvegarde (progression) sur la grille en cours"""
    #     chemin, _ = QFileDialog.getOpenFileName(self.vue, "Charger", os.path.join(sys.path[0], "sauvegarder"), "JSON (*.json)")
    #     if self.modele and chemin:
    #         self.modele.charger_sauvegarde(chemin)
    #         valeurs = {(c.x, c.y): c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
    #         self.vue.mettre_a_jour(valeurs)
     
     
          
    def chargerSauvegarder(self) -> None:
        """Charger une sauvegarde : tue la grille actuelle, recharge l'originale et rejoue les coups"""
        chemin, _ = QFileDialog.getOpenFileName(self.vue, "Charger sauvegarde", os.path.join(sys.path[0], "sauvegarder"), "JSON (*.json)")
        if chemin : 
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 1. On retrouve le chemin complet du fichier d'origine dans le dossier Annexes
            nom_fichier = data.get("grille_originale", "")
            chemin_original = os.path.join(sys.path[0], "Annexes", nom_fichier)
            
            if not os.path.exists(chemin_original):
                print("Erreur : Fichier d'origine introuvable dans Annexes")
                return
                
            # 2. On TUE l'ancienne grille et on recrée la nouvelle depuis l'annexe
            self.fichier_original = nom_fichier
            self.modele = Grille.depuis_json(chemin_original)
            appartenance = {(c.x, c.y) : m.nom for m in self.modele.motifs for c in m.cases}
            valeurs = {(c.x, c.y) : c.valeur for m in self.modele.motifs for c in m.cases if c.valeur != 0}
            
            # On reconstruit la vue (ce qui recrée les cases grises/fixes de base)
            self.vue.grille.caseModifiee.disconnect(self.modifierCase)
            self.vue.grille = VueGrilleAvecSaisie(appartenance, valeurs)
            self.vue.setCentralWidget(self.vue.grille)
            self.vue.grille.caseModifiee.connect(self.modifierCase)
            
            # 3. On rejoue les coups du joueur par-dessus
            for x, y, val in data.get("coups_joueur", []):
                self.modele.poser_valeur(x, y, val) # Mise à jour du modèle
                case_vue = self.vue.grille.cases.get((y, x))
                if case_vue:
                    case_vue.blockSignals(True)
                    case_vue.setText(str(val))      # Mise à jour de la vue
                    case_vue.blockSignals(False)
                    
            self._nom_grille = nom_fichier
            self.vue.set_titre(nom_fichier, os.path.basename(chemin))  #titre   
                 
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