"""Module containing the Events class used for event handling."""
from __future__ import annotations

import functools
import pathlib
from typing import Callable

import clipboard
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog, QMainWindow
from qdarkstyle import load_stylesheet

import lightning_pass.gui.message_boxes as msg_box
import lightning_pass.gui.mouse_randomness as mouse_rnd
import lightning_pass.users.account as acc
from lightning_pass.util.exceptions import (
    AccountDoesNotExist,
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
)
from lightning_pass.util.util import Password, ProfilePicture


def login_required(func: Callable) -> Callable:
    """Decorator to ensure that a user has to be logged in to access a specific event.

    :param func: Function to decorate

    :return: the decorated function

    """

    @functools.wraps(func)
    def wrapper(self: Events, *args, **kwargs) -> Callable | None:
        """

        :param self: Class instance to give access to its attributes

        :return: executed function
        """
        if not hasattr(self, "current_user"):
            msg_box.MessageBoxes.login_required_box(self.ui.message_boxes, "account")
        else:
            return func(self, args, kwargs)

    return wrapper


class Events:
    """Used to provide utilities to connections to the events funcs."""

    def __init__(
        self,
        parent: QMainWindow,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Buttons constructor."""
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.main_win = parent.main_win
        self.ui = parent.ui

    def home_event(self) -> None:
        """Switch to home widget."""
        self.ui.stacked_widget.setCurrentWidget(self.ui.home)

    def login_event(self) -> None:
        """Switch to login widget and reset previous values."""
        self.ui.log_username_line_edit.setText("")
        self.ui.log_password_line_edit.setText("")
        self.ui.stacked_widget.setCurrentWidget(self.ui.login)

    def login_user_event(self) -> None:
        """Try to login a user. If successful, show the account widget."""
        try:
            self.current_user = acc.Account.login(
                self.ui.log_username_line_edit.text(),
                self.ui.log_password_line_edit.text(),
            )
        except AccountDoesNotExist:
            msg_box.MessageBoxes.invalid_login_box(self.ui.message_boxes, "Login")
        else:
            self.account_event()

    def register_event(self) -> None:
        """Switch to register widget and reset previous values."""
        self.ui.reg_username_line.setText("")
        self.ui.reg_password_line.setText("")
        self.ui.reg_conf_pass_line.setText("")
        self.ui.reg_email_line.setText("")
        self.ui.stacked_widget.setCurrentWidget(self.ui.register_2)

    def register_user_event(self) -> None:
        """Try to register a user. If successful, show login widget."""
        try:
            self.current_user = acc.Account.register(
                self.ui.reg_username_line.text(),
                Password.hash_password(self.ui.reg_password_line.text()),
                self.ui.reg_conf_pass_line.text(),
                self.ui.reg_email_line.text(),
            )
        except InvalidUsername:
            msg_box.MessageBoxes.invalid_username_box(self.ui.message_boxes, "Register")
        except InvalidPassword:
            msg_box.MessageBoxes.invalid_password_box(self.ui.message_boxes, "Register")
        except InvalidEmail:
            msg_box.MessageBoxes.invalid_email_box(self.ui.message_boxes, "Register")
        except UsernameAlreadyExists:
            msg_box.MessageBoxes.username_already_exists_box(
                self.ui.message_boxes, "Register"
            )
        except EmailAlreadyExists:
            msg_box.MessageBoxes.email_already_exists_box(
                self.ui.message_boxes, "Register"
            )
        except PasswordsDoNotMatch:
            msg_box.MessageBoxes.passwords_do_not_match_box(
                self.ui.message_boxes, "Register"
            )
        else:
            msg_box.MessageBoxes.account_creation_box(self.ui.message_boxes, "Register")

    def forgot_password_event(self) -> None:
        """Switch to forgot password widget and reset previous email."""
        self.ui.forgot_pass_email_line.setText("")
        self.ui.stacked_widget.setCurrentWidget(self.ui.forgot_password)

    def generate_pass_event(self) -> None:
        """Switch to first password generation widget and reset previous password options."""
        self.ui.collector = mouse_rnd.Collector()
        self.ui.generate_pass_spin_box.setValue(16)
        self.ui.generate_pass_numbers_check.setChecked(True)
        self.ui.generate_pass_symbols_check.setChecked(True)
        self.ui.generate_pass_lower_check.setChecked(True)
        self.ui.generate_pass_upper_check.setChecked(True)
        self.ui.stacked_widget.setCurrentWidget(self.ui.generate_pass)

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
            msg_box.MessageBoxes.no_options_generate(self.ui.message_boxes, "Generator")
        else:
            self.parent.collector = mouse_rnd.Collector()
            self.parent.pass_progress = 0
            self.ui.generate_pass_p2_prgrs_bar.setValue(self.parent.pass_progress)
            self.ui.generate_pass_p2_final_pass_line.setText("")
            self.ui.stacked_widget.setCurrentWidget(self.ui.generate_pass_phase2)

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
            f"Last login was {self.ui.current_user.last_login_date}.",
        )
        self.ui.account_pfp_pixmap_lbl.setPixmap(
            QtGui.QPixmap(self.current_user.profile_picture_path),
        )
        self.ui.stacked_widget.setCurrentWidget(self.ui.account)

    @login_required
    def change_pfp_event(self) -> None:
        """Change profile picture of current user."""
        if self.ui.account_pfp_pixmap_lbl.text() == self.current_user.profile_picture:
            fname, _ = QFileDialog.getOpenFileName(
                self.parent,
                "Lightning Pass - Open your new profile picture",
                "c:\\",
                "Image files (*.jpg *.png)",
            )
        else:
            fname = self.ui.account_pfp_pixmap_lbl.text()
        if fname:
            self.current_user.profile_picture = ProfilePicture.save_picture(
                pathlib.Path(fname),
            )
        self.account_event()

    @login_required
    def logout_event(self) -> None:
        """Logout current user."""
        del self.current_user
        self.ui.home_event()

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
            except InvalidUsername:
                msg_box.MessageBoxes.invalid_username_box(
                    self.ui.message_boxes, "Account"
                )
            except UsernameAlreadyExists:
                msg_box.MessageBoxes.username_already_exists_box(
                    self.ui.message_boxes,
                    "Account",
                )
            else:
                msg_box.MessageBoxes.details_updated_box(
                    self.ui.message_boxes,
                    "username",
                    "Account",
                )
        if self.current_user.email != self.ui.account_email_line.text():
            try:
                self.current_user.email = self.ui.account_email_line.text()
            except InvalidEmail:
                msg_box.MessageBoxes.invalid_email_box(self.ui.message_boxes, "Account")
            except EmailAlreadyExists:
                msg_box.MessageBoxes.email_already_exists_box(
                    self.ui.message_boxes, "Account"
                )
            else:
                msg_box.MessageBoxes.details_updated_box(
                    self.ui.message_boxes,
                    "email",
                    "Account",
                )

    def toggle_stylesheet_light(self, *args: object) -> None:
        """Change stylesheet to light mode."""
        if args:
            ...
        self.main_win.setStyleSheet("")

    def toggle_stylesheet_dark(self, *args: object) -> None:
        """Change stylesheet to dark mode."""
        if args:
            ...
        self.main_win.setStyleSheet(load_stylesheet(qt_api="pyqt5"))
