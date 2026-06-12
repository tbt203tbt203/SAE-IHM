from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QIntValidator
from PyQt6.QtWidgets import QPushButton
import sys, os
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget, QSizePolicy, QMenuBar


TAILLE_CELLULE = 60
MARGE = 10

COULEUR_FIXE     = QColor(224, 224, 224)   
COULEUR_INVALIDE = QColor(255, 204, 204)   
COULEUR_VIDE     = QColor(255, 255, 255)   


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

        val_max = max(colonnes, lignes)

        self.cases: dict[tuple[int, int], QLineEdit] = {}
        for i in range(lignes):
            for j in range(colonnes):
                case = QLineEdit(self)
                case.setValidator(QIntValidator(1, val_max))
                case.setAlignment(Qt.AlignmentFlag.AlignCenter)
                case.setMaxLength(1)
                case.setFixedSize(TAILLE_CELLULE, TAILLE_CELLULE)
                case.move(MARGE + j * TAILLE_CELLULE, MARGE + i * TAILLE_CELLULE)
                case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: black;")
                self.cases[(i, j)] = case
                case.textChanged.connect(lambda texte, x=j, y=i: self.caseModifiee.emit(x, y, texte))

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



PADDING_FENETRE = 4


class VueNeonaure(QMainWindow):

    def __init__(self, appartenance_motifs: dict, valeurs: dict = {}, modele=None):
        super().__init__()

        self.setWindowTitle("Néonaure")
        
        self._construire_menu()
        
        self.grille = VueGrilleAvecSaisie(appartenance_motifs, valeurs)
        self.setCentralWidget(self.grille)
        
    def _construire_menu(self) : 
        """Construire le bouton menu"""
        menu = self.menuBar().addMenu("Menu")
        menu.setStyleSheet(
            "QMenu { background-color: black; color: white; border: 1px solid gray; }"
            "QMenu::item:selected { background-color: gray; color: white; }"
            "QMenu::item { padding: 4px 20px; }"
            )
        
        action_sauvegarder = menu.addAction("Sauvegarder")
        action_sauvegarder.triggered.connect(self.sauvegarder)

        action_charger = menu.addAction("Charger")
        action_charger.triggered.connect(self.charger)

        action_jouer = menu.addAction("Jouer")
        action_jouer.triggered.connect(self.changerGrille)

        action_reset = menu.addAction("Reset")
        action_reset.triggered.connect(self.reset)
        btn_reset = QPushButton("↺")
        btn_reset.setFlat(True)
        btn_reset.clicked.connect(self.reset)
        # self.menuBar().setCornerWidget(btn_reset)
        
        btn_resoudre = QPushButton("💡")
        btn_resoudre.setFlat(True)
        btn_resoudre.clicked.connect(self.resoudre)
        coin = QWidget()
        layout = QHBoxLayout(coin)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(btn_resoudre)
        layout.addWidget(btn_reset)
        self.menuBar().setCornerWidget(coin)

        action_supprimer = menu.addAction("Supprimer")
        action_supprimer.triggered.connect(self.supprimer)

        action_resoudre = menu.addAction("Resoudre")
        action_resoudre.triggered.connect(self.resoudre)

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
            # if not self.isMaximized():
            #     pad2 = PADDING_FENETRE * 2
            #     self.setMinimumSize(widget.width() + pad2, widget.height() + pad2)
            #     self.resize(widget.width() + pad2, widget.height() + pad2)
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


    def mettre_a_jour(self, valeurs: dict) -> None:
        """Mettre à jour la grille courante"""
        for (i, j), case in self.grille.cases.items():
            if (j, i) in valeurs:
                case.setText(str(valeurs[(j, i)]))
            else:
                if not case.isReadOnly():
                    case.setText("")

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