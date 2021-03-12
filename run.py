"""Run app."""

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import lightning_pass.gui.window as window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = window.LightningPassWindow()
    trayIcon = QSystemTrayIcon(QIcon("tray_icon.png"), app)
    trayIcon.setToolTip("Lightning Pass")
    trayIcon.show()
    # Inherit main window to follow current style sheet
    menu = QMenu(MainWindow.main_win)
    quit_action = menu.addAction("Exit Lightning Pass")
    quit_action.triggered.connect(quit)

    trayIcon.setContextMenu(menu)

    MainWindow.show()
    app.exec_()
