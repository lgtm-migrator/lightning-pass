"""Holds main GUI class"""
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from ..util.exceptions import StopCollectingPositions
from .gui_config import buttons, events
from .message_boxes import MessageBoxes
from .mouse_randomness import Collector
from .static.qt_designer.output.main import Ui_lightning_pass


class LightningPassWindow(QMainWindow):
    """Main Window."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_win = QMainWindow()

        self.ui = Ui_lightning_pass()
        self.ui.setupUi(self.main_win)

        self.events = events.Events(self)

        self.buttons = buttons.Buttons(self)
        self.buttons.setup_buttons()
        self.buttons.setup_menu_bar()

        self.ui.message_boxes = MessageBoxes(child=self.main_win, parent=self)

        self.collector = Collector()

        self.general_setup()

    def __repr__(self) -> str:
        """Provide information about this class."""
        return "Lightning Pass :)"

    def show(self):
        """Show main window."""
        self.main_win.show()

    def general_setup(self) -> None:
        self.progress = 0
        self.password_generated = False
        self.ui.stacked_widget.setCurrentWidget(self.ui.home)
        self.events.toggle_stylesheet_dark()  # Dark mode is the default theme.
        self.center()

    def center(self):
        """Center main window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_position_changed(self, pos: "QtCore.QPoint") -> None:
        """Handler for changes in mouse position over connected label.

        :param QPoint pos: Mouse position

        """
        # TODO: check generated
        try:
            self.collector.collect_position(pos)
        except StopCollectingPositions:
            self.ui.generate_pass_p2_final_pass_line.setText(
                self.events.get_generator().generate_password()
            )
        else:
            self.progress += 0.1
            self.ui.generate_pass_p2_prgrs_bar.setValue(self.progress)
