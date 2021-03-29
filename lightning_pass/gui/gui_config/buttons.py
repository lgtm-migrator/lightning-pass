"""Module containing the Buttons class.

Used for connecting each button on the GUI to various events or lambdas.

"""
from typing import Any

from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.settings import DARK_STYLESHEET, LIGHT_STYLESHEET


class Buttons:
    """Used to setup buttons on the LightningPassWindow."""

    def __init__(
        self,
        parent: QtWidgets.QMainWindow,
        *args: Any,
        **kwargs: Any,
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
        buttons_dict = {
            # home
            "home_login_btn": "login_event",
            "home_register_btn": "register_event",
            "home_generate_password_btn": "generate_pass_event",
            # login
            "log_main_btn": "home_event",
            "log_forgot_pass_btn": "forgot_password_event",
            "log_login_btn_2": "login_user_event",
            # register
            "reg_main_btn": "home_event",
            "reg_register_btn": "register_user_event",
            # forgot password
            "forgot_pass_main_menu_btn": "home_event",
            "forgot_pass_reset_btn": "send_token_event",
            # reset token
            "reset_token_main_btn": "home_event",
            "reset_token_submit_btn": "submit_reset_token_event",
            # reset password
            "reset_pass_main_btn": "home_event",
            "reset_pass_confirm_btn": "submit_reset_password_event",
            # generate_pass
            "generate_pass_generate_btn": "generate_pass_phase2_event",
            "generate_pass_main_menu_btn": "home_event",
            # generate_pass_phase2
            "generate_pass_p2_main_btn": "home_event",
            "generate_pass_p2_reset_btn": "generate_pass_phase2_event",
            "generate_pass_p2_copy_tool_btn": "copy_password_event",
            # account
            "account_main_menu_btn": "home_event",
            "account_change_pfp_btn": "change_pfp_event",
            "account_logout_btn": "logout_event",
            "account_change_pass_btn": "change_pass_event",
            "account_edit_details_btn": "edit_details_event",
            "account_vault_btn": "vault_event",
            # vault
            "vault_menu_btn": "home_event",
            "vault_lock_btn": "vault_lock_event",
        }
        for button, event in buttons_dict.items():
            getattr(self.ui, button).clicked.connect(
                getattr(self.main_win.events, event),
            )

        del buttons_dict

    def setup_menu_bar(self) -> None:
        """Connect all menu bar actions."""
        menu_bar_dict = {
            # menu_general
            "action_main_menu": "home_event",
            # menu_password
            "action_generate": "generate_pass_event",
            # menu_users
            "action_login": "login_event",
            "action_register": "register_event",
            "action_forgot_password": "forgot_password_event",
            "action_reset_token": "reset_token_event",
            # menu_account
            "action_profile": "account_event",
            "action_vault": "vault_event",
            "action_master_password": "master_password_event",
        }

        for action, event in menu_bar_dict.items():
            getattr(self.ui, action).triggered.connect(
                getattr(self.main_win.events, event),
            )

        del menu_bar_dict

        # menu_theme
        self.ui.action_light.triggered.connect(
            lambda: self.main_win.events.toggle_stylesheet_light(LIGHT_STYLESHEET),
        )
        self.ui.action_dark.triggered.connect(
            lambda: self.main_win.events.toggle_stylesheet_dark(DARK_STYLESHEET),
        )

    def data_validation(self) -> None:
        """Disable whitespaces in registration input fields."""
        # TODO: add validator lines
        input_validator = QtGui.QRegExpValidator(QtCore.QRegExp(r"[^\s ]+"))
        validator_lines = {
            "reg_username_line",
            "reg_password_line",
            "reg_conf_pass_line",
            "reg_email_line",
        }
        for line in validator_lines:
            getattr(self.ui, line).setValidator(input_validator)

        del validator_lines


__all__ = [
    "Buttons",
]
