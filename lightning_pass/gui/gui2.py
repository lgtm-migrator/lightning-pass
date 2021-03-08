from PyQt5 import QtCore
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from .gui_config import buttons, events
from .message_boxes import MessageBoxes
from .mouse_randomness import Collector, Generator
from .static.qt_designer.output.main import Ui_lightning_pass


class LightningPassWindow(QMainWindow):
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

    def __repr__(self):
        return "Lightning Pass :)"

    def show(self):
        """Show main window."""
        self.main_win.show()

    def general_setup(self):
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
    def on_position_changed(self, pos):
        """Handler for changes in mouse position over connected label."""
        val = self.collector.collect_position(pos)
        if val == "Done":
            if not self.password_generated:
                self.pass_gen = Generator(
                    self.collector.randomness_lst,
                    self.ui.generate_pass_spin_box.value(),
                    True if self.ui.generate_pass_numbers_check.isChecked() else False,
                    True if self.ui.generate_pass_symbols_check.isChecked() else False,
                    True if self.ui.generate_pass_lower_check.isChecked() else False,
                    True if self.ui.generate_pass_upper_check.isChecked() else False,
                )
                self.ui.generate_pass_p2_final_pass_line.setText(
                    self.pass_gen.generate_password()
                )
            self.password_generated = True
        elif val is True:
            self.progress += 1
            self.ui.generate_pass_p2_prgrs_bar.setValue(self.progress)
