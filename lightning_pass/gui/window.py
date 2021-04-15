"""Module containing the main GUI classes."""
from __future__ import annotations

import functools
import logging
import sys
from typing import TYPE_CHECKING, Callable

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


def window_runner(func) -> Callable:
    """Decorate a function to run a window without the Qt boilerplate.

    :param func: The functions to decorate

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> None:
        """Wrap the function.

        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        """
        QtCore.QCoreApplication.setApplicationName("Lightning Pass")
        app = QtWidgets.QApplication(sys.argv)

        win = func(app, *args, **kwargs)
        win.show()

        app.exec()

    return wrapper


def run() -> None:
    """Run the application with everything."""
    # run_splash_screen()
    run_main_window()


@window_runner
def run_splash_screen(_) -> SplashScreen:
    """Return ``SplashScreen`` window.

    Dump the ``app`` arg passed in by the decorator.

    """
    return SplashScreen()


@window_runner
def run_main_window(app) -> LightningPassWindow:
    """Return ``LightningPassWindow`` window.

    :param app: The current ``QApplication`` instance

    """
    main_window = LightningPassWindow()
    setup_tray_icon(app, main_window)
    return main_window


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
    """Splash Screen."""

    def __init__(self, parent=None) -> None:
        """Widget constructor."""
        super().__init__(parent)

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
        return f"{self.__class__.__qualname__}()"

    def show(self) -> None:
        """Show the ``SplashScreen`` and initialize loading."""
        self.widget.show()
        self.timer.start(30)

    def increase(self) -> None:
        """Increase loading bar progress by 1 point and close widget if 100% has been reached."""
        self.ui.loading_progress_bar.setValue(self.progress)
        if self.progress > 100:
            self.timer.stop()
            self.widget.close()
        self.progress += 1


class LightningPassWindow(QtWidgets.QMainWindow):
    """Main Window."""

    def __init__(self, parent=None) -> None:
        """Construct the class."""
        super().__init__(parent=parent)

        self.main_win = QtWidgets.QMainWindow()
        self.ui = main.Ui_lightning_pass()
        self.ui.setupUi(self.main_win)

        self.ui.vault_widget_obj = VaultWidget

        self.events = events.Events(self)
        self.buttons = buttons.Buttons(self)
        self.buttons.setup_all()

        self.ui.message_boxes = boxes.MessageBoxes(
            child=self.main_win,
            parent=self,
        )
        self.ui.input_dialogs = boxes.InputDialogs(
            child=self.main_win,
            parent=self,
        )

        self.general_setup()

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}()"

    def show(self) -> None:
        """Show main window."""
        self.main_win.show()

    def general_setup(self) -> None:
        """Move function __init__ function call into a function for simplicity."""
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
    "run",
    "run_main_window",
    "run_splash_screen",
    "setup_tray_icon",
    "window_runner",
]
