"""Module containing the Buttons class.

Used for connecting each button on the GUI to various events or lambdas.

"""
import webbrowser
from typing import Any, NamedTuple

import clipboard
from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.settings import DARK_STYLESHEET, LIGHT_STYLESHEET


class Clickable(NamedTuple):
    widget: str
    action: str


class VaultToolButton(NamedTuple):
    widget: str
    item: str
    source: str


class Buttons:
    """Used to setup buttons on the ``LightningPassWindow``."""

    __slots__ = "parent"

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
        self.parent = parent

    def setup_all(self):
        """Run all 3 funcs to setup everything."""
        self.setup_buttons()
        self.setup_menu_bar()
        self.data_validation()

    def setup_buttons(self) -> None:
        """Connect all buttons on all widgets"""
        buttons_set = {
            # home
            Clickable("home_login_btn", "login_event"),
            Clickable("home_register_btn", "register_event"),
            Clickable("home_generate_password_btn", "generate_pass_event"),
            # login
            Clickable("log_main_btn", "home_event"),
            Clickable("log_forgot_pass_btn", "forgot_password_event"),
            Clickable("log_login_btn_2", "login_user_event"),
            # register
            Clickable("reg_main_btn", "home_event"),
            Clickable("reg_register_btn", "register_user_event"),
            # forgot_password
            Clickable("forgot_pass_main_menu_btn", "home_event"),
            Clickable("forgot_pass_reset_btn", "send_token_event"),
            # reset_token
            Clickable("reset_token_main_btn", "home_event"),
            Clickable("reset_token_submit_btn", "submit_reset_token_event"),
            # reset_password
            Clickable("reset_password_confirm_btn", "reset_password_submit_event"),
            Clickable("reset_password_main_btn", "home_event"),
            # change_password
            Clickable("change_password_main_btn", "home_event"),
            Clickable("change_password_confirm_btn", "submit_change_password_event"),
            # generate_pass
            Clickable("generate_pass_generate_btn", "generate_pass_phase2_event"),
            Clickable("generate_pass_main_menu_btn", "home_event"),
            # generate_pass_phase2
            Clickable("generate_pass_p2_main_btn", "home_event"),
            Clickable("generate_pass_p2_reset_btn", "generate_pass_again_event"),
            # account
            Clickable("account_main_menu_btn", "home_event"),
            Clickable("account_change_pfp_btn", "change_pfp_event"),
            Clickable("account_logout_btn", "logout_event"),
            Clickable("account_change_pass_btn", "change_password_event"),
            Clickable("account_edit_details_btn", "edit_details_event"),
            Clickable("account_vault_btn", "vault_event"),
            # vault
            Clickable("vault_add_page_btn", "add_vault_page_event"),
            Clickable("vault_remove_page_btn", "remove_vault_page_event"),
            Clickable("vault_menu_btn", "home_event"),
            Clickable("vault_lock_btn", "vault_lock_event"),
            # master_password
            Clickable("master_pass_menu_btn", "home_event"),
            Clickable("master_pass_save_btn", "master_password_submit_event"),
        }

        for button in buttons_set:
            getattr(self.parent.ui, button.widget).clicked.connect(
                getattr(self.parent.events, button.action),
            )

        # miscellaneous
        self.parent.ui.generate_pass_p2_copy_tool_btn.clicked.connect(
            lambda: clipboard.copy(
                self.parent.ui.generate_pass_p2_final_pass_line.text(),
            ),
        )

    def setup_menu_bar(self) -> None:
        """Connect all menu bar actions."""
        menu_bar_set = {
            # menu_general
            Clickable("action_main_menu", "home_event"),
            # menu_password
            Clickable("action_generate", "generate_pass_event"),
            # menu_users
            Clickable("action_login", "login_event"),
            Clickable("action_register", "register_event"),
            Clickable("action_forgot_password", "forgot_password_event"),
            Clickable("action_reset_token", "reset_token_event"),
            # menu_account
            Clickable("action_profile", "account_event"),
            Clickable("action_change_password", "change_password_event"),
            Clickable("action_vault", "vault_event"),
            Clickable("action_master_password", "master_password_event"),
        }

        for button in menu_bar_set:
            getattr(self.parent.ui, button.widget).triggered.connect(
                getattr(self.parent.events, button.action),
            )

        menu_theme_set = {
            # menu_general > themes
            Clickable("action_light", LIGHT_STYLESHEET),
            Clickable("action_dark", DARK_STYLESHEET),
        }

        for action in menu_theme_set:
            getattr(self.parent.ui, action.widget).triggered.connect(
                lambda sheet=action.action: self.parent.events.toggle_stylesheet_light(
                    sheet
                ),
            )

    def data_validation(self) -> None:
        """Disable whitespaces in some input fields."""
        validator_lines = {
            "reg_username_line",
            "reg_password_line",
            "reg_conf_pass_line",
            "reg_email_line",
            "reset_password_new_pass_line",
            "reset_password_conf_new_pass_line",
            "change_password_new_pass_line",
            "change_password_conf_new_line",
            "account_username_line",
            "account_email_line",
            "master_pass_master_pass_line",
            "master_pass_conf_master_pass_line",
        }

        for line in validator_lines:
            getattr(self.parent.ui, line).setValidator(
                QtGui.QRegExpValidator(QtCore.QRegExp(r"[^\s ]+")),
            )

    def setup_vault_buttons(self):
        """Connect all buttons on a new vault widget."""

        # tool buttons for copying vault items
        vault_copy_tool_buttons_set = {
            VaultToolButton(
                "vault_copy_username_tool_btn", "username", "vault_username_line"
            ),
            VaultToolButton("vault_copy_email_tool_btn", "email", "vault_email_line"),
            VaultToolButton(
                "vault_copy_password_tool_btn", "password", "vault_password_line"
            ),
        }

        parent = self.parent.ui.vault_widget.ui
        events = self.parent.events

        parent.vault_open_web_tool_btn.clicked.connect(
            lambda: webbrowser.get().open(parent.vault_web_line.text(), new=2)
        )
        for button in vault_copy_tool_buttons_set:
            getattr(parent, button.widget).clicked.connect(
                # since lambda has a default > dump the first bool passed in by the widget parent
                lambda _, line=getattr(parent, button.source): _copy_text(line),
            )

        parent.vault_update_btn.clicked.connect(
            events.update_vault_page_event,
        )

        parent.vault_forward_tool_btn.clicked.connect(
            lambda: events.change_vault_page_event(1),
        )
        parent.vault_backward_tool_btn.clicked.connect(
            lambda: events.change_vault_page_event(-1),
        )


def _copy_text(obj: QtWidgets.QLineEdit):
    clipboard.copy(obj.text())


__all__ = [
    "Buttons",
]
