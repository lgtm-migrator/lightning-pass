"""Run app."""

import sys

from PyQt5.QtWidgets import QApplication

from lightning_pass.gui.gui import LightningPassWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LightningPassWindow()
    window.show()
    sys.exit(app.exec_())
