"""Module containing the Events class used for event handling."""
from __future__ import annotations

import functools
import pathlib
from typing import Any, Callable, Optional

import clipboard
import qdarkstyle
from PyQt5 import QtGui, QtWidgets

import lightning_pass.gui.mouse_randomness as mouse_rnd
import lightning_pass.users.account as acc
import lightning_pass.util.exceptions as exc
from lightning_pass.util.credentials import Email, ProfilePicture, Token
from lightning_pass.gui.gui_config.widget_data import ClearPreviousWidget


def login_required(func: Callable) -> Callable:
    """Decorate to ensure that a user has to be logged in to access a specific event.

    :param func: Function to decorate

    :return: the decorated function

    """

    @functools.wraps(func)
    def wrapper(self: Events, *args, **kwargs) -> Optional[Callable]:
        """Check the "current_user" attribute.

        :param self: Class instance to give access to its attributes

        :return: executed function or None and show a message box indicating need log in

        """
        if not hasattr(self, "current_user"):
            self.ui.message_boxes.login_required_box("Account")
        else:
            return func(self)

    return wrapper


def vault_unlock_required(func: Callable) -> Callable:
    """Decorate to ensure that a vault is unlocked to access a specific event.

    :param func: Function to decorate

    :return: the decorated function

    """

    @functools.wraps(func)
    def wrapper(self: Events, *args, **kwargs) -> Optional[Callable]:
        """Check the vault_unlocked attribute of the current user.

        If current user does not exist show normal login required box.
        If vault is not unlocked show box indicating need to unlock it.

        :param self: Class instance to give access to its attributes
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        :return: executed function or None and show a message box indicating need log in

        """
        try:
            vault = self.current_user.vault_unlocked
        except AttributeError:
            self.ui.message_boxes.login_required_box("Account")
        else:
            if not vault:
                self.ui.input_dialogs.master_password_dialog(
                    "Account", getattr(self.current_user, "username")
                )
            else:
                return func(self)

    return wrapper


