import sys
from PyQt5 import QtWidgets
from lightning_pass.gui.gui import UiLightningPass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = UiLightningPass()
    window = QtWidgets.QMainWindow()
    ex.setup_ui(window)
    window.show()
    sys.exit(app.exec_())
