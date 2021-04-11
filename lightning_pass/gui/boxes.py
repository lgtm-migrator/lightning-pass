"""Module containing the MessageBoxes and InputDialogs classes

Used for showing information to the user.

"""
import contextlib
import functools
from typing import Callable, NamedTuple, Optional, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)


def partial_factory(func: Callable, *args: Optional[any], **kwargs: Optional[any]):
    """Return a new partial function.

    :param func: The function which will be made partial
    :param args: Optional positional arguments
    :param kwargs: Optional keyword arguments

    :returns: the partial function

    """
    return functools.partial(func, *args, **kwargs)


def event_handler_factory(options: dict[str, Callable[[], None]]) -> Callable[[], None]:
    """Generate a new event handler.

    :param options: Dictionary containing keys and functions tied to them.

    :returns: the event handler

    """

    def handler(btn: QPushButton) -> None:
        """Handle clicks on message box window.

        :param btn: Clicked button

        """
        with contextlib.suppress(KeyError):
            event = options[btn.text()]
        with contextlib.suppress(UnboundLocalError):
            event()

    return handler


class MessageBoxOperation(NamedTuple):
    func: str
    args: Optional[
        Union[
            str,
            QMessageBox.Icon,
            QMessageBox.StandardButtons,
            QMessageBox.StandardButton,
            Callable,
        ]
    ] = None


