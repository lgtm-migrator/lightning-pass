"""Module containing the Events class used for event handling."""
from __future__ import annotations

import contextlib
import pathlib
from typing import TYPE_CHECKING, Any

import qdarkstyle
from PyQt5 import QtGui, QtWidgets

import lightning_pass.gui.gui_config.event_decorators as decorators
from lightning_pass.gui.gui_config.widgets import WidgetUtil
from lightning_pass.users.account import Account
from lightning_pass.util.exceptions import (
    AccountDoesNotExist,
    AccountException,
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidURL,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
    ValidationFailure,
    VaultException,
)

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QMainWindow


def _ord(day: int) -> str:
    """Return given day in a human readable string.

    :param day: The day to convert to the human readable form

    """
    suffix = "th", "st", "nd", "rd"

    if (div := day % 10) in (1, 2, 3) and day not in (11, 12, 13):
        return suffix[div]
    return suffix[0]


class Events:
    """Used to provide logic to specific event functions."""

    __current_token: str

    def __init__(self, parent: QMainWindow) -> None:
        """Construct the class."""
        super().__init__()
        self.widget_util = WidgetUtil(parent)
        self.parent = parent

        self.current_user = Account(0)

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.parent!r})"

    def home_event(self) -> None:
        """Switch to home widget."""
        self.widget_util.set_current_widget("home")

    def login_event(self) -> None:
        """Switch to login widget and reset previous values."""
        self.widget_util.set_current_widget("login")

    def login_user_event(self) -> None:
        """Try to login a user. If successful, show the account widget."""
        try:
            self.current_user = Account.login(
                self.parent.ui.log_username_line_edit.text(),
                self.parent.ui.log_password_line_edit.text(),
            )
        except AccountException:
            self.widget_util.message_box("invalid_login_box", "Login")
        else:
            self.account_event()

    def register_event(self) -> None:
        """Switch to register widget and reset previous values."""
        self.widget_util.set_current_widget("register_2")

    def register_user_event(self) -> None:
        """Try to register a user. If successful, show login widget."""
        try:
            self.current_user = Account.register(
                self.parent.ui.reg_username_line.text(),
                self.parent.ui.reg_password_line.text(),
                self.parent.ui.reg_conf_pass_line.text(),
                self.parent.ui.reg_email_line.text(),
            )
        except InvalidUsername:
            self.widget_util.message_box("invalid_username_box", "Register")
        except InvalidPassword:
            self.widget_util.message_box("invalid_password_box", "Register")
        except InvalidEmail:
            self.widget_util.message_box("invalid_email_box", "Register")
        except UsernameAlreadyExists:
            self.widget_util.message_box("username_already_exists_box", "Register")
        except EmailAlreadyExists:
            self.widget_util.message_box("email_already_exists_box", "Register")
        except PasswordsDoNotMatch:
            self.widget_util.message_box("passwords_do_not_match_box", "Register")
        else:
            self.widget_util.message_box("account_creation_box")

    def forgot_password_event(self) -> None:
        """Switch to forgot password widget and reset previous email."""
        self.widget_util.set_current_widget("forgot_password")

    def reset_token_event(self) -> None:
        """Switch to reset token page and reset previous values."""
        self.widget_util.set_current_widget("reset_token")

    def send_token_event(self) -> None:
        """Send token and switch to token page."""
        try:
            Account.email_validator.pattern(
                email := self.parent.ui.forgot_pass_email_line.text(),
            )
        except ValidationFailure:
            self.widget_util.message_box("invalid_email_box", "Forgot Password")
        else:
            with self.widget_util.disable_widget(self.parent.ui.reset_token_submit_btn):
                if not Account.credentials.check_item_existence(
                    email,
                    "email",
                    should_exist=True,
                ):
                    # mimic waiting time to send the email
                    self.widget_util.waiting_loop(2)

                Account.credentials.send_reset_email(email)

            self.widget_util.message_box("reset_email_sent_box", "Forgot Password")

    def submit_reset_token_event(self) -> None:
        """If submitted token is correct, proceed to password change widget."""
        if Account.credentials.validate_token(
            token := self.parent.ui.reset_token_token_line.text(),
        ):
            self.__current_token = token
            self.reset_password_event()
        else:
            self.widget_util.message_box("invalid_token_box", "Reset Password")

    def reset_password_event(self) -> None:
        """Switch to the reset password widget."""
        self.widget_util.set_current_widget("reset_password")

    def reset_password_submit_event(self) -> None:
        """Reset user's password."""
        try:
            # everything after the token hex is the user's database primary key
            # refer to the token generation for more information
            Account(int(self.__current_token[30:])).reset_password(
                self.parent.ui.reset_password_new_pass_line.text(),
                self.parent.ui.reset_password_conf_new_pass_line.text(),
            )
        except InvalidPassword:
            self.widget_util.message_box("invalid_password_box", "Reset Password")
        except PasswordsDoNotMatch:
            self.widget_util.message_box("passwords_do_not_match_box", "Reset Password")
        else:
            self.widget_util.message_box(
                "detail_updated_box",
                "Reset Password",
                detail="password",
            )
            del self.__current_token

    @decorators.login_required(page_to_access="change password")
    def change_password_event(self) -> None:
        """Change password for current user."""
        self.widget_util.set_current_widget("change_password")

    @decorators.login_required(page_to_access="change password")
    def submit_change_password_event(self) -> None:
        """Change user's password.

        Show message box if something goes wrong, otherwise move to login page.

        """
        try:
            self.current_user.password = self.current_user.credentials.PasswordData(
                self.current_user.password,
                self.parent.ui.change_password_current_pass_line.text(),
                self.parent.ui.change_password_new_pass_line.text(),
                self.parent.ui.change_password_conf_new_line.text(),
            )
        except AccountDoesNotExist:
            self.widget_util.message_box("invalid_login_box", "Change Password")
        except InvalidPassword:
            self.widget_util.message_box(
                "invalid_password_box",
                "Change Password",
                item="new password",
            )
        except PasswordsDoNotMatch:
            self.widget_util.message_box(
                "passwords_do_not_match_box",
                "Change Password",
                item="New passwords",
            )
        else:
            self.widget_util.message_box(
                "detail_updated_box",
                "Change Password",
                "password",
            )
            self.change_password_event()

    def generate_pass_event(self) -> None:
        """Switch to first password generation widget and reset previous password options."""
        self.widget_util.set_current_widget("generate_pass")
        self.parent.ui.pass_progress = 0

    def generate_pass_phase2_event(self) -> None:
        """Switch to the second password generation widget and reset previous values.

        If no password options were checked, shows message box letting the user know about it.

        """
        if not self.parent.ui.generate_pass_p2_tracking_lbl.hasMouseTracking():
            self.widget_util.mouse_randomness.MouseTracker.setup_tracker(
                self.parent.ui.generate_pass_p2_tracking_lbl,
                self.parent.on_position_changed,
            )

        if not any(
            # exclude length
            val
            for val in self.widget_util.password_options
            if isinstance(val, bool)
        ):
            self.widget_util.message_box("no_options_generate_box", "Generator")
        else:
            self.parent.gen = self.widget_util.get_generator()
            self.parent.pass_progress = 0
            self.parent.ui.generate_pass_p2_prgrs_bar.setValue(
                self.parent.pass_progress,
            )

            self.widget_util.set_current_widget("generate_pass_phase2")

    def generate_pass_again_event(self) -> None:
        """Re-instantiate a new generator object with the same options.

        Reset previous generation values.

        """
        self.parent.pass_progress = 0
        self.parent.ui.generate_pass_p2_prgrs_bar.setValue(self.parent.pass_progress)
        self.parent.ui.generate_pass_p2_final_pass_line.clear()
        self.parent.gen = self.widget_util.mouse_randomness.PwdGenerator(
            self.parent.gen.options,
        )

    @decorators.login_required(page_to_access="account")
    def account_event(self) -> None:
        """Switch to account widget and set current user values."""
        self.parent.ui.account_username_line.setText(self.current_user.username)
        self.parent.ui.account_email_line.setText(self.current_user.email)

        date = self.current_user.current_login_date
        try:
            text = f"Last login date: {date:%d}{_ord(date.day)} {date:%b. %Y, %H:%M}"
        except TypeError:
            text = "Last login date: None"
        self.parent.ui.account_last_log_date.setText(text)

        self.parent.ui.account_pfp_pixmap_lbl.setPixmap(
            QtGui.QPixmap(self.current_user.profile_picture_path),
        )

        self.widget_util.set_current_widget("account")

    decorators.login_required(page_to_access="account")

    def change_pfp_event(self) -> None:
        """Change profile picture of current user."""
        # dump used file filter
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.parent,
            "Lightning Pass - Choose your new profile picture",
            str(pathlib.Path.home()),
            "Image files (*.jpg *.png)",
        )
        if fname:
            self.current_user.profile_picture = (
                self.current_user.credentials.save_picture(
                    pathlib.Path(fname),
                )
            )
            self.parent.ui.account_pfp_pixmap_lbl.setPixmap(
                QtGui.QPixmap(self.current_user.profile_picture_path),
            )

    def logout_event(self) -> None:
        """Logout current user."""
        self.widget_util.clear_platform_actions()
        del self.current_user
        self.home_event()

    def edit_details_event(self) -> None:
        """Edit user details by changing them on their respective edit lines."""
        if not self.current_user.username == (
            name := self.parent.ui.account_username_line.text()
        ):
            try:
                self.current_user.username = name
            except InvalidUsername:
                self.widget_util.message_box("invalid_username_box", "Account")
            except UsernameAlreadyExists:
                self.widget_util.message_box("username_already_exists_box", "Account")
            else:
                self.widget_util.message_box(
                    "detail_updated_box",
                    "Account",
                    detail="username",
                )

        if self.current_user.email != (
            email := self.parent.ui.account_email_line.text()
        ):
            try:
                self.current_user.email = email
            except InvalidEmail:
                self.widget_util.message_box("invalid_email_box", "Account")
            except EmailAlreadyExists:
                self.widget_util.message_box("email_already_exists_box", "Account")
            else:
                self.widget_util.message_box(
                    "detail_updated_box",
                    "Account",
                    detail="email",
                )

    @decorators.login_required(page_to_access="master password")
    def master_password_event(self) -> None:
        """Switch to master password widget.

        If master password already exists, user is required to unlock vault to access this page.
        By unlocking the vault, access to the master key is provided.
        The key will be used while rehashing the saved vault passwords (if master password is changed).

        """
        if not self.current_user.master_key:
            self.widget_util.set_current_widget("master_password")
        elif self.current_user.vault_unlocked and self.current_user.vault_pages():
            self.widget_util.set_current_widget("master_password")
        else:
            self.widget_util.message_box(
                "vault_unlock_required_box",
                "master password",
                page="master password",
            )

    def master_password_submit_event(self) -> None:
        """Try to change or add a master password to a user account.

        :raises AccountDoesNotExist: If the normal password doesn't match
        :raises InvalidPassword: If the master password doesn't match the password pattern
            password pattern:
                1) must be at least 8 characters long
                2) must contain at least 1 capital letter
                3) must contain at least 1 number
                4) must contain at least 1 special character
        :raises PasswordsDoNotMatch: If the 2 master passwords do not match

        """
        prev_key = self.current_user.master_key
        try:
            self.current_user.master_key = self.current_user.credentials.PasswordData(
                self.current_user.password,
                self.parent.ui.master_pass_current_pass_line.text(),
                self.parent.ui.master_pass_master_pass_line.text(),
                self.parent.ui.master_pass_conf_master_pass_line.text(),
            )
        except AccountDoesNotExist:
            self.widget_util.message_box("invalid_login_box", "Master Password")
        except InvalidPassword:
            self.widget_util.message_box(
                "invalid_password_box",
                "Master Password",
                item="master password",
            )
        except PasswordsDoNotMatch:
            self.widget_util.message_box(
                "passwords_do_not_match_box",
                "Master Password",
                item="Master passwords",
            )
        else:
            # need to rehash currently saved vault passwords so they can be recognized by the new master key
            for vault in self.current_user.vault_pages(key=prev_key):
                self.widget_util.rehash_vault_password(vault)

            self.widget_util.message_box(
                "detail_updated_box",
                "Master Password",
                detail="Master password",
            )
            self.account_event()

    @decorators.login_required
    @decorators.master_password_required
    def master_password_dialog_event(self) -> None:
        """Show an input dialog asking the user to enter their current master password.

        Either locks or unlocks the vault depending on the result.

        """
        password = self.parent.ui.input_dialogs.master_password_dialog(
            "Vault",
            self.current_user.username,
        )

        if not self.current_user.pwd_hashing.auth_derived_key(
            password,
            self.current_user.hashed_vault_credentials,
        ):
            self.current_user.vault_unlocked = False
            self.widget_util.message_box("invalid_login_box", "Vault")
        else:
            self.current_user.vault_unlocked = True
            self.current_user._master_key_str = password
            self.widget_util.message_box("vault_unlocked_box")

    @decorators.login_required(page_to_access="vault")
    @decorators.master_password_required(page_to_access="vault")
    @decorators.vault_unlock_required(page_to_access="vault")
    def vault_event(self, previous_index: int | None = None) -> None:
        """Switch to vault window.

        :param previous_index: The index of the window before rebuilding

        """
        self.widget_util.rebuild_vault_stacked_widget()
        for page in self.current_user.vault_pages():
            self.widget_util.setup_vault_widget(page)
        self.parent.ui.menu_bar.addAction(
            getattr(self.parent.ui, "menu_platform").menuAction(),
        )

        self.parent.ui.vault_username_lbl.setText(
            f"Current user: {self.current_user.username}",
        )

        date = self.current_user.current_vault_unlock_date
        try:
            text = f"Last unlock date: {date:%d}{_ord(date.day)} {date:%b. %Y, %H:%M}"
        except TypeError:
            text = "Last unlock date: None"
        self.parent.ui.vault_date_lbl.setText(text)

        self.widget_util.set_current_widget("vault")
        if previous_index:
            self.parent.ui.vault_stacked_widget.setCurrentIndex(previous_index)

    def add_vault_page_event(self) -> None:
        """Add a new vault page.

        Adds new page if empty one was not found,
        switches to new and unused page if one like that exists.

        """
        if (page := self.current_user.vault_pages_int) == (
            count := self.parent.ui.vault_stacked_widget.count() - 1
        ):
            # empty one not found -> create new one
            self.widget_util.setup_vault_widget()
            self.parent.ui.vault_widget.ui.vault_page_lcd_number.display(page)
        else:
            # empty one found -> switch to it
            self.widget_util.vault_stacked_widget_index = count

    def remove_vault_page_event(self) -> None:
        """Remove the current vault page."""
        if self.current_user.vault_pages_int < 1:
            # no eligible page to remove
            return

        platform = self.widget_util.vault_widget_vault.platform_name
        text = self.parent.ui.input_dialogs.confirm_vault_deletion_dialog(
            "Vault",
            platform,
        )
        if text == "CONFIRM" and self.current_user.vault_pages_int >= 1:
            self.current_user.vaults.delete_vault(
                self.current_user.user_id,
                self.widget_util.vault_stacked_widget_index - 1,
            )
            getattr(self.parent.ui, f"action_{platform}").deleteLater()
            self.parent.events.widget_util.rebuild_vault_stacked_widget()

            self.vault_event()
            self.widget_util.message_box(
                "vault_page_deleted_box",
                "Vault",
                platform,
            )

    def vault_lock_event(self) -> None:
        """Lock the vault of the current user."""
        self.current_user.vault_unlocked = False
        self.widget_util.clear_platform_actions()
        self.account_event()

    def change_vault_page_event(self, index_change: int) -> None:
        """Handle changes on the vault window.

        :param index_change: Integer indicating how should the widget index be changed

        """
        with contextlib.suppress(ValueError):
            self.widget_util.vault_stacked_widget_index += index_change

    def update_vault_page_event(self) -> None:
        """Add a new vault tied to the current user.

        Checks if the vault previously existed and stores it.
        Used later to choose correct message box.

        """
        previous_vault = self.current_user.vaults.get_vault(
            self.current_user.user_id,
            self.widget_util.vault_widget_vault.vault_index,
        )

        try:
            self.current_user.vaults.update_vault(
                (
                    new_vault := self.current_user.vaults.Vault(
                        self.current_user.user_id,
                        self.widget_util.vault_widget_vault.platform_name,
                        self.widget_util.vault_widget_vault.website,
                        self.widget_util.vault_widget_vault.username,
                        self.widget_util.vault_widget_vault.email,
                        self.current_user.encrypt_vault_password(
                            new_pass := self.widget_util.vault_widget_vault.password,
                        ),
                        int(self.widget_util.vault_widget_vault.vault_index),
                    )
                ),
            )
        except InvalidURL:
            self.widget_util.message_box("invalid_url_box", "Vault")
        except InvalidEmail:
            self.widget_util.message_box("invalid_email_box", "Vault")
        except VaultException:
            self.widget_util.message_box("invalid_vault_box", "Vault")
        else:
            if previous_vault:
                previous_pass = self.current_user.decrypt_vault_password(
                    previous_vault.password,
                )

                updated_details = [
                    key
                    for key, val in zip(previous_vault._fields, previous_vault)
                    # password check done separately, decryption needed
                    if not key == "password" and not getattr(new_vault, str(key)) == val
                ]
                if previous_pass != new_pass:
                    updated_details.append("password")

                self.widget_util.message_box(
                    "vault_updated_box",
                    "Vault",
                    self.widget_util.vault_widget_vault.platform_name,
                    updated_details,
                )
            else:
                self.widget_util.message_box(
                    "vault_created_box",
                    "Vault",
                    self.widget_util.vault_widget_vault.platform_name,
                )

            self.vault_event(previous_index=self.widget_util.vault_stacked_widget_index)

    def menu_platform_action_event(self, index: int):
        """Handle changes on the vault stacked widget,

        :param index: The index to access

        """
        self.vault_event(previous_index=index)

    def toggle_stylesheet_light(self, *args: Any) -> None:
        """Change stylesheet to light mode."""
        if args:
            ...
        self.parent.main_win.setStyleSheet("")

    def toggle_stylesheet_dark(self, *args: Any) -> None:
        """Change stylesheet to dark mode."""
        if args:
            ...
        self.parent.main_win.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))


__all__ = [
    "Events",
]
