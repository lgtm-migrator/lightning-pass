import pathlib

from PyQt5.QtWidgets import QWidget


class Buttons(QWidget):
    def __init__(self, parent):
        """Buttons constructor"""
        super().__init__(parent)
        self.main_win = parent.main_win
        self.setup_buttons(self.main_win)
        self.setup_menu_bar()

    def setup_buttons(self):
        """Connect all buttons."""
        self.parent.home_login_btn.clicked.connect(self.main_win.login_event)
        self.main_win.home_register_btn.clicked.connect(self.main_win.register_event)
        self.main_win.home_generate_password_btn.clicked.connect(
            self.main_win.generate_pass_event
        )

        self.main_win.log_main_btn.clicked.connect(self.main_win.home_event)
        self.main_win.log_forgot_pass_btn.clicked.connect(
            self.main_win.forgot_password_event
        )
        self.main_win.log_login_btn_2.clicked.connect(self.main_win.login_user_event)

        self.main_win.reg_main_btn.clicked.connect(self.main_win.home_event)
        self.main_win.reg_register_btn.clicked.connect(
            self.main_win.register_user_event
        )

        self.main_win.forgot_pass_main_menu_btn.clicked.connect(
            self.main_win.home_event
        )

        self.main_win.generate_pass_generate_btn.clicked.connect(
            self.main_win.generate_pass_phase2_event
        )
        self.main_win.generate_pass_main_menu_btn.clicked.connect(
            self.main_win.home_event
        )
        self.main_win.generate_pass_p2_main_btn.clicked.connect(
            self.main_win.home_event
        )
        self.main_win.generate_pass_p2_copy_btn.clicked.connect(
            self.main_win.copy_password_event
        )

        self.main_win.account_main_menu_btn.clicked.connect(self.main_win.home_event)
        self.main_win.account_change_pfp_btn.clicked.connect(
            self.main_win.change_pfp_event
        )
        self.main_win.account_logout_btn.clicked.connect(self.main_win.logout_event)
        self.main_win.account_change_pass_btn.clicked.connect(
            self.main_win.change_pass_event
        )
        self.main_win.account_edit_details_btn.clicked.connect(
            self.main_win.edit_details_event
        )

    def setup_menu_bar(self):
        """Connect all menu bar actions."""
        self.main_win.action_main_menu.triggered.connect(self.main_win.home_event)
        self.main_win.action_light.triggered.connect(
            lambda: self.main_win.toggle_stylesheet_light(
                f"{pathlib.Path(__file__).parent}\\static\\light.qss"
            )
        )
        self.main_win.action_dark.triggered.connect(
            lambda: self.main_win.toggle_stylesheet_dark(
                f"{pathlib.Path(__file__).parent}\\static\\dark.qss"
            )
        )
        self.main_win.action_generate.triggered.connect(
            self.main_win.generate_pass_event
        )
        self.main_win.action_login.triggered.connect(self.main_win.login_event)
        self.main_win.action_register.triggered.connect(self.main_win.register_event)
        self.main_win.action_account.triggered.connect(self.main_win.account_event)
        self.main_win.action_forgot_password.triggered.connect(
            self.main_win.forgot_password_event
        )
