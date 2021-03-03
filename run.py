import sys

from PyQt5 import QtWidgets

from lightning_pass.gui.gui import Ui_LightningPass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_LightningPass()
    window.show()
    sys.exit(app.exec_())
