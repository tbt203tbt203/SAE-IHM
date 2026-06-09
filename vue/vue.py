from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys

class VueGrille(QWidget):
    def __init__(self, lignes, colonnes):
        super().__init__()
        layout = QGridLayout()
        self.setLayout(layout)
        self.cases = {}

        for i in range(lignes):
            for j in range(colonnes):
                case = QLineEdit()
                case.setAlignment(Qt.AlignmentFlag.AlignCenter)
                case.setMaxLength(1)
                case.setFixedSize(60, 60)
                self.cases[(i, j)] = case
                layout.addWidget(case, i, j)

class VueNeonaure(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure")

        self.grille = VueGrille(8, 8)
        self.setCentralWidget(self.grille)

        menu = self.menuBar().addMenu("Fichier")
        menu.addAction("Charger")
        menu.addAction("Sauvegarder")
        menu.addAction("Résoudre")

app = QApplication(sys.argv)
fenetre = VueNeonaure()
fenetre.show()
sys.exit(app.exec())