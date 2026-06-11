from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor
import sys, json, os

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


class VueNeonaure(QMainWindow):

    def __init__(self, appartenance_motifs):
        super().__init__()
        self.setWindowTitle("Néonaure")
        self.grille = VueGrille(appartenance_motifs)
        self.setCentralWidget(self.grille)


def _charger_json(chemin):
    appartenance = {}
    with open(chemin) as f:
        data = json.load(f)
    for motif_id, cells in data.items():
        for cell in cells:
            appartenance[(cell[0], cell[1])] = motif_id
    return appartenance


app = QApplication(sys.argv)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
appartenance_motifs = _charger_json(os.path.join(base_dir, "Annexes", "grille2.json"))
fenetre = VueNeonaure(appartenance_motifs)
fenetre.show()
sys.exit(app.exec())