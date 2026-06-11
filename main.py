import sys, os
from PyQt6.QtWidgets import QApplication
from controleur.controleur import Controleur

app = QApplication(sys.argv)
base_dir = os.path.dirname(os.path.abspath(__file__))
ctrl = Controleur(os.path.join(base_dir, "Annexes", "grille2.json"))
ctrl.vue.show()
sys.exit(app.exec())