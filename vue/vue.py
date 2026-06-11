from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor
import sys, os
from modele.grille import Grille

LIGNES = 8
COLONNES = 8
TAILLE_CELLULE = 60
MARGE = 10

class VueGrille(QWidget):

    def __init__(self, appartenance_motifs):
        super().__init__()
        self.appartenance_motifs = appartenance_motifs
        self.setFixedSize(COLONNES * TAILLE_CELLULE + 2 * MARGE, LIGNES * TAILLE_CELLULE + 2 * MARGE)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255))

        # petites lignes
        painter.setPen(QPen(QColor(190, 190, 190), 1))
        for i in range(LIGNES + 1):
            painter.drawLine(MARGE, MARGE + i * TAILLE_CELLULE, MARGE + COLONNES * TAILLE_CELLULE, MARGE + i * TAILLE_CELLULE)
        for j in range(COLONNES + 1):
            painter.drawLine(MARGE + j * TAILLE_CELLULE, MARGE, MARGE + j * TAILLE_CELLULE, MARGE + LIGNES * TAILLE_CELLULE)

        # bordures motifs
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        cellules_par_motif = {}
        for (col, row), mid in self.appartenance_motifs.items():
            cellules_par_motif.setdefault(mid, set()).add((col, row))
        for cellules in cellules_par_motif.values():
            for (col, row) in cellules:
                x, y = MARGE + col * TAILLE_CELLULE, MARGE + row * TAILLE_CELLULE
                if (col, row - 1) not in cellules: painter.drawLine(x, y, x + TAILLE_CELLULE, y)
                if (col, row + 1) not in cellules: painter.drawLine(x, y + TAILLE_CELLULE, x + TAILLE_CELLULE, y + TAILLE_CELLULE)
                if (col - 1, row) not in cellules: painter.drawLine(x, y, x, y + TAILLE_CELLULE)
                if (col + 1, row) not in cellules: painter.drawLine(x + TAILLE_CELLULE, y, x + TAILLE_CELLULE, y + TAILLE_CELLULE)

        painter.drawRect(MARGE, MARGE, COLONNES * TAILLE_CELLULE, LIGNES * TAILLE_CELLULE)

class VueGrilleAvecSaisie(QWidget):

    def __init__(self, appartenance_motifs, valeurs={}):
        super().__init__()
        self.setFixedSize(COLONNES * TAILLE_CELLULE + 2 * MARGE, LIGNES * TAILLE_CELLULE + 2 * MARGE)
        
        # La grille dessinée en arrière-plan
        self.grille = VueGrille(appartenance_motifs)
        self.grille.setParent(self)
        self.grille.move(0, 0)

        # Les QLineEdit par-dessus
        self.cases = {}
        for i in range(LIGNES):
            for j in range(COLONNES):
                case = QLineEdit(self)
                case.setAlignment(Qt.AlignmentFlag.AlignCenter)
                case.setMaxLength(1)
                case.setFixedSize(TAILLE_CELLULE - 2, TAILLE_CELLULE - 2)
                case.move(MARGE + j * TAILLE_CELLULE + 1, MARGE + i * TAILLE_CELLULE + 1)
                case.setStyleSheet("background: transparent; border: none; font-size: 20px; color: black;")
                self.cases[(i, j)] = case
                if (j, i) in valeurs:
                    case.setText(str(valeurs[(j, i)]))
                    case.setReadOnly(True)
                
class VueNeonaure(QMainWindow):

    def __init__(self, appartenance_motifs, valeurs={}, modele=None):
        super().__init__()
        self.setWindowTitle("Néonaure")
        self.grille = VueGrilleAvecSaisie(appartenance_motifs, valeurs)
        self.modele = modele
        self.setCentralWidget(self.grille)
        menu = self.menuBar().addMenu("Fichier")
        action_sauvegarder = menu.addAction("Sauvegarder")
        action_sauvegarder.triggered.connect(self.sauvegarder)
    
    def sauvegarder(self):
        from PyQt6.QtWidgets import QFileDialog
        chemin, _ = QFileDialog.getSaveFileName(self, "Sauvegarder", "", "JSON (*.json)")
        if chemin:
            self.modele.sauvegarder(chemin)
        
app = QApplication(sys.argv)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
grille = Grille.depuis_json(os.path.join(base_dir, "Annexes", "grille2.json"))
appartenance_motifs = {(c.x, c.y): m.nom for m in grille.motifs for c in m.cases}
valeurs = {(c.x, c.y): c.valeur for m in grille.motifs for c in m.cases if c.valeur != 0}
fenetre = VueNeonaure(appartenance_motifs, valeurs, grille)
fenetre.show()
sys.exit(app.exec())