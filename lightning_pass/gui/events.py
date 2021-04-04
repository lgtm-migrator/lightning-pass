"""Module containing the Events class used for event handling."""
from __future__ import annotations

import contextlib
import pathlib
from typing import Optional, TYPE_CHECKING

import clipboard
import qdarkstyle
from PyQt5 import QtGui, QtWidgets

import lightning_pass.gui.mouse_randomness as mouse_randomness
import lightning_pass.users.account as account
import lightning_pass.users.vaults as vaults
import lightning_pass.util.credentials as credentials
import lightning_pass.gui.gui_config.event_decorators as decorators
import lightning_pass.gui.window as window
from lightning_pass.gui.gui_config.widget_data import (
    ClearPreviousWidget,
    VAULT_WIDGET_DATA,
)
from lightning_pass.util.exceptions import (
    AccountDoesNotExist,
    AccountException,
    EmailAlreadyExists,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    PasswordsDoNotMatch,
    UsernameAlreadyExists,
    InvalidURL,
    VaultException,
)

if TYPE_CHECKING:
    from lightning_pass.users.vaults import Vault


class Events:
    """Used to provide utilities to connections to the events funcs."""

    def __init__(
        self,
        parent: QtWidgets.QMainWindow,
        *args: any,
        **kwargs: any,
    ) -> None:
        """Construct the class."""
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.main_win = parent.main_win
        self.ui = parent.ui

    def _set_current_widget(self, widget: str) -> None:
        """Set a new current widget.

        Clears previous widget with the ClearPreviousWidget ctx manager.

        :param widget: The widget to switch to

        """
        with ClearPreviousWidget(self.parent):
            self.ui.stacked_widget.setCurrentWidget(getattr(self.ui, widget))

    def _message_box(self, message_box: str, *args: any, **kwargs: any) -> None:
        """Show a chosen message box with the given positional and keyword arguments.

        :param message_box: The message box type to show
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        """
        box = getattr(self.ui.message_boxes, message_box)
        box(*args, **kwargs)

    def _setup_vault_page(self, page: Optional[Vault] = None):
        """Set up and connect a new vault page

        :param page: Vault object containing the data which should be shown on the current page, defaults to None

        """
        self.ui.vault_widget = window.VaultWidget()
        self.ui.vault_stacked_widget.addWidget(self.ui.vault_widget.widget)

        if page:
            for data in VAULT_WIDGET_DATA:
                obj = getattr(self.ui.vault_widget.ui, data.name)
                method = getattr(obj, data.method)

                with contextlib.suppress(TypeError):
                    args = getattr(page, data.args)

                try:
                    method(str(args))
                except (TypeError, UnboundLocalError):
                    method()

        self.ui.vault_widget.ui.vault_update_btn.clicked.connect(
            self.update_vault_page_event,
        )
        self.ui.vault_widget.ui.vault_forward_tool_btn.clicked.connect(
            lambda: self.change_vault_page_event(1),
        )
        self.ui.vault_widget.ui.vault_backward_tool_btn.clicked.connect(
            lambda: self.change_vault_page_event(-1),
        )

        self.ui.vault_stacked_widget.setCurrentWidget(self.ui.vault_widget.widget)

    def _rebuild_vault_stacked_widget(self):
        """Rebuild ``self.ui.vault_stacked_widget``."""
        self.ui.vault_stacked_widget = QtWidgets.QStackedWidget(self.ui.vault)
        self.ui.vault_stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.ui.vault_stacked_widget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.ui.vault_stacked_widget.setObjectName("vault_stacked_widget")
        self.ui.vault_dummy_page1 = QtWidgets.QWidget()
        self.ui.vault_dummy_page1.setEnabled(False)
        self.ui.vault_dummy_page1.setObjectName("vault_dummy_page1")
        self.ui.vault_stacked_widget.addWidget(self.ui.vault_dummy_page1)
        self.ui.gridLayout_12.addWidget(self.ui.vault_stacked_widget, 0, 3, 6, 1)

    @property
    def _vault_widget_vault(self) -> Vault:
        """Return ``Vault object`` instantiated with the current vault widget values.

        Finds the new values by accessing the children objects of the current widget.
        The indexes point to the ``line_edit`` objects containing the string values.

        """
        children_objects = self.ui.vault_stacked_widget.currentWidget().children()
        return vaults.Vault(
            self.current_user.user_id,
            children_objects[1].text(),
            children_objects[3].text(),
            children_objects[6].text(),
            children_objects[9].text(),
            children_objects[12].text(),
            children_objects[15].text(),
        )

    @property
    def vault_stacked_widget_index(self) -> int:
        """Return the current ``vault_stacked_widget`` index."""
        return self.ui.vault_stacked_widget.currentIndex()

    @vault_stacked_widget_index.setter
    def vault_stacked_widget_index(self, i) -> None:
        """Set a new ``vault_stacked_widget_index``."""
        self.ui.vault_stacked_widget.setCurrentIndex(i)

    def home_event(self) -> None:
        """Switch to home widget."""
        self._set_current_widget("home")

    def login_event(self) -> None:
        """Switch to login widget and reset previous values."""
        self._set_current_widget("login")

    def login_user_event(self) -> None:
        """Try to login a user. If successful, show the account widget."""
        try:
            self.current_user = account.Account.login(
                self.ui.log_username_line_edit.text(),
                self.ui.log_password_line_edit.text(),
            )
        except AccountException:
            self._message_box("invalid_login_box", "Login")
        else:
            self.account_event()

    def register_event(self) -> None:
        """Switch to register widget and reset previous values."""
        self._set_current_widget("register_2")

    def register_user_event(self) -> None:
        """Try to register a user. If successful, show login widget."""
        try:
            self.current_user = account.Account.register(
                self.ui.reg_username_line.text(),
                self.ui.reg_password_line.text(),
                self.ui.reg_conf_pass_line.text(),
                self.ui.reg_email_line.text(),
            )
        except InvalidUsername:
            self._message_box("invalid_username_box", "Register")
        except InvalidPassword:
            self._message_box("invalid_password_box", "Register")
        except InvalidEmail:
            self._message_box("invalid_email_box", "Register")
        except UsernameAlreadyExists:
            self._message_box("username_already_exists_box", "Register")
        except EmailAlreadyExists:
            self._message_box("email_already_exists_box", "Register")
        except PasswordsDoNotMatch:
            self._message_box("passwords_do_not_match_box", "Register")
        else:
            self._message_box("account_creation_box")

    def forgot_password_event(self) -> None:
        """Switch to forgot password widget and reset previous email."""
        self._set_current_widget("forgot_password")

    def send_token_event(self) -> None:
        """Send token and switch to token page."""
        if credentials.Email.check_email_pattern(
            email := self.ui.forgot_pass_email_line.text(),
        ):
            self.ui.reset_token_submit_btn.setEnabled(False)
            credentials.Email.send_reset_email(email)
            self.ui.reset_token_submit_btn.setEnabled(True)

            self._message_box("reset_email_sent_box", "Forgot Password")
        else:
            self._message_box("invalid_email_box", "Forgot Password")

    def reset_token_event(self) -> None:
        """Switch to reset token page and reset previous values."""
        self._set_current_widget("reset_token")

    def submit_reset_token_event(self) -> None:
        """If submitted token is correct, proceed to password change widget."""
        if credentials.Token.check_token_existence(
            self.ui.reset_token_token_line.text(),
        ):
            self.reset_password_event()
        else:
            self._message_box("invalid_token_box", "Reset Password")

    def reset_password_event(self) -> None:
        """Move to reset password page."""
        self._set_current_widget("reset_password")

    def submit_reset_password_event(self) -> None:
        """Attempt to change user's password, show message box if something goes wrong, otherwise move to login page."""
        try:
            account.change_password(
                ...,
                self.ui.reset_pass_new_pass_line.text(),
                self.ui.reset_pass_conf_new_line.text(),
            )
        except InvalidPassword:
            self._message_box("invalid_password_box", "Reset Password")
        except PasswordsDoNotMatch:
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

    def get_generator(self) -> mouse_randomness.PwdGenerator:
        """Get Generator from current password params.

        :returns: PwdGenerator object

        """
        return mouse_randomness.PwdGenerator(
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
            self._message_box("no_options_generate_box", "Generator")
        else:
            self.parent.gen = self.get_generator()
            self.parent.collector.randomness_set = {*()}
            self.parent.pass_progress = 0
            self.ui.generate_pass_p2_prgrs_bar.setValue(self.parent.pass_progress)

            self._set_current_widget("generate_pass_phase2")

    def copy_password_event(self) -> None:
        """Copy generated password into clipboard."""
        clipboard.copy(self.ui.generate_pass_p2_final_pass_line.text())

    @decorators.login_required("account")
    def account_event(self) -> None:
        """Switch to account widget and set current user values."""
        self.ui.account_username_line.setText(self.current_user.username)
        self.ui.account_email_line.setText(self.current_user.email)
        self.ui.account_last_log_date.setText(
            f"Last login date: {self.current_user.last_login_date}.",
        )
        self.ui.account_pfp_pixmap_lbl.setPixmap(
            QtGui.QPixmap(self.current_user.profile_picture_path),
        )

        self._set_current_widget("account")

    def change_pfp_event(self) -> None:
        """Change profile picture of current user."""
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.parent,
            "Lightning Pass - Choose your new profile picture",
            str(pathlib.Path.home()),
            "Image files (*.jpg *.png)",
        )

        if fname:
            self.current_user.profile_picture = credentials.ProfilePicture.save_picture(
                pathlib.Path(fname),
            )

        self.account_event()

    def logout_event(self) -> None:
        """Logout current user."""
        self.current_user.update_last_login_date()
        # unlink current_user reference
        del self.current_user
        self.home_event()

    @decorators.login_required()
    def change_pass_event(self) -> None:
        """Change password for current user."""
        ...

    def edit_details_event(self) -> None:
        """Edit user details by changing them on their respective edit lines."""
        if self.current_user.username != (i := self.ui.account_username_line.text()):
            try:
                self.current_user.username = i
            except InvalidUsername:
                self._message_box("invalid_username_box", "Account")
            except UsernameAlreadyExists:
                self._message_box("username_already_exists_box", "Account")
            else:
                self._message_box("detail_updated_box", "Account", "username")

        if self.current_user.email != (i := self.ui.account_email_line.text()):
            try:
                self.current_user.email = i
            except InvalidEmail:
                self._message_box("invalid_email_box", "Account")
            except EmailAlreadyExists:
                self._message_box("email_already_exists_box", "Account")
            else:
                self._message_box("detail_updated_box", "Account", detail="email")

    @decorators.login_required("master password")
    def master_password_event(self) -> None:
        """Switch to master password widget."""
        self._set_current_widget("master_password")

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
        try:
            self.current_user.master_password = (
                self.ui.master_pass_current_pass_line.text(),
                self.ui.master_pass_master_pass_line.text(),
                self.ui.master_pass_conf_master_pass_line.text(),
            )
        except AccountDoesNotExist:
            self._message_box("invalid_login_box", "Master Password")
        except InvalidPassword:
            self._message_box(
                "invalid_password_box",
                "Master Password",
                item="master password",
            )
        except PasswordsDoNotMatch:
            self._message_box("passwords_do_not_match_box", "Master Password")
        else:
            self._message_box(
                "detail_updated_box",
                "Master Password",
                detail="master password",
            )

    @decorators.login_required()
    @decorators.master_password_required()
    def master_password_dialog_event(self) -> None:
        """Show an input dialog asking the user to enter their current master password.

        Either locks or unlocks the vault depending on the result

        """
        password = self.parent.ui.input_dialogs.master_password_dialog(
            "Vault",
            self.current_user.username,
        )

        if password and credentials.Password.authenticate_password(
            password, self.current_user.master_password
        ):
            self.current_user.vault_unlocked = True
            self._message_box("vault_unlocked_box")
        else:
            self.current_user.vault_unlocked = False
            self._message_box("invalid_login_box", "Vault")

    @decorators.login_required("vault")
    @decorators.master_password_required("vault")
    @decorators.vault_unlock_required("vault")
    def vault_event(self) -> None:
        """Switch to vault window."""
        self._rebuild_vault_stacked_widget()

        for page in self.current_user.vault_pages:
            self._setup_vault_page(page)

        self.ui.vault_username_lbl.setText(
            f"Current user: {self.current_user.username}",
        )
        self.ui.vault_date_lbl.setText(
            f"Last unlock date: {str(self.current_user.register_date)}",
        )

        self._set_current_widget("vault")

    def add_vault_page_event(self) -> None:
        """Add a new vault page.

        Adds new page if empty one was not found,
        switches to new and unused page if one like that exists.

        """
        if (page := self.current_user.vault_pages_int) == (
            count := self.ui.vault_stacked_widget.count() - 1
        ):
            # empty one not found -> create new one
            self._setup_vault_page()
            self.ui.vault_widget.ui.vault_page_lbl.setText(str(page))
        else:
            # empty one found -> switch to it
            self.vault_stacked_widget_index = count

    def remove_vault_page_event(self) -> None:
        """Remove the current vault page."""
        vaults.delete_vault(
            self.current_user.user_id,
            self.vault_stacked_widget_index - 1,
        )

        platform = self._vault_widget_vault.platform_name
        self.vault_event()
        self._message_box(
            "vault_page_deleted_box",
            platform,
            "Vault",
        )

    def vault_lock_event(self) -> None:
        """Lock the vault."""
        self.current_user.vault_unlocked = False
        self.account_event()

    def change_vault_page_event(self, index_change: int) -> None:
        """Handle changes on the vault window.

        :param index_change: Integer indicating how should the widget index be changed

        """
        if (new_index := self.vault_stacked_widget_index + index_change) > 0:
            # did not reach border, switch to new page
            self.vault_stacked_widget_index = new_index

    def update_vault_page_event(self) -> None:
        """Add a new vault tied to the current user.

        Checks if the vault previously existed and stores it.
        Used later to choose correct message box.

        """
        exists = vaults.get_vault(
            self.current_user.user_id,
            self._vault_widget_vault.vault_index,
        )

        try:
            vaults.update_vault(
                (
                    new_vault := vaults.Vault(
                        self.current_user.user_id,
                        self._vault_widget_vault.platform_name,
                        self._vault_widget_vault.website,
                        self._vault_widget_vault.username,
                        self._vault_widget_vault.email,
                        self._vault_widget_vault.password,
                        int(self._vault_widget_vault.vault_index),
                    )
                ),
            )
        except InvalidURL:
            self._message_box("invalid_url_box", "Vault")
        except InvalidEmail:
            self._message_box("invalid_email_box", "Vault")
        except VaultException:
            self._message_box("invalid_vault_box", "Vault")
        else:
            self.ui.vault_widget.ui.vault_password_line.clear()

            if exists:
                self._message_box(
                    "vault_updated_box",
                    "Vault",
                    self._vault_widget_vault.platform_name,
                    [
                        key
                        for key, val in zip(exists._fields, exists)
                        if not getattr(new_vault, str(key)) == val
                    ],
                )
            else:
                self._message_box(
                    "vault_created_box",
                    "Vault",
                    self._vault_widget_vault.platform_name,
                )

    def toggle_stylesheet_light(self, *args: any) -> None:
        """Change stylesheet to light mode."""
        if args:
            ...
        self.main_win.setStyleSheet("")

    def toggle_stylesheet_dark(self, *args: any) -> None:
        """Change stylesheet to dark mode."""
        if args:
            ...
        self.main_win.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))


__all__ = [
    "Events",
]
