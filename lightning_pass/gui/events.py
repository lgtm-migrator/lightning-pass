"""Module containing the Events class used for event handling."""
from __future__ import annotations

import contextlib
import functools
import itertools as it
import pathlib
from typing import TYPE_CHECKING

from PyQt5 import QtWidgets

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

import timeit


@functools.cache
def _ord(day: int) -> str:
    """Return given day in a human readable string and cache the result.

    :param day: The day integer

    """
    suffix = "th", "st", "nd", "rd"

    return str(day) + (
        suffix[div]
        if (div := day % 10) in (1, 2, 3) and day not in (11, 12, 13)
        else suffix[0]
    )


class Events:
    """Class with all of the event classes."""

    def __init__(self, parent: QMainWindow) -> None:
        """Construct the class."""
        self.parent = parent
        self.widget_util = WidgetUtil(parent)
        self.current_user = Account(0)

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.parent!r})"

    @property
    @functools.cache
    def home(self) -> HomeEvents:
        """Return the main event class."""
        return HomeEvents(self.parent)

    @property
    @functools.cache
    def account(self) -> AccountEvents:
        """Return the account event class."""
        return AccountEvents(self.parent)

    @property
    @functools.cache
    def generator(self) -> GeneratorEvents:
        """Return the generator event class."""
        return GeneratorEvents(self.parent)

    @property
    @functools.cache
    def vault(self) -> VaultEvents:
        """Return the vault event class."""
        return VaultEvents(self.parent)


class HomeEvents(Events):
    """Provide logic to events connected to basic actions."""

    __current_token: str

    def __init__(self, parent: QMainWindow) -> None:
        """Construct the class."""
        super().__init__(parent)

    @decorators.widget_changer
    def home(self) -> None:
        """Switch to home widget."""
        self.widget_util.current_widget = "home"

    main = home

    @decorators.widget_changer
    def login(self) -> None:
        """Switch to login widget and reset previous values."""
        self.widget_util.current_widget = "login"

    def login_user(self) -> None:
        """Try to login a user. If successful, show the account widget."""
        # need to clean up data about previous users' vault platforms if there are any
        self.parent.events.account.logout(home=False)
        try:
            self.parent.events.current_user = Account.login(
                self.parent.ui.log_username_line_edit.text(),
                self.parent.ui.log_password_line_edit.text(),
            )
        except AccountException:
            self.widget_util.message_box("invalid_login_box", "Login")
        else:
            self.parent.events.account.main()

    @decorators.widget_changer
    def register_2(self) -> None:
        """Switch to register widget and reset previous values."""
        self.widget_util.current_widget = "register_2"

    def register_user(self) -> None:
        """Try to register a user. If successful, show login widget."""
        try:
            self.parent.events.current_user = Account.register(
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

    @decorators.widget_changer
    def forgot_password(self) -> None:
        """Switch to forgot password widget and reset previous email."""
        self.widget_util.current_widget = "forgot_password"

    @decorators.widget_changer
    def reset_token(self) -> None:
        """Switch to reset token page and reset previous values."""
        self.widget_util.current_widget = "reset_token"

    def send_token(self) -> None:
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

    def submit_reset_token(self) -> None:
        """If submitted token is correct, proceed to password change widget."""
        if Account.credentials.validate_token(
            token := self.parent.ui.reset_token_token_line.text(),
        ):
            self.__current_token = token
            self.reset_password()
        else:
            self.widget_util.message_box("invalid_token_box", "Reset Password")

    @decorators.widget_changer
    def reset_password(self) -> None:
        """Switch to the reset password widget."""
        self.widget_util.current_widget = "reset_password"

    def reset_password_submit(self) -> None:
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


class AccountEvents(Events):
    """Provide logic to events connected to account."""

    def __init__(self, parent: QMainWindow) -> None:
        """Construct the class."""
        super().__init__(parent)

    @decorators.widget_changer
    @decorators.login_required(page_to_access="account")
    def account(self) -> None:
        """Switch to account widget and set current user values."""
        self.parent.ui.account_username_line.setText(
            self.parent.events.current_user.username,
        )
        self.parent.ui.account_email_line.setText(self.parent.events.current_user.email)

        date = self.parent.events.current_user.current_login_date
        try:
            text = f"Last login date: {_ord(date.day)} {date:%b. %Y, %H:%M}"
        except TypeError:
            text = "Last login date: None"
        self.parent.ui.account_last_log_date.setText(text)

        self.parent.ui.account_pfp_pixmap_lbl.setPixmap(
            self.parent.events.current_user.profile_picture_pixmap(),
        )

        self.widget_util.current_widget = "account"

    main = account

    @decorators.widget_changer
    @decorators.login_required(page_to_access="change password")
    def change_password(self) -> None:
        """Change password for current user."""
        self.widget_util.current_widget = "change_password"

    @decorators.login_required(page_to_access="change password")
    def submit_change_password(self) -> None:
        """Change user's password.

        Show message box if something goes wrong, otherwise move to login page.

        """
        try:
            self.parent.events.current_user.password = (
                self.parent.events.current_user.credentials.PasswordData(
                    self.parent.events.current_user.password,
                    self.parent.ui.change_password_current_pass_line.text(),
                    self.parent.ui.change_password_new_pass_line.text(),
                    self.parent.ui.change_password_conf_new_line.text(),
                )
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
            self.change_password()

    def change_pfp(self) -> None:
        """Change profile picture of current user."""
        # dump used file filter
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.parent,
            "Lightning Pass - Choose your new profile picture",
            str(pathlib.Path.home()),
            "Image files (*.jpg *.png)",
        )
        if fname:
            self.parent.events.current_user.profile_picture = (
                self.parent.events.current_user.credentials.save_picture(
                    pathlib.Path(fname),
                )
            )
            self.parent.ui.account_pfp_pixmap_lbl.setPixmap(
                self.parent.events.current_user.profile_picture_pixmap(),
            )

    def logout(self, _=None, home: bool = True) -> None:
        """Logout current user.

        :param _: Dump the bool value passed in by the qt connection
        :param home: Whether to redirect user to the home page after logging out.

        """
        self.widget_util.clear_account_page()
        self.widget_util.clear_platform_actions()
        self.widget_util.clear_vault_stacked_widget()
        with contextlib.suppress(AttributeError):
            delattr(self, "current_user")
        if home:
            self.parent.events.home.main()

    def edit_details(self) -> None:
        """Edit user details by changing them on their respective edit lines."""
        if not self.parent.events.current_user.username == (
            name := self.parent.ui.account_username_line.text()
        ):
            try:
                self.parent.events.current_user.username = name
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

        if not self.parent.events.current_user.email == (
            email := self.parent.ui.account_email_line.text()
        ):
            try:
                self.parent.events.current_user.email = email
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

    @decorators.widget_changer
    @decorators.login_required(page_to_access="master password")
    def master_password(self) -> None:
        """Switch to master password widget.

        If master password already exists, user is required to unlock vault to access this page.
        By unlocking the vault, access to the master key is provided.
        The key will be used while rehashing the saved vault passwords (if master password is changed).

        """
        if not self.parent.events.current_user.master_key:
            self.widget_util.current_widget = "master_password"
        elif (
            self.parent.events.current_user.vault_unlocked
            and self.parent.events.current_user.vault_pages()
        ):
            self.widget_util.current_widget = "master_password"
        else:
            self.widget_util.message_box(
                "vault_unlock_required_box",
                "master password",
                page="master password",
            )

    def master_password_submit(self) -> None:
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
        prev_key = self.parent.events.current_user.master_key
        try:
            self.parent.events.current_user.master_key = (
                self.parent.events.current_user.credentials.PasswordData(
                    self.parent.events.current_user.password,
                    self.parent.ui.master_pass_current_pass_line.text(),
                    self.parent.ui.master_pass_master_pass_line.text(),
                    self.parent.ui.master_pass_conf_master_pass_line.text(),
                )
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
            for vault in self.parent.events.current_user.vault_pages(key=prev_key):
                self.widget_util.rehash_vault_password(vault)

            self.widget_util.message_box(
                "detail_updated_box",
                "Master Password",
                detail="Master password",
            )
            self.main()

    @decorators.login_required
    @decorators.master_password_required
    def master_password_dialog(self) -> None:
        """Show an input dialog asking the user to enter their current master password.

        Either locks or unlocks the vault depending on the result.

        """
        password = self.parent.ui.input_dialogs.master_password_dialog(
            "Vault",
            self.parent.events.current_user.username,
        )

        if not self.parent.events.current_user.pwd_hashing.auth_derived_key(
            password,
            self.parent.events.current_user.hashed_vault_credentials,
        ):
            self.parent.events.current_user.vault_unlocked = False
            self.widget_util.message_box("invalid_login_box", "Vault")
        else:
            self.parent.events.current_user.vault_unlocked = True
            self.parent.events.current_user._master_key_str = password
            self.widget_util.message_box("vault_unlocked_box")


class GeneratorEvents(Events):
    """Provide logic to events connected to password generation."""

    def __init__(self, parent: QMainWindow) -> None:
        """Construct the class."""
        super().__init__(parent)

    @decorators.widget_changer
    def generate_pass(self) -> None:
        """Switch to first password generation widget and reset previous password options."""
        self.widget_util.current_widget = "generate_pass"

    main = generate_pass

    @decorators.widget_changer
    def generate_pass_phase2(self) -> None:
        """Switch to the second password generation widget and reset previous values.

        If no password options were checked, shows message box letting the user know about it.

        """
        if not self.parent.ui.generate_pass_p2_tracking_lbl.hasMouseTracking():
            self.widget_util.mouse_randomness.MouseTracker.setup_tracker(
                self.parent.ui.generate_pass_p2_tracking_lbl,
                self.parent.on_position_changed,
            )

        if not any(
            val
            for val in self.widget_util.password_options
            # exclude length
            if isinstance(val, bool)
        ):
            self.widget_util.message_box("no_options_generate_box", "Generator")
        else:
            self.parent.gen = self.widget_util.get_generator()
            self.parent.pass_progress = 0
            self.parent.ui.generate_pass_p2_prgrs_bar.setValue(
                self.parent.pass_progress,
            )

            self.widget_util.current_widget = "generate_pass_phase2"

    def generate_pass_again(self) -> None:
        """Re-instantiate a new generator object with the same options.

        Reset previous generation values.

        """
        self.parent.pass_progress = 0
        self.parent.ui.generate_pass_p2_prgrs_bar.setValue(self.parent.pass_progress)
        self.parent.ui.generate_pass_p2_final_pass_line.clear()
        self.parent.gen = self.widget_util.mouse_randomness.PwdGenerator(
            self.parent.gen.options,
        )


class VaultEvents(Events):
    """Provide logic to events connected to vault."""

    def __init__(self, parent: QMainWindow) -> None:
        """Construct the class."""
        super().__init__(parent)

    @decorators.login_required(page_to_access="vault")
    @decorators.master_password_required(page_to_access="vault")
    @decorators.vault_unlock_required(page_to_access="vault")
    def vault(
        self,
        _=None,
        switch: bool = True,
        previous_index: int | None = None,
    ) -> None:
        """Switch to vault window.

        :param _: Dump the bool value passed in by the qt connection
        :param switch: Whether to switch to the vault page or only set it up
        :param previous_index: The index of the window before rebuilding

        """
        now = timeit.default_timer()

        self.widget_util.clear_vault_stacked_widget()

        pages = self.parent.events.current_user.vault_pages()

        try:
            page = next(pages)
        except StopIteration:
            self.widget_util.setup_vault_widget()
        else:
            for page in it.chain((page,), pages):
                self.widget_util.setup_vault_widget(page)

        self.parent.ui.menu_platforms.setEnabled(True)

        self.parent.ui.vault_username_lbl.setText(
            f"Current user: {self.parent.events.current_user.username}",
        )

        date = self.parent.events.current_user.current_vault_unlock_date
        try:
            text = f"Last unlock date: {_ord(date.day)} {date:%b. %Y, %H:%M}"
        except TypeError:
            text = "Last unlock date: None"
        self.parent.ui.vault_date_lbl.setText(text)

        if switch:
            self.widget_util.current_widget = "vault"

        if previous_index:
            self.parent.ui.vault_stacked_widget.setCurrentIndex(previous_index)

        print(timeit.default_timer() - now)

    main = vault

    def add_vault_page(self) -> None:
        """Add a new vault page.

        Add new page if empty one was not found,
        switch to new and unused page if one like that exists.

        """
        if (high := self.widget_util.number_of_real_vault_pages) == (
            self.parent.ui.vault_stacked_widget.count()
        ):
            # empty one not found -> create new one
            self.widget_util.setup_vault_widget()
            self.parent.ui.vault_stacked_widget.currentWidget().findChild(
                QtWidgets.QLCDNumber,
            ).display(high + 1)
        else:
            # empty one found -> switch to it
            self.widget_util.vault_stacked_widget_index = high + 1

    def remove_vault_page(self) -> None:
        """Remove the current vault page."""
        if (
            self.widget_util.number_of_real_vault_pages
        ) < self.widget_util.vault_stacked_widget_index:
            # user tried to remove a page which has not yet been submitted to the database
            # -> just clear the fields
            self.widget_util.clear_current_vault_page()
            return

        platform = self.widget_util.vault_widget_vault.platform_name
        text = self.parent.ui.input_dialogs.confirm_vault_deletion_dialog(
            "Vault",
            platform,
        )
        if text == "CONFIRM":
            self.parent.events.current_user.vaults.delete_vault(
                self.parent.events.current_user.user_id,
                self.widget_util.vault_stacked_widget_index,
            )

            getattr(self.parent.ui, f"action_{platform}").deleteLater()

            self.widget_util.message_box(
                "vault_page_deleted_box",
                "Vault",
                platform,
            )

            self.main()

    def lock_vault(self) -> None:
        """Lock the vault of the current user."""
        self.current_user.vault_unlocked = False
        self.widget_util.clear_vault_stacked_widget()
        self.widget_util.clear_platform_actions()
        self.parent.events.account.main()

    def update_vault_page(self) -> None:
        """Add a new vault tied to the current user.

        Checks if the vault previously existed and stores it.
        Used later to choose correct message box.

        """
        vaults = self.parent.events.current_user.vaults

        previous_vault = vaults.get_vault(
            self.parent.events.current_user.user_id,
            self.widget_util.vault_widget_vault.vault_index,
        )

        try:
            vaults.update_vault(
                (
                    new_vault := vaults.Vault(
                        self.parent.events.current_user.user_id,
                        self.widget_util.vault_widget_vault.platform_name,
                        self.widget_util.vault_widget_vault.website,
                        self.widget_util.vault_widget_vault.username,
                        self.widget_util.vault_widget_vault.email,
                        self.parent.events.current_user.encrypt_vault_password(
                            new_pass := self.widget_util.vault_widget_vault.password,
                        ),
                        int(self.widget_util.vault_stacked_widget_index),
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
            new_vault = vaults.Vault(*new_vault[:5], new_pass, *new_vault[6:])

            if previous_vault:
                getattr(
                    self.parent.ui,
                    f"action_{previous_vault.platform_name}",
                ).setText(new_vault.platform_name)

                previous_vault = vaults.Vault(
                    *previous_vault[:5],
                    self.parent.events.current_user.decrypt_vault_password(
                        previous_vault.password,
                    ),
                    *previous_vault[6:],
                )

                updated_details = [
                    key
                    for key, val in zip(previous_vault._fields, previous_vault)
                    if not getattr(new_vault, str(key)) == val
                ]

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

                self.widget_util.setup_vault_page(new_vault)

    def change_vault_page(self, index: int, calculate: bool = False):
        """Handle changes on the vault stacked widget.

        :param index: The index to access
        :param calculate: If the index should be changed by the given amount

        """
        if calculate:
            self.widget_util.vault_stacked_widget_index += index
        else:
            self.widget_util.vault_stacked_widget_index = index

        if not self.widget_util.current_widget.objectName() == (v := "vault"):
            self.widget_util.current_widget = v


__all__ = [
    "Events",
]
