"""Module containing the main GUI classes."""
from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.gui import boxes, events
from lightning_pass.gui.gui_config import buttons
from lightning_pass.gui.static.qt_designer.output import (
    main,
    splash_screen,
    vault_widget,
)
from lightning_pass.settings import LOG, TRAY_ICON

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QApplication


def logger():
    log = logging.getLogger(__name__)
    fh = logging.FileHandler(LOG)
    fh.setFormatter(
        logging.Formatter("%(asctime)s: %(name)s: %(levelname)s: %(message)s"),
    )
    log.addHandler(fh)

    return log


def run_main_window(splash: bool = True) -> None:
    """Execute the main window.

    :param splash: Enable splash screen on startup, defaults to True

    """
    QtCore.QCoreApplication.setApplicationName("Lightning Pass")
    app = QtWidgets.QApplication(sys.argv)

    main_window = LightningPassWindow()
    setup_tray_icon(app, main_window)

    if splash:
        main_window.load()
    else:
        main_window.show()

    app.exec()


def setup_tray_icon(app: QApplication, main_window: LightningPassWindow) -> None:
    """Setup a tray icon for the main window.

    :param app: The currently running``QApplication`` instance
    :param main_window: The window which will be shown

    """
    tray_icon = QtWidgets.QSystemTrayIcon(
        QtGui.QIcon(str(TRAY_ICON)),
        app,
    )
    tray_icon.setToolTip("Lightning Pass")
    # inherit main window to follow current style sheet
    menu = QtWidgets.QMenu(main_window.main_win)

    quit_action = menu.addAction("Exit Lightning Pass")
    quit_action.triggered.connect(quit)

    generate_option = menu.addAction("Generate a password")
    generate_option.triggered.connect(main_window.events.generate_pass_event)

    tray_icon.setContextMenu(menu)
    tray_icon.show()


class SplashScreen(QtWidgets.QWidget):
    """Lightning Pass splash screen."""

    def __init__(self, parent=None) -> None:
        """Widget constructor."""
        super().__init__(parent)
        self.parent = parent

        self.widget = QtWidgets.QWidget()
        self.widget.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))
        self.widget.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.ui = splash_screen.Ui_loading_widget()
        self.ui.setupUi(self.widget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.increase)
        self.progress = 0

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.parent!r})"

    def show(self) -> None:
        """Show the ``SplashScreen`` and initialize loading."""
        self.widget.show()
        self.timer.start(30)

    def increase(self) -> None:
        """Increase loading bar progress by 1 point and close widget if 100% has been reached.

        Show parent windows if exists.

        """
        if self.progress == 0:
            self.ui.loading_progress_bar.setFormat(f"%p% - Interface")
        elif self.progress == 65:
            self.ui.loading_progress_bar.setFormat(f"%p% - Database")
        elif self.progress == 95:
            self.ui.loading_progress_bar.setFormat(f"%p% - Done")
        elif self.progress > 100:
            self.timer.stop()
            self.widget.close()

            if p := self.parent:
                p.show()

        self.ui.loading_progress_bar.setValue(self.progress)
        self.progress += 1


class LightningPassWindow(QtWidgets.QMainWindow):
    """Main Lightning Pass window."""

    def __init__(self, parent=None) -> None:
        """Construct the class."""
        super().__init__(parent=parent)

        self.main_win = QtWidgets.QMainWindow()
        self.ui = main.Ui_lightning_pass()
        self.ui.setupUi(self.main_win)

        self.ui.vault_widget_inst = lambda: VaultWidget()

        self.events = events.Events(self)
        self.buttons = buttons.Buttons(self)
        self.buttons.setup_all()

        self.ui.message_boxes = boxes.MessageBoxes(self)
        self.ui.input_dialogs = boxes.InputDialogs(self)

        self.extras()

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}()"

    def show(self) -> None:
        """Show main window."""
        self.main_win.show()

    def load(self) -> None:
        """Show the window with the loading screen as well.

        Main window is then shown after loading is finished.

        """
        splash = SplashScreen(self)
        splash.show()

    def extras(self) -> None:
        """Additional setup for the window."""
        self.main_win.setWindowIcon(QtGui.QIcon(str(TRAY_ICON)))
        self.events.toggle_stylesheet_dark()  # Dark mode is the default theme.
        self.ui.stacked_widget.setCurrentWidget(self.ui.home)
        self.center()

    def center(self) -> None:
        """Center main window."""
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @property
    def current_index(self) -> int:
        """Return the current index of the main stacked widget."""
        return self.ui.stacked_widget.currentIndex()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_position_changed(self, pos: QtCore.QPoint) -> None:
        """Handle changes in mouse position over connected label.

        :param pos: Mouse position

        """
        if self.pass_progress > 1_000:
            return

        if self.gen.coro.send(self.pass_progress) and self.pass_progress != 0:
            self.gen.get_character(pos.x(), pos.y())

        self.ui.generate_pass_p2_final_pass_line.setText(self.gen.password)
        self.pass_progress += 1
        self.ui.generate_pass_p2_prgrs_bar.setValue(self.pass_progress)


class VaultWidget(QtWidgets.QWidget):
    """The widget to be displayed on the left side of the vault page."""

    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QWidget()
        self.ui = vault_widget.Ui_vault_widget()
        self.ui.setupUi(self.widget)

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}()"


__all__ = [
    "LightningPassWindow",
    "SplashScreen",
    "VaultWidget",
    "logger",
    "run_main_window",
    "setup_tray_icon",
]
