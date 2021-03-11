from __future__ import annotations

import pathlib

import clipboard
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog
from qdarkstyle import load_stylesheet

from lightning_pass.users.account import Account
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

from ..message_boxes import MessageBoxes
from ..mouse_randomness import Collector, MouseTracker, PwdGenerator


class Events:
    def __init__(self, parent, *args: object, **kwargs: object) -> None:
        """Buttons constructor"""
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
            self.ui.current_user = Account.login(
                self.ui.log_username_line_edit.text(),
                self.ui.log_password_line_edit.text(),
            )
        except AccountDoesNotExist:
            MessageBoxes.invalid_login_box(self.ui.message_boxes, "Login")
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
            self.ui.current_user = Account.register(
                self.ui.reg_username_line.text(),
                Password.hash_password(self.ui.reg_password_line.text()),
                self.ui.reg_conf_pass_line.text(),
                self.ui.reg_email_line.text(),
            )
        except InvalidUsername:
            MessageBoxes.invalid_username_box(self.ui.message_boxes, "Register")
        except InvalidPassword:
            MessageBoxes.invalid_password_box(self.ui.message_boxes, "Register")
        except InvalidEmail:
            MessageBoxes.invalid_email_box(self.ui.message_boxes, "Register")
        except UsernameAlreadyExists:
            MessageBoxes.username_already_exists_box(self.ui.message_boxes, "Register")
        except EmailAlreadyExists:
            MessageBoxes.email_already_exists_box(self.ui.message_boxes, "Register")
        except PasswordsDoNotMatch:
            MessageBoxes.passwords_do_not_match_box(self.ui.message_boxes, "Register")
        else:
            MessageBoxes.account_creation_box(self.ui.message_boxes, "Register")

    def forgot_password_event(self) -> None:
        """Switch to forgot password widget and reset previous email."""
        self.ui.forgot_pass_email_line.setText("")
        self.ui.stacked_widget.setCurrentWidget(self.ui.forgot_password)

    def generate_pass_event(self) -> None:
        """Switch to first password generation widget and reset previous password options."""
        self.ui.collector = Collector()
        self.ui.generate_pass_spin_box.setValue(16)
        self.ui.generate_pass_numbers_check.setChecked(True)
        self.ui.generate_pass_symbols_check.setChecked(True)
        self.ui.generate_pass_lower_check.setChecked(True)
        self.ui.generate_pass_upper_check.setChecked(True)
        self.ui.stacked_widget.setCurrentWidget(self.ui.generate_pass)

    def get_generator(self) -> PwdGenerator:
        """Get Generator from current password params.

        :returns: PwdGenerator object

        """
        return PwdGenerator(
            self.parent.collector.randomness_lst,
            self.ui.generate_pass_spin_box.value(),
            True if self.ui.generate_pass_numbers_check.isChecked() else False,
            True if self.ui.generate_pass_symbols_check.isChecked() else False,
            True if self.ui.generate_pass_lower_check.isChecked() else False,
            True if self.ui.generate_pass_upper_check.isChecked() else False,
        )

    def generate_pass_phase2_event(self) -> None:
        """Switch to second password generation widget and reset previous values."""
        MouseTracker.setup_tracker(
            self.ui.generate_pass_p2_tracking_lbl, self.parent.on_position_changed
        )
        self.ui.progress = 0
        self.ui.generate_pass_p2_prgrs_bar.setValue(self.ui.progress)
        self.ui.generate_pass_p2_final_pass_line.setText("")
        self.ui.password_generated = False
        if (
            not self.ui.generate_pass_lower_check.isChecked()
            and not self.ui.generate_pass_upper_check.isChecked()
        ):
            MessageBoxes.no_case_type_box(self.ui.message_boxes, "Generator")
        else:
            self.ui.password_generated = False
            self.ui.stacked_widget.setCurrentWidget(self.ui.generate_pass_phase2)

    def copy_password_event(self) -> None:
        """Copy generated password into clipboard."""
        clipboard.copy(self.ui.generate_pass_p2_final_pass_line.text())

    def account_event(self) -> None:
        """Switch to account widget and reset previous values.
        Raises log in required error if an user tries to access the page without being logged in."""
        try:
            if self.ui.current_user.user_id is None:
                raise AttributeError
        except AttributeError:
            MessageBoxes.login_required_box(self.ui.message_boxes, "Account")
        else:
            self.ui.current_user = Account(self.ui.current_user.user_id)
            self.ui.account_username_line.setText(self.ui.current_user.username)
            self.ui.account_email_line.setText(self.ui.current_user.email)
            self.ui.account_last_log_date.setText(
                f"Last login was {self.ui.current_user.last_login_date}."
            )
            self.ui.account_pfp_pixmap_lbl.setPixmap(
                QtGui.QPixmap(self.ui.current_user.profile_picture_path)
            )
            self.ui.stacked_widget.setCurrentWidget(self.ui.account)

    def change_pfp_event(self) -> None:
        """Change profile picture of current user."""
        fname, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Lightning Pass - Open your new profile picture",
            "c:\\",
            "Image files (*.jpg *.png)",
        )
        if fname:
            self.ui.current_user.profile_picture = ProfilePicture.save_picture(
                pathlib.Path(fname)
            )
            self.account_event()

    def logout_event(self) -> None:
        """Logout current user."""
        del self.ui.current_user
        self.ui.home_event()

    def change_pass_event(self) -> None:
        """Change password for current user."""
        ...

    def edit_details_event(self) -> None:
        """Edit user details by changing them on their respective edit lines."""
        if self.ui.current_user.username != self.ui.account_username_line.text():
            try:
                self.ui.current_user.username = self.ui.account_username_line.text()
            except InvalidUsername:
                MessageBoxes.invalid_username_box(self.ui.message_boxes, "Account")
            except UsernameAlreadyExists:
                MessageBoxes.username_already_exists_box(
                    self.ui.message_boxes, "Account"
                )
            else:
                MessageBoxes.details_updated_box(
                    self.ui.message_boxes, "username", "Account"
                )
        if self.ui.current_user.email != self.ui.account_email_line.text():
            try:
                self.ui.current_user.email = self.ui.account_email_line.text()
            except InvalidEmail:
                MessageBoxes.invalid_email_box(self.ui.message_boxes, "Account")
            except EmailAlreadyExists:
                MessageBoxes.email_already_exists_box(self.ui.message_boxes, "Account")
            else:
                MessageBoxes.details_updated_box(
                    self.ui.message_boxes, "email", "Account"
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
