"""Module containing the main GUI classes."""
from __future__ import annotations

import pathlib
import sys

import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.gui import message_boxes, mouse_randomness
from lightning_pass.gui.gui_config import buttons, events
from lightning_pass.gui.static.qt_designer.output import main, splash_screen
from lightning_pass.util.exceptions import StopCollectingPositions


def run() -> None:
    """Show main window with everything set up."""
    SplashScreen()
    app = QtWidgets.QApplication(sys.argv)
    main_window = LightningPassWindow()

    # tray icon setup
    tray_icon = QtWidgets.QSystemTrayIcon(
        QtGui.QIcon(
            str(pathlib.Path(__file__).parent.parent / "gui/static/tray_icon.png")
        ),
        app,
    )
    tray_icon.setToolTip("Lightning Pass")
    tray_icon.show()
    # inherit main window to follow current style sheet
    menu = QtWidgets.QMenu(main_window.main_win)
    quit_action = menu.addAction("Exit Lightning Pass")
    quit_action.triggered.connect(quit)
    tray_icon.setContextMenu(menu)

    main_window.show()
    app.exec_()


class SplashScreen(QtWidgets.QWidget):
    """Splash Screen."""

    def __init__(self) -> None:
        """Widget constuctor."""
        app = QtWidgets.QApplication(sys.argv)

        super().__init__()

        self.widget = QtWidgets.QWidget()
        self.widget.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))
        self.widget.setWindowFlag(QtCore.Qt.FramelessWindowHint)

        self.ui = splash_screen.Ui_loading_widget()
        self.ui.setupUi(self.widget)

        self.widget.show()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.increase)
        self.progress = 0
        self.timer.start(30)

        app.exec_()

    def increase(self) -> None:
        """Increase loading bar progress by 1 point and close widget if 100% has been reached."""
        self.ui.loading_progress_bar.setValue(self.progress)
        if self.progress > 100:
            self.timer.stop()
            self.widget.close()
        self.progress += 1


class LightningPassWindow(QtWidgets.QMainWindow):
    """Main Window."""

    def __init__(self, *args: iter, **kwargs: iter) -> None:
        """Construct the class.

        :param args: ...
        :param kwargs: ...

        """
        super().__init__(*args, **kwargs)

        self.main_win = QtWidgets.QMainWindow()

        self.ui = main.Ui_lightning_pass()
        self.ui.setupUi(self.main_win)

        self.events = events.Events(self)

        buttons.Buttons(self).setup_all()

        self.ui.message_boxes = message_boxes.MessageBoxes(
            child=self.main_win,
            parent=self,
        )

        self.general_setup()

        self.collector = mouse_randomness.Collector()
        mouse_randomness.MouseTracker.setup_tracker(
            self.ui.generate_pass_p2_tracking_lbl,
            self.on_position_changed,
        )
        self.pass_progress = 0

    def __repr__(self) -> str:
        """Provide information about this class."""
        return "LightningPassWindow()"

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

    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_position_changed(self, pos: QtCore.QPoint) -> None:
        """Handle changes in mouse position over connected label.

        :param QPoint pos: Mouse position

        """
        try:
            self.collector.collect_position(pos)
        except StopCollectingPositions:
            if not self.ui.generate_pass_p2_final_pass_line.text():
                gen = self.events.get_generator()
                for i in self.collector.generator():
                    length_check = gen.get_character(i)
                    if length_check is False:
                        break
                self.ui.generate_pass_p2_final_pass_line.setText(gen.get_password())
        else:
            self.pass_progress += 1
            self.ui.generate_pass_p2_prgrs_bar.setValue(self.pass_progress)


__all__ = [
    "LightningPassWindow",
    "SplashScreen",
    "run",
]