class MessageBoxes(QWidget):
    """This class holds the functionality to show various message boxes."""

    __slots__ = ("main_win", "parent", "events", "title")

    def __init__(self, child: QMainWindow, parent: QMainWindow) -> None:
        """Class constructor."""
        super().__init__(parent)
        self.main_win = child
        self.parent = parent
        self.events = parent.events
        self.title = child.windowTitle()

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.main_win}, {self.parent})"

    def message_box_factory(
        self,
        parent_lbl: str,
        text: str,
        icon: Optional[QMessageBox.Icon] = QMessageBox.NoIcon,
        # rest must be passed in as a keyword arguments
        *,
        informative_text: str = None,
        standard_buttons: Union[
            QMessageBox.StandardButtons,
            QMessageBox.StandardButton,
        ] = QMessageBox.Ok,
        default_button: QMessageBox.StandardButton = QMessageBox.Ok,
        event_handler: Callable = None,
    ) -> QMessageBox:
        """Return a message box initialized with the given params.

        :param parent_lbl: Specifies which window instantiated the new message box
        :param text: Main text to be displayed on the message box
        :param icon: Message box icon type, defaults to QMessageBox.Warning
        :param informative_text: Additional text to appear below the root text, defaults to None
        :param standard_buttons: Extra buttons to be shown on the message box, defaults to None
        :param default_button: Default button, defaults to None
        :param event_handler: Handler for clicks on buttons, defaults to None

        :returns: the message box

        """
        box = QMessageBox(self.main_win)

        operations = {
            MessageBoxOperation("setWindowTitle", f"{self.title} - {parent_lbl}"),
            MessageBoxOperation("setText", text),
            MessageBoxOperation("setIcon", icon),
            MessageBoxOperation("setInformativeText", informative_text),
            MessageBoxOperation("setStandardButtons", standard_buttons),
            MessageBoxOperation("setDefaultButton", default_button),
        }

        for operation in operations:
            getattr(box, operation.func)(operation.args)
        with contextlib.suppress(TypeError):
            box.buttonClicked.connect(event_handler)

        box.setTextFormat(Qt.RichText)

        return box

    def _invalid_item_box(self, item: str, parent_lbl: str) -> message_box_factory:
        """Show message box indicating that the entered value is not correct.

        :param str item: Specifies which detail was incorrect
        :param str parent_lbl: Specifies which window instantiated current box

        """
        return partial_factory(
            self.message_box_factory,
            parent_lbl,
            f"This {item} is invalid.",
            QMessageBox.Warning,
        )

    def _item_already_exists_box(
        self,
        item: str,
        parent_lbl: str,
    ) -> message_box_factory:
        """Handle message boxes with information about existence of entered values.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        return partial_factory(
            self.message_box_factory,
            parent_lbl,
            f"This {item} already exists. Please use different {item}.",
            QMessageBox.Warning,
        )

    def _yes_no_box(self, handler, default_btn: str = "No") -> message_box_factory:
        """Return a partially initialized message box with yes and no buttons.

        :param default_btn: Which button should me the default one, defaults to "No"
        :param handler: Event handler for click on the two yes | no buttons

        """
        return partial_factory(
            self.message_box_factory,
            standard_buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=getattr(QMessageBox, default_btn),
            event_handler=handler,
        )

    def invalid_username_box(self, parent_lbl: str) -> None:
        """Show invalid username message box.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        box = self._invalid_item_box("username", parent_lbl)
        box(
            informative_text="Username be at least 5 characters long and mustn't contain any special characters.",
        ).exec()

    def invalid_password_box(self, parent_lbl: str, item: str = "password") -> None:
        """Show invalid password message box.

        :param parent_lbl: Specifies which window instantiated current box
        :param item: Optional argument to change the invalid item
            (should be connected to password due to informative text), defaults to "password"

        """
        box = self._invalid_item_box(item, parent_lbl)
        item = item[0].upper() + item[1::1]
        box(
            informative_text=(
                f"""{item} must be at least 8 characters long,
contain at least 1 capital letter,
contain at least 1 number and
contain at least one special character."""
            ),
        ).exec()

    def invalid_email_box(self, parent_lbl: str) -> None:
        """Show invalid email message box.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        self._invalid_item_box("email", parent_lbl)().exec()

    def invalid_token_box(self, parent_lbl: str) -> None:
        """Show invalid token message box.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.forgot_password_event},
        )

        box = self._yes_no_box(event_handler, "Yes")
        box(
            parent_lbl,
            "This token is invalid",
            QMessageBox.Warning,
            informative_text="Would you like to generate a token?",
        ).exec()

    def invalid_url_box(self, parent_lbl: Optional[str] = "Vault") -> None:
        """Show invalid url message box.

        :param parent_lbl: Specifies which window instantiated the current box, defaults to "Vault"

        """
        self._invalid_item_box("website URL", parent_lbl)().exec()

    def username_already_exists_box(self, parent_lbl: str) -> None:
        """Show username already exists message box.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        self._item_already_exists_box("username", parent_lbl)().exec()

    def email_already_exists_box(self, parent_lbl: str) -> None:
        """Show email already exists message box.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        self._item_already_exists_box("email", parent_lbl)().exec()

    def passwords_do_not_match_box(
        self,
        parent_lbl: str,
        item: str = "Passwords",
    ) -> None:
        """Show passwords do not match message box.

        :param parent_lbl: Specifies which window instantiated current box
        :param item: Alter the message a bit

        """
        self.message_box_factory(
            parent_lbl,
            f"{item} don't match.",
            QMessageBox.Warning,
            informative_text="Please try again.",
        ).exec()

    def login_required_box(self, parent_lbl: str, page: Optional[str] = None) -> None:
        """Show message box indicating that password can't be generated with current case type option.

        :param parent_lbl: Specifies which window instantiated current box
        :param page: The page which the user tried to access, defaults to None

        """
        text = (
            f"Please log in to access the {page} page."
            if page
            else "Please log in to access that page."
        )

        box = self._yes_no_box(
            event_handler_factory({"&Yes": self.events.login_event}),
            "No",
        )
        box(
            parent_lbl,
            text,
            QMessageBox.Warning,
            informative_text="Would you like to move to the login page?",
        ).exec()

    def invalid_login_box(self, parent_lbl: str) -> None:
        """Show invalid login message box.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.forgot_password_event},
        )

        box = self._yes_no_box(event_handler, "No")
        box(
            parent_lbl,
            "Could not authenticate an account with the given credentials.",
            QMessageBox.Warning,
            informative_text="Forgot password?",
        ).exec()

    def invalid_vault_box(self, parent_lbl: Optional[str] = "Vault") -> None:
        """Show a message box indicating the vault details are not correct.

        :param parent_lbl: Specifies which window instantiated the current box, defaults to "Vault"

        """
        self.message_box_factory(
            parent_lbl,
            "The vault details can't contain empty fields.",
            QMessageBox.Warning,
        ).exec()

    def account_creation_box(self, parent_lbl: Optional[str] = "Register") -> None:
        """Show successful account creation message box.

        :param str parent_lbl: Specifies which window instantiated current box, defaults to "Register"

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.login_event, "&No": self.events.register_event},
        )

        box = self._yes_no_box(event_handler, "Yes")
        box(
            parent_lbl,
            "Account successfully created.",
            QMessageBox.Question,
            informative_text="Would you like to move to the login page?",
        ).exec()

    def detail_updated_box(
        self,
        parent_lbl: str,
        detail: str,
    ) -> None:
        """Show message box indicating that a user details has been successfully updated.

        :param str detail: Specifies which detail was updated
        :param str parent_lbl: Specifies which window instantiated current box

        """
        self.message_box_factory(
            parent_lbl,
            f"Your {detail} has been successfully updated!",
        ).exec()

    def reset_email_sent_box(self, parent_lbl: str) -> None:
        """Show message box indicating that a reset email has been sent.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        box = self._yes_no_box(
            event_handler_factory({"&Yes": self.events.reset_token_event}),
            "Yes",
        )
        box(
            parent_lbl,
            "The reset email has been sent.",
            QMessageBox.Question,
            informative_text="Would you like to move to the token page now?",
        ).exec()

    def no_options_generate_box(self, parent_lbl: str) -> None:
        """Show a message box indicating that password can't be generated without a single option.

        :param str parent_lbl: Specifies which window instantiated current box

        """
        box = self._yes_no_box(
            event_handler_factory({"&Yes": self.events.generate_pass_event}),
            "No",
        )
        box(
            parent_lbl,
            "Password can't be generate without a single parameter.",
            QMessageBox.Warning,
            informative_text="Would you like to reset the values?",
        ).exec()

    def master_password_required_box(
        self,
        parent_lbl: Optional[str] = "Master Password",
        page: Optional[str] = None,
    ) -> None:
        """Show message box indicating that the current user needs to setup master password to proceed.

        :param parent_lbl: The window which instantiated the current box, defaults to "Master Password"
        :param page: The page which the user tried to access

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.master_password_event},
        )

        text = (
            f"You need to set up a master password to access the {page} page."
            if page
            else "You need to set up a master password to proceed."
        )

        box = self._yes_no_box(event_handler, "No")
        box(
            parent_lbl,
            text,
            QMessageBox.Warning,
            informative_text="Would you like to move to the master password page?",
        ).exec()

    def vault_unlock_required_box(
        self,
        parent_lbl: Optional[str] = "Vault",
        page: Optional[str] = None,
    ) -> None:
        """Show a message box indicating that the current user needs unlock the master vault to proceed.

        :param parent_lbl: Specifies which window instantiated the current box
        :param page: The page which the user tried to access

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.master_password_dialog_event},
        )

        text = (
            f"Please unlock your vault to access the {page} page."
            if page
            else "Please unlock your vault to access that page."
        )

        box = self._yes_no_box(event_handler, "Yes")
        box(
            parent_lbl,
            text,
            QMessageBox.Warning,
            informative_text="Would you like to unlock it?",
        ).exec()

    def vault_unlocked_box(self, parent_lbl: Optional[str] = "Vault"):
        """Show a message box indicating that the vault of the current user has been unlocked.

        :param parent_lbl: Specifies which window instantiated the current box, defaults to "Vault"

        """
        box = self._yes_no_box(
            event_handler_factory({"&Yes": self.events.vault_event}),
            "Yes",
        )
        box(
            parent_lbl,
            "Your vault has been unlocked.",
            QMessageBox.Question,
            informative_text="Would you like to move to the vault page?",
        ).exec()

    def vault_created_box(self, parent_lbl: str, platform: str) -> None:
        """Show a message box indicating that a new vault page has been created.

        :param parent_lbl: Specifies which windows instantiated the current box
        :param platform: The platform affected by this change

        """
        self.message_box_factory(
            parent_lbl,
            f"Vault page for {platform} created.",
        ).exec()

    def vault_page_deleted_box(
        self,
        parent_lbl: str,
        platform: str,
    ):
        """Show a message box indicating that the current vault page has been deleted.

        :param platform: The platform of the deleted page
        :param parent_lbl: Specifies which window instantiated the current box, defaults to "Vault"

        """
        self.message_box_factory(
            parent_lbl,
            f"Vault page for {platform} deleted.",
        ).exec()

    def vault_updated_box(
        self,
        parent_lbl: str,
        platform: str,
        updated_values: list[str],
    ) -> None:
        """Show a message box indicating that a new vault page has been updated.

        :param parent_lbl: Specifies which windows instantiated the current box
        :param platform: The platform affected by this change
        :param updated_values: A ``list`` containing the values that have been updated

        """
        try:
            updated_values[0] = updated_values[0].capitalize()
        except IndexError:
            # first element/character did not exist, return without showing anything
            return

        informative = (
            f"""{', '.join(updated_values[:-1])} and {updated_values[-1]} have been successfully updated."""
            if len(updated_values) > 1
            else f"{updated_values[0]} has been successfully updated."
        )

        self.message_box_factory(
            parent_lbl,
            f"Vault page for {platform} updated.",
            informative_text=informative,
        ).exec()


class InputDialogs(QWidget):

    __slots__ = ("events", "main_win", "title")

    def __init__(self, child: QMainWindow, parent: QMainWindow) -> None:
        """Class constructor."""
        super().__init__(parent)
        self.events = parent.events
        self.main_win = child
        self.title = child.windowTitle()

    def _input_password_dialog(
        self,
        parent_lbl: str,
        account_username: str,
        password_type: str,
    ) -> str:
        """Show a general password input dialog.

        :param parent_lbl: Specifies which windows instantiated the current box
        :param account_username: Username of the account for which we're getting the password
        :param password_type: Specifies which kind of password should be put into the dialog

        """
        password, i = QInputDialog.getText(
            self.main_win,
            parent_lbl,
            f"{password_type} for {account_username}:",
            QLineEdit.Password,
        )
        return password if i else ""

    def master_password_dialog(
        self,
        parent_lbl: str,
        account_username: str,
    ) -> Union[str, bool]:
        """Show a dialog asking user to enter their master password.

        :param parent_lbl: The window which instantiated the current dialog
        :param account_username: The username of the current user

        """
        return self._input_password_dialog(parent_lbl, account_username, "Password")

    def confirm_vault_deletion_dialog(self, parent_lbl: str, platform: str):
        """Show a dialog asking user to enter their master password.

        :param parent_lbl: The window which instantiated the current dialog
        :param platform: The platform which might be deleted

        """
        dialog = QInputDialog(self.main_win)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setWindowTitle(parent_lbl)
        dialog.setLabelText(
            f'All of the data connected to {platform} will be permanently deleted.\nType in "CONFIRM" to proceed:',
        )
        dialog.exec()
        return dialog.textValue()


__all__ = [
    "InputDialogs",
    "MessageBoxOperation",
    "MessageBoxes",
    "event_handler_factory",
    "partial_factory",
]
