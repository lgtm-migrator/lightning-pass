import sys

from PyQt5 import QtWidgets

from lightning_pass.gui.gui import UiLightningPass


def create_app():
    app = QtWidgets.QApplication(sys.argv)
    window = UiLightningPass()
    window.show()
    return app
