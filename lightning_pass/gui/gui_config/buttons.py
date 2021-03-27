"""Module containing the Buttons class.

Used for connecting each button on the GUI to various events or lambdas.

"""
from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.settings import LIGHT_STYLESHEET, DARK_STYLESHEET


class Buttons:
    """Used to setup buttons on the LightningPassWindow."""

    def __init__(
        self,
        parent: QtWidgets.QMainWindow,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Buttons constructor.

        :param QMainWindow parent: Main GUI window

        """
        super().__init__(*args, **kwargs)
        self.main_win = parent
        self.ui = parent.ui

    def setup_all(self):
        """Run all 3 funcs to setup everything."""
        self.setup_buttons()
        self.setup_menu_bar()
        self.data_validation()

    def setup_buttons(self) -> None:
        """Connect all buttons on all widgets"""
        # home
        self.ui.home_login_btn.clicked.connect(self.main_win.events.login_event)
        self.ui.home_register_btn.clicked.connect(self.main_win.events.register_event)
        self.ui.home_generate_password_btn.clicked.connect(
            self.main_win.events.generate_pass_event,
        )

        # login
        self.ui.log_main_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.log_forgot_pass_btn.clicked.connect(
            self.main_win.events.forgot_password_event,
        )
        self.ui.log_login_btn_2.clicked.connect(self.main_win.events.login_user_event)

        # register
        self.ui.reg_main_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.reg_register_btn.clicked.connect(
            self.main_win.events.register_user_event,
        )

        # forgot_password
        self.ui.forgot_pass_main_menu_btn.clicked.connect(
            self.main_win.events.home_event,
        )
        self.ui.forgot_pass_reset_btn.clicked.connect(
            self.main_win.events.send_token_event,
        )

        # reset_token
        self.ui.reset_token_main_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.reset_token_submit_btn.clicked.connect(
            self.main_win.events.submit_reset_token_event,
        )

        # reset_password
        self.ui.reset_pass_main_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.reset_pass_confirm_btn.clicked.connect(
            self.main_win.events.submit_reset_password_event,
        )

        # generate_pass
        self.ui.generate_pass_generate_btn.clicked.connect(
            self.main_win.events.generate_pass_phase2_event,
        )
        self.ui.generate_pass_main_menu_btn.clicked.connect(
            self.main_win.events.home_event,
        )

        # generate_pass_phase2
        self.ui.generate_pass_p2_main_btn.clicked.connect(
            self.main_win.events.home_event,
        )
        self.ui.generate_pass_p2_copy_btn.clicked.connect(
            self.main_win.events.copy_password_event,
        )

        # account
        self.ui.account_main_menu_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.account_change_pfp_btn.clicked.connect(
            self.main_win.events.change_pfp_event,
        )
        self.ui.account_logout_btn.clicked.connect(self.main_win.events.logout_event)
        self.ui.account_change_pass_btn.clicked.connect(
            self.main_win.events.change_pass_event,
        )
        self.ui.account_edit_details_btn.clicked.connect(
            self.main_win.events.edit_details_event,
        )
        self.ui.account_vault_btn.clicked.connect(self.main_win.events.vault_event)

        # vault
        self.ui.vault_menu_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.vault_lock_btn.clicked.connect(self.main_win.events.vault_lock_event)

    def setup_menu_bar(self) -> None:
        """Connect all menu bar actions."""
        self.ui.action_main_menu.triggered.connect(self.main_win.events.home_event)
        self.ui.action_light.triggered.connect(
            lambda: self.main_win.events.toggle_stylesheet_light(LIGHT_STYLESHEET),
        )
        self.ui.action_dark.triggered.connect(
            lambda: self.main_win.events.toggle_stylesheet_dark(DARK_STYLESHEET),
        )
        self.ui.action_generate.triggered.connect(
            self.main_win.events.generate_pass_event,
        )
        self.ui.action_login.triggered.connect(self.main_win.events.login_event)
        self.ui.action_register.triggered.connect(self.main_win.events.register_event)
        self.ui.action_profile.triggered.connect(self.main_win.events.account_event)
        self.ui.action_vault.triggered.connect(self.main_win.events.vault_event)
        self.ui.action_forgot_password.triggered.connect(
            self.main_win.events.forgot_password_event,
        )
        self.ui.action_reset_token.triggered.connect(
            self.main_win.events.reset_token_event,
        )

    def data_validation(self) -> None:
        """Disable whitespaces in registration input fields."""
        input_validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"[^\s ]+"))
        self.ui.reg_username_line.setValidator(input_validator)
        self.ui.reg_password_line.setValidator(input_validator)
        self.ui.reg_conf_pass_line.setValidator(input_validator)
        self.ui.reg_email_line.setValidator(input_validator)


__all__ = [
    "Buttons",
]