class Events:
    """Used to provide utilities to connections to the events funcs."""

    def __init__(
        self,
        parent: QtWidgets.QMainWindow,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Construct the class."""
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.main_win = parent.main_win
        self.ui = parent.ui

        # temporary fix for default value in gen_pass spin box
        self.ui.generate_pass_spin_box.setValue(16)

    def _set_current_widget(self, widget: str) -> None:
        """Set a new current widget.

        Clears previous widget with the ClearPreviousWidget ctx manager.

        :param widget: The widget to switch to

        """
        with ClearPreviousWidget(self.parent):
            self.ui.stacked_widget.setCurrentWidget(getattr(self.ui, widget))

    def _message_box(self, message_box: str, *args: Any, **kwargs: Any) -> None:
        """Show a chosen message box with the given positional and keyword arguments.

        :param message_box: The message box type to show
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        """
        box = getattr(self.ui.message_boxes, message_box)
        box(*args, **kwargs)

    def home_event(self) -> None:
        """Switch to home widget."""
        self._set_current_widget("home")

    def login_event(self) -> None:
        """Switch to login widget and reset previous values."""
        self._set_current_widget("login")

    def login_user_event(self) -> None:
        """Try to login a user. If successful, show the account widget."""
        try:
            self.current_user = acc.Account.login(
                self.ui.log_username_line_edit.text(),
                self.ui.log_password_line_edit.text(),
            )
        except exc.AccountException:
            self._message_box("invalid_login_box", "Login")
        else:
            self.account_event()

    def register_event(self) -> None:
        """Switch to register widget and reset previous values."""
        self._set_current_widget("register_2")

    def register_user_event(self) -> None:
        """Try to register a user. If successful, show login widget."""
        try:
            self.current_user = acc.Account.register(
                self.ui.reg_username_line.text(),
                self.ui.reg_password_line.text(),
                self.ui.reg_conf_pass_line.text(),
                self.ui.reg_email_line.text(),
            )
        except exc.InvalidUsername:
            self._message_box("invalid_username_box", "Register")
        except exc.InvalidPassword:
            self._message_box("invalid_password_box", "Register")
        except exc.InvalidEmail:
            self._message_box("invalid_email_box", "Register")
        except exc.UsernameAlreadyExists:
            self._message_box("username_already_exists_box", "Register")
        except exc.EmailAlreadyExists:
            self._message_box("email_already_exists_box", "Register")
        except exc.PasswordsDoNotMatch:
            self._message_box("passwords_do_not_match_box", "Register")
        else:
            self._message_box("account_creation_box", "Register")

    def forgot_password_event(self) -> None:
        """Switch to forgot password widget and reset previous email."""
        self._set_current_widget("forgot_password")

    def send_token_event(self) -> None:
        """Send token and switch to token page."""
        email = self.ui.forgot_pass_email_line.text()
        check = Email.check_email_pattern(email)
        if not check:
            self._message_box("invalid_email_box", "Forgot Password")
        else:
            self.ui.reset_token_submit_btn.setEnabled(False)
            Email.send_reset_email(email)
            self.ui.reset_token_submit_btn.setEnabled(True)

            self._message_box("reset_email_sent_box", "Forgot Password")

    def reset_token_event(self) -> None:
        """Switch to reset token page and reset previous values."""
        self._set_current_widget("reset_token")

    def submit_reset_token_event(self) -> None:
        """If submitted token is correct, proceed to password change widget."""
        if Token.check_token_existence(self.ui.reset_token_token_line.text()):
            self.reset_password_event()
        else:
            self._message_box("invalid_token_box", "Reset Password")

    def reset_password_event(self) -> None:
        """Move to reset password page."""
        self._set_current_widget("reset_password")

    def submit_reset_password_event(self) -> None:
        """Attempt to change user's password, show message box if something goes wrong, otherwise move to login page."""
        try:
            acc.change_password(
                ...,
                self.ui.reset_pass_new_pass_line.text(),
                self.ui.reset_pass_conf_new_line.text(),
            )
        except exc.InvalidPassword:
            self._message_box("invalid_password_box", "Reset Password")
        except exc.PasswordsDoNotMatch:
            self._message_box("passwords_do_not_match_box", "Reset Password")
        else:
            del self.parent.change_pass_id
            self._message_box(
                "detail_updated_box",
                "Reset Password",
                "password",
            )

            self.login_event()

    def generate_pass_event(self) -> None:
        """Switch to first password generation widget and reset previous password options."""
        self._set_current_widget("generate_pass")

    def get_generator(self) -> mouse_rnd.PwdGenerator:
        """Get Generator from current password params.

        :returns: PwdGenerator object

        """
        return mouse_rnd.PwdGenerator(
            self.ui.generate_pass_spin_box.value(),
            bool(self.ui.generate_pass_numbers_check.isChecked()),
            bool(self.ui.generate_pass_symbols_check.isChecked()),
            bool(self.ui.generate_pass_lower_check.isChecked()),
            bool(self.ui.generate_pass_upper_check.isChecked()),
        )

    def generate_pass_phase2_event(self) -> None:
        """Switch to the second password generation widget and reset previous values.

        If no password options were checked, shows message box letting the user know about it.

        """
        if (
            not self.ui.generate_pass_numbers_check.isChecked()
            and not self.ui.generate_pass_symbols_check.isChecked()
            and not self.ui.generate_pass_lower_check.isChecked()
            and not self.ui.generate_pass_upper_check.isChecked()
        ):
            self._message_box("no_options_generate", "Generator")
        else:
            self.parent.gen = self.get_generator()
            self.parent.collector.randomness_set = {*()}
            self.parent.pass_progress = 0
            self.ui.generate_pass_p2_prgrs_bar.setValue(self.parent.pass_progress)

            self._set_current_widget("generate_pass_phase2")

    def copy_password_event(self) -> None:
        """Copy generated password into clipboard."""
        clipboard.copy(self.ui.generate_pass_p2_final_pass_line.text())

    @login_required
    def account_event(self) -> None:
        """Switch to account widget and reset previous values.

        Raises log in required error if an user tries to access the page without being logged in.

        """
        self.current_user = acc.Account(self.current_user.user_id)
        self.ui.account_username_line.setText(self.current_user.username)
        self.ui.account_email_line.setText(self.current_user.email)
        self.ui.account_last_log_date.setText(
            f"Last login was {self.current_user.last_login_date}.",
        )
        self.ui.account_pfp_pixmap_lbl.setPixmap(
            QtGui.QPixmap(self.current_user.profile_picture_path),
        )

        self._set_current_widget("account")

    @login_required
    def change_pfp_event(self) -> None:
        """Change profile picture of current user."""
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.parent,
            "Lightning Pass - Open your new profile picture",
            "c:\\",
            "Image files (*.jpg *.png)",
        )
        if fname:
            self.current_user.profile_picture = ProfilePicture.save_picture(
                pathlib.Path(fname),
            )
        self.account_event()

    @login_required
    def logout_event(self) -> None:
        """Logout current user."""
        del self.current_user
        self.home_event()

    @login_required
    def change_pass_event(self) -> None:
        """Change password for current user."""
        ...

    @login_required
    def edit_details_event(self) -> None:
        """Edit user details by changing them on their respective edit lines."""
        if self.current_user.username != self.ui.account_username_line.text():

            try:
                self.current_user.username = self.ui.account_username_line.text()
            except exc.InvalidUsername:
                self._message_box("invalid_username_box", "Account")
            except exc.UsernameAlreadyExists:
                self._message_box("username_already_exists_box", "Account")
            else:
                self._message_box("detail_updated_box", "Account", "username")

        if self.current_user.email != self.ui.account_email_line.text():

            try:
                self.current_user.email = self.ui.account_email_line.text()
            except exc.InvalidEmail:
                self._message_box("invalid_email_box", "Account")
            except exc.EmailAlreadyExists:
                self._message_box("email_already_exists_box", "Account")
            else:
                self._message_box("detail_updated_box", "Account", "email")

    @vault_unlock_required
    @login_required
    def vault_event(self) -> None:
        """Switch to vault window."""
        print(self.current_user.vault_existence)

        from lightning_pass.gui.window import VaultWidget

        self.ui.vault_widget = VaultWidget().widget

        self.ui.vault_stacked_widget.addWidget(self.ui.vault_widget)
        self.ui.vault_stacked_widget.setCurrentWidget(self.ui.vault_widget)

        self.ui.vault_username_lbl.setText(
            f"Current user: {self.current_user.username}",
        )
        self.ui.vault_date_lbl.setText(
            f"Last unlock date: {str(self.current_user.register_date)}",
        )

        self._set_current_widget("vault")

    def vault_lock_event(self) -> None:
        """Lock vault."""
        self.current_user.vault_unlocked = False
        self.account_event()

    @login_required
    def master_password_event(self) -> None:
        """Switch to master password widget."""
        self._set_current_widget("master_password")

    def master_password_submit_event(self) -> None:
        """"""
        try:
            self.current_user.set_master_password(
                self.ui.master_pass_current_pass_line,
                self.ui.master_pass_master_pass_line,
                self.ui.master_pass_conf_master_pass_line,
            )
        except exc.AccountDoesNotExist:
            self._message_box("invalid_login_box", "Master Password")
        return

    def toggle_stylesheet_light(self, *args: object) -> None:
        """Change stylesheet to light mode."""
        self.current_user.vault_unlocked = True
        if args:
            ...
        self.main_win.setStyleSheet("")

    def toggle_stylesheet_dark(self, *args: object) -> None:
        """Change stylesheet to dark mode."""
        if args:
            ...
        self.main_win.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))


__all__ = [
    "Events",
    "login_required",
]
