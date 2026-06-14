from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication, QLineEdit, QWidgetAction, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QRegularExpression
from PyQt6.QtGui import QPainter, QPen, QColor, QIntValidator, QRegularExpressionValidator, QShortcut, QKeySequence
from PyQt6.QtWidgets import QPushButton
import sys, os
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget, QSizePolicy, QMenuBar
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QMessageBox

TAILLE_CELLULE = 60
MARGE = 10

COULEUR_FIXE     = QColor(224, 224, 224)   
COULEUR_INVALIDE = QColor(255, 204, 204)   
COULEUR_VIDE     = QColor(255, 255, 255)   
COULEUR_GAGNE    = QColor(167, 230, 167)   #vert grille terminé


def _dimensions(appartenance_motifs: dict) -> tuple[int, int]:
    """Déduit (colonnes, lignes) depuis les coordonnées du dict appartenance_motifs."""
    if not appartenance_motifs:
        return 1, 1
    cols = max(c for c, _ in appartenance_motifs) + 1
    rows = max(r for _, r in appartenance_motifs) + 1
    return cols, rows



class VueGrille(QWidget):
    """
    Couche de dessin pure : fonds colorés, petites lignes, bordures de motifs.
    Tout est peint ici dans paintEvent, donc les lignes sont TOUJOURS au-dessus
    des fonds — aucun widget ne peut les cacher.
    """

    def __init__(self, appartenance_motifs: dict):
        super().__init__()
        self.appartenance_motifs = appartenance_motifs
        self.colonnes, self.lignes = _dimensions(appartenance_motifs)
        self.setFixedSize(
            self.colonnes * TAILLE_CELLULE + 2 * MARGE,
            self.lignes   * TAILLE_CELLULE + 2 * MARGE,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")

        self.couleurs: dict[tuple[int, int], QColor] = {}

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(self.rect(), COULEUR_VIDE)

        for (col, row), couleur in self.couleurs.items():
            x = MARGE + col * TAILLE_CELLULE
            y = MARGE + row * TAILLE_CELLULE
            painter.fillRect(x, y, TAILLE_CELLULE, TAILLE_CELLULE, couleur)

        painter.setPen(QPen(QColor(190, 190, 190), 1))
        for i in range(self.lignes + 1):
            painter.drawLine(
                MARGE, MARGE + i * TAILLE_CELLULE,
                MARGE + self.colonnes * TAILLE_CELLULE, MARGE + i * TAILLE_CELLULE,
            )
        for j in range(self.colonnes + 1):
            painter.drawLine(
                MARGE + j * TAILLE_CELLULE, MARGE,
                MARGE + j * TAILLE_CELLULE, MARGE + self.lignes * TAILLE_CELLULE,
            )

        painter.setPen(QPen(QColor(0, 0, 0), 3))
        cellules_par_motif: dict[str, set] = {}
        for (col, row), mid in self.appartenance_motifs.items():
            cellules_par_motif.setdefault(mid, set()).add((col, row))

        for cellules in cellules_par_motif.values():
            for (col, row) in cellules:
                x = MARGE + col * TAILLE_CELLULE
                y = MARGE + row * TAILLE_CELLULE
                if (col, row - 1) not in cellules:
                    painter.drawLine(x, y, x + TAILLE_CELLULE, y)
                if (col, row + 1) not in cellules:
                    painter.drawLine(x, y + TAILLE_CELLULE, x + TAILLE_CELLULE, y + TAILLE_CELLULE)
                if (col - 1, row) not in cellules:
                    painter.drawLine(x, y, x, y + TAILLE_CELLULE)
                if (col + 1, row) not in cellules:
                    painter.drawLine(x + TAILLE_CELLULE, y, x + TAILLE_CELLULE, y + TAILLE_CELLULE)

        painter.drawRect(MARGE, MARGE, self.colonnes * TAILLE_CELLULE, self.lignes * TAILLE_CELLULE)



class VueGrilleAvecSaisie(QWidget):

    caseModifiee = pyqtSignal(int, int, str)

    def __init__(self, appartenance_motifs: dict, valeurs: dict = {}):
        super().__init__()
        colonnes, lignes = _dimensions(appartenance_motifs)
        self.setFixedSize(
            colonnes * TAILLE_CELLULE + 2 * MARGE,
            lignes   * TAILLE_CELLULE + 2 * MARGE,
        )

        self.grille = VueGrille(appartenance_motifs)
        self.grille.setParent(self)
        self.grille.move(0, 0)
        self.grille.lower()  
        
        self.caseActive : tuple[int, int] | None = None 

        val_max = max(colonnes, lignes)

        self.cases: dict[tuple[int, int], QLineEdit] = {}
        for i in range(lignes):
            for j in range(colonnes):
                case = QLineEdit(self)
                case.setValidator(QRegularExpressionValidator(QRegularExpression("[1-9]")))
                case.setAlignment(Qt.AlignmentFlag.AlignCenter)
                case.setMaxLength(1)
                case.setFixedSize(TAILLE_CELLULE, TAILLE_CELLULE)
                case.move(MARGE + j * TAILLE_CELLULE, MARGE + i * TAILLE_CELLULE)
                case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: black;")
                self.cases[(i, j)] = case
                case.textChanged.connect(lambda texte, x=j, y=i: self.caseModifiee.emit(x, y, texte))

                case.installEventFilter(self)
                
                if (j, i) in valeurs:
                    case.setText(str(valeurs[(j, i)]))
                    case.setReadOnly(True)
                    self.grille.couleurs[(j, i)] = COULEUR_FIXE
                    case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: #555555;")
                    
        
    def set_couleur_case(self, col: int, row: int, couleur: QColor | None) -> None:
        """
        Met à jour la couleur de fond d'une case dans VueGrille et force le repaint.
        Passer couleur=None remet la case en blanc (état normal).
        """
        if couleur is None:
            self.grille.couleurs.pop((col, row), None)
        else:
            self.grille.couleurs[(col, row)] = couleur
        self.grille.update()
        
            
    def eventFilter(self, source, event) -> None :
        
        if event.type() == QEvent.Type.FocusIn : 
            for (i, j), case in self.cases.items() :
                if source is case : 
                    
                    if self.caseActive is not None : 
                        ancien_col, ancien_row = self.caseActive
                        ancien_case = self.cases.get((ancien_row, ancien_col))
                        if ancien_case :
                            if ancien_case.isReadOnly() : 
                                ancien_case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: #555555;")
                            else : 
                                ancien_case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: black;")
                            
                    self.caseActive = (j, i)
                    case.setStyleSheet("background: transparent; border: 4px solid blue; font-size: 20px; color: black;")
                    break
                
        if event.type() == QEvent.Type.FocusOut:
            for (i, j), case in self.cases.items():
                if source is case : 
                    if case.isReadOnly():
                        case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: #555555;")
                    else : 
                        case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: black;")
                    break
        
        if event.type() == QEvent.Type.KeyPress :
            if self.caseActive is not None : 
                col, row = self.caseActive   
                     
                if event.key() == Qt.Key.Key_Right : 
                    nouveau_col, nouveau_row = col + 1, row
                elif event.key() == Qt.Key.Key_Left : 
                    nouveau_col, nouveau_row = col - 1, row 
                elif event.key() == Qt.Key.Key_Down : 
                    nouveau_col, nouveau_row = col, row + 1
                elif event.key() == Qt.Key.Key_Up : 
                    nouveau_col, nouveau_row = col, row - 1
                else : 
                    return super().eventFilter(source, event)
        
                nouvelle_case = self.cases.get((nouveau_row, nouveau_col))
                if nouvelle_case :
                    nouvelle_case.setFocus()
                return True
            
        return super().eventFilter(source, event)


            
    def colorier_tout_en_vert(self) -> None:
        """Colore toutes les cases en vert (affichage quand la grille est terminée)."""
        for (i, j) in self.cases:          # i = ligne (y), j = colonne (x)
            self.grille.couleurs[(j, i)] = COULEUR_GAGNE
        self.grille.update()

    def reinitialiser_couleurs(self) -> None:
        """Remet les couleurs de fond à l'état de départ : cases fixes en gris, le reste vide."""
        self.grille.couleurs.clear()
        for (i, j), case in self.cases.items():
            if case.isReadOnly():          # case fixe (donnée du puzzle)
                self.grille.couleurs[(j, i)] = COULEUR_FIXE
        self.grille.update()

            
    def colorier_tout_en_vert(self) -> None:
        """Colore toutes les cases en vert (affichage quand la grille est terminée)."""
        for (i, j) in self.cases:          # i = ligne (y), j = colonne (x)
            self.grille.couleurs[(j, i)] = COULEUR_GAGNE
        self.grille.update()

    def reinitialiser_couleurs(self) -> None:
        """Remet les couleurs de fond à l'état de départ : cases fixes en gris, le reste vide."""
        self.grille.couleurs.clear()
        for (i, j), case in self.cases.items():
            if case.isReadOnly():          # case fixe (donnée du puzzle)
                self.grille.couleurs[(j, i)] = COULEUR_FIXE
        self.grille.update()



PADDING_FENETRE = 20 # avant c est 4


class VueNeonaure(QMainWindow):

    def __init__(self, appartenance_motifs: dict, valeurs: dict = {}, modele=None):
        super().__init__()

        self.setWindowTitle("Néonaure")
        
        self._construire_menu()
        
        self.grille = VueGrilleAvecSaisie(appartenance_motifs, valeurs)
        self.setCentralWidget(self.grille)
        
        
    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange : 
            if not (self.windowState() & Qt.WindowState.WindowMaximized) and \
                not (self.windowState() & Qt.WindowState.WindowMinimized) : 
                    self._ajuster_taille()
                    
    def _ajuster_taille(self) -> None :
        if hasattr(self, 'grille') and self.grille : 
            if not self.isMaximized():
                pad2 = PADDING_FENETRE * 2
                menu_h = self.menuBar().sizeHint().height()
                new_w = self.grille.width() + pad2
                new_h = self.grille.height() + menu_h + pad2
                self.setMinimumSize(new_w, new_h)
                self.resize(new_w, new_h)
            
    def _construire_menu(self) : 
        """Construire le bouton menu"""
        menu = self.menuBar().addMenu("Menu")
        menu.setStyleSheet(
            "QMenu { background-color: black; color: white; border: 1px solid gray; }"
            "QMenu::item:selected { background-color: gray; color: white; }"
            "QMenu::item { padding: 4px 20px; }"
            "QMenu::item::shortcut { color: #888888; }"
            )
        
        # action_jouer = menu.addAction("Jouer")
        # action_jouer.triggered.connect(self.changerGrille)
        # action_jouer.setShortcut("Ctrl+O")
        
        # action_charger = menu.addAction("Charger")
        # action_charger.triggered.connect(self.charger)
        # action_charger.setShortcut("Ctrl+L")
        
        # action_sauvegarder = menu.addAction("Sauvegarder")
        # action_sauvegarder.triggered.connect(self.sauvegarder)
        # action_sauvegarder.setShortcut("Ctrl+S")

        btn_reset = QPushButton("↺")
        btn_reset.setFlat(True)
        btn_reset.clicked.connect(self.reset)
        # self.menuBar().setCornerWidget(btn_reset)
        
        btn_resoudre = QPushButton("💡")
        btn_resoudre.setFlat(True)
        btn_resoudre.clicked.connect(self.resoudre)
        
        btn_annuler = QPushButton("←")
        btn_annuler.setFlat(True)
        btn_annuler.clicked.connect(self.annuler)

        btn_retablir = QPushButton("→")
        btn_retablir.setFlat(True)
        btn_retablir.clicked.connect(self.retablir)


        
        coin = QWidget()
        layout = QHBoxLayout(coin)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(btn_resoudre)
        layout.addWidget(btn_reset)
        self.menuBar().setCornerWidget(coin)
        
        layout.addWidget(btn_annuler)
        layout.addWidget(btn_retablir)
        layout.addWidget(btn_resoudre)
        layout.addWidget(btn_reset)

        # action_supprimer = menu.addAction("Supprimer")
        # action_supprimer.triggered.connect(self.supprimer)
        # action_supprimer.setShortcut("Ctrl+D")

        # action_resoudre = menu.addAction("Resoudre")
        # action_resoudre.triggered.connect(self.resoudre)
        # action_resoudre.setShortcut("Ctrl+R")
        
        # action_reset = menu.addAction("Reset")
        # action_reset.triggered.connect(self.reset)
        # action_reset.setShortcut("Ctrl+Shift+Z")
        
        self._ajouter_action_menu(menu, "Jouer", "Ctrl+O", self.changerGrille)
        self._ajouter_action_menu(menu, "Charger", "Ctrl+L", self.charger)
        self._ajouter_action_menu(menu, "Sauvegarder", "Ctrl+S", self.sauvegarder)
        self._ajouter_action_menu(menu, "Supprimer", "Ctrl+D", self.supprimer)
        self._ajouter_action_menu(menu, "Resoudre", "Ctrl+R", self.resoudre)
        self._ajouter_action_menu(menu, "Reset", "Ctrl+Shift+R", self.reset)
        self._ajouter_action_menu(menu, "Annuler", "Ctrl+Z", self.annuler)
        self._ajouter_action_menu(menu, "Rétablir", "Ctrl+Y", self.retablir)
        
    
        
    def _ajouter_action_menu(self, menu, texte: str, raccourci: str, slot) -> None:
        """Crée une action de menu avec texte blanc et raccourci gris."""
        conteneur = QWidget()
        conteneur.setFixedHeight(28)
        layout = QHBoxLayout(conteneur)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)

        label_texte = QLabel(texte)
        label_texte.setStyleSheet("color: white; background: transparent; font-size: 13px;")

        label_raccourci = QLabel(raccourci)
        label_raccourci.setStyleSheet("color: #888888; background: transparent; font-size: 13px;")
        label_raccourci.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(label_texte)
        layout.addStretch()
        layout.addWidget(label_raccourci)

        conteneur.setStyleSheet("QWidget:hover { background-color: gray; }")

        action = QWidgetAction(menu)
        action.setDefaultWidget(conteneur)
        action.triggered.connect(slot)
        menu.addAction(action)

        shortcut = QShortcut(QKeySequence(raccourci), self)
        shortcut.activated.connect(slot)


    def setCentralWidget(self, widget) -> None:
        from PyQt6.QtWidgets import QWidget, QVBoxLayout
        if isinstance(widget, VueGrilleAvecSaisie):
            self.grille = widget
            conteneur = QWidget()
            layout = QVBoxLayout(conteneur)
            layout.setContentsMargins(PADDING_FENETRE, PADDING_FENETRE, PADDING_FENETRE, PADDING_FENETRE)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(widget)
            super().setCentralWidget(conteneur)
            
            self._ajuster_taille()
            
            # if not self.isMaximized():
            #     pad2 = PADDING_FENETRE * 2
            #     menu_h = self.menuBar().sizeHint().height()
            #     new_w = widget.width() + pad2
            #     new_h = widget.height() + menu_h + pad2
            #     self.setMinimumSize(new_w, new_h)
            #     self.resize(new_w, new_h)
        else:
            super().setCentralWidget(widget)

        # menu = self.menuBar().addMenu("Menu")
        # menu.setStyleSheet(
        #     "QMenu { background-color: black; color: white; border: 1px solid gray; }"
        #     "QMenu::item:selected { background-color: gray; color: white; }"
        #     "QMenu::item { padding: 4px 20px; }"
        # )

        # action_sauvegarder = menu.addAction("Sauvegarder")
        # action_sauvegarder.triggered.connect(self.sauvegarder)

        # action_charger = menu.addAction("Charger")
        # action_charger.triggered.connect(self.charger)

        # action_jouer = menu.addAction("Jouer")
        # action_jouer.triggered.connect(self.changerGrille)

        # action_reset = menu.addAction("Reset")
        # action_reset.triggered.connect(self.reset)
        # btn_reset = QPushButton("↺")
        # btn_reset.setFlat(True)
        # btn_reset.clicked.connect(self.reset)
        # self.menuBar().setCornerWidget(btn_reset)

        # action_supprimer = menu.addAction("Supprimer")
        # action_supprimer.triggered.connect(self.supprimer)

        # action_resoudre = menu.addAction("Resoudre")
        # action_resoudre.triggered.connect(self.resoudre)


    supprimerClicked = pyqtSignal()
    def supprimer(self):
        """Supprimer un fichier dans le dossier sauvegarder"""
        self.supprimerClicked.emit()

    sauvegarderClicked = pyqtSignal()
    def sauvegarder(self):
        """Sauvegarde un fichier JSON dans le dossier sauvegarder"""
        self.sauvegarderClicked.emit()

    chargerSauvegarderClicked = pyqtSignal()
    def charger(self):
        """Charger un fichier JSON depuis le dossier sauvegarder"""
        self.chargerSauvegarderClicked.emit()

    changerGrilleClicked = pyqtSignal()
    def changerGrille(self):
        """Charger un fichier JSON depuis le dossier Annexes"""
        self.changerGrilleClicked.emit()

    resetClicked = pyqtSignal()
    def reset(self):
        """Rendre la grille à son état initial"""
        self.resetClicked.emit()

    resoudreClicked = pyqtSignal()
    def resoudre(self):
        """Résout la grille courant"""
        self.resoudreClicked.emit()
        
    annulerClicked = pyqtSignal()
    def annuler(self):
        self.annulerClicked.emit()

    retablirClicked = pyqtSignal()
    def retablir(self):
        self.retablirClicked.emit()


    #def mettre_a_jour(self, valeurs: dict) -> None:
     #   """Mettre à jour la grille courante"""
      #  for (i, j), case in self.grille.cases.items():
       #     if (j, i) in valeurs:
        #        case.setText(str(valeurs[(j, i)]))
         #   else:
          #      if not case.isReadOnly():
           #         case.setText("")

    def mettre_a_jour(self, valeurs: dict) -> None:
            """Mettre à jour la grille courante"""
            for (i, j), case in self.grille.cases.items():
                case.blockSignals(True)   # MAJ programmée : on ne redéclenche pas caseModifiee
                if (j, i) in valeurs:
                    case.setText(str(valeurs[(j, i)]))
                else:
                    if not case.isReadOnly():
                        case.setText("")
                        
                if not case.isReadOnly() :
                    self.grille.set_couleur_case(j, i, None)
                case.blockSignals(False)
                
    def colorier_case(self, x: int, y: int, valide: bool) -> None:
        """
        Colorie le fond d'une case via VueGrille (jamais via QLineEdit).
        Les cases fixes ne sont jamais recolorées.
        """
        case = self.grille.cases.get((y, x))
        if case and not case.isReadOnly():
            couleur = None if valide else COULEUR_INVALIDE
            self.grille.set_couleur_case(x, y, couleur)
            
    def set_titre(self, nom_grille : str, nom_sauvegarde: str = None) : 
        self.setWindowTitle(f"Néonaure - {nom_grille}  |  {nom_sauvegarde or '---'}")

    def afficher_message_fin(self) -> None:
        """Pop-up affiché quand la partie est terminée (grille finie ou résolue)."""
        boite = QDialog(self)
        boite.setWindowTitle("Néonaure")
        layout = QVBoxLayout(boite)

        label = QLabel("Jeu terminé ! Bien joué.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 12px;")
        layout.addWidget(label)

        ligne_boutons = QHBoxLayout()
        btn_recommencer = QPushButton("Recommencer")
        btn_credit = QPushButton("Crédit")
        ligne_boutons.addWidget(btn_recommencer)
        ligne_boutons.addWidget(btn_credit)
        layout.addLayout(ligne_boutons)

        def _recommencer():
            boite.accept()
            self.reset()
        btn_recommencer.clicked.connect(_recommencer)

        btn_credit.clicked.connect(self.afficher_credits)

        boite.exec()

    def afficher_credits(self) -> None:
        """Pop-up affichant les noms des auteurs du projet."""
        noms = "Axel Guilbert\nThibault Frappart\nAmmal Najnan Bin Asri"
        QMessageBox.information(self, "Crédits", noms)
        
        
        
## test de la vue YAYYY !!!
'''if __name__ == "__main__" :
    print("TEST : classe vue")
    app = QApplication(sys.argv)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    grille = Grille.depuis_json(os.path.join(base_dir, "Annexes", "grille2.json"))
    appartenance_motifs = {(c.x, c.y): m.nom for m in grille.motifs for c in m.cases}
    valeurs = {(c.x, c.y): c.valeur for m in grille.motifs for c in m.cases if c.valeur != 0}
    fenetre = VueNeonaure(appartenance_motifs, valeurs, grille)
    fenetre.show()
    sys.exit(app.exec())'''