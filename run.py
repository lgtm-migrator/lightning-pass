"""Run app."""

import sys

from PyQt5.QtWidgets import QApplication

import lightning_pass.gui.window as window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = window.LightningPassWindow()
    window.show()
    sys.exit(app.exec_())
