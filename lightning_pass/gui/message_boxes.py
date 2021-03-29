"""Module containing the MessageBoxes class used for showing various message boxes."""
import contextlib
import functools
from typing import Any, Callable, Optional, Union

from PyQt5.QtWidgets import (
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)


def partial_factory(func: Callable, *args: Optional[Any], **kwargs: Optional[Any]):
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


class MessageBoxes(QWidget):
    """This class holds the functionality to show various message boxes."""

    def __init__(self, child: QMainWindow, parent: QMainWindow) -> None:
        """Class constructor."""
        super().__init__(parent)
        self.events = parent.events
        self.main_win = child
        self.title = "Lightning Pass"

    def message_box_factory(
        self,
        parent: str,
        text: str,
        icon: QMessageBox.Icon,
        informative_text: str = None,
        standard_buttons: Union[
            QMessageBox.StandardButtons,
            QMessageBox.StandardButton,
        ] = None,
        default_button: QMessageBox.StandardButton = None,
        event_handler: Callable = None,
    ) -> QMessageBox:
        """Return a message box initialized with the given params.

        :param parent: Specifies which window instantiated the new message box
        :param text: Main text to be displayed on the message box
        :param icon: Message box icon type
        :param informative_text: Additional text, defaults to None
        :param standard_buttons: Extra buttons to be shown on the message box, defaults to None
        :param default_button: Default button, defaults to None
        :param event_handler: Handler for clicks on buttons, defaults to None

        :returns: the message box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText(text)
        box.setIcon(icon)
        box.setInformativeText(informative_text)

        with contextlib.suppress(TypeError):
            box.setStandardButtons(standard_buttons)
            box.setDefaultButton(default_button)
            box.buttonClicked.connect(event_handler)

        return box

    def _invalid_item_box(self, item: str, parent: str) -> message_box_factory:
        """Show message box indicating that the entered value is not correct.

        :param str item: Specifies which detail was incorrect
        :param str parent: Specifies which window instantiated current box

        """
        return partial_factory(
            self.message_box_factory,
            parent,
            f"This {item} is invalid.",
            QMessageBox.Warning,
        )

    def _item_already_exists_box(self, item: str, parent: str) -> message_box_factory:
        """Handle message boxes with information about existence of entered values.

        :param str parent: Specifies which window instantiated current box

        """
        return partial_factory(
            self.message_box_factory,
            parent,
            f"This {item} already exists. Please use different {item}.",
            QMessageBox.Warning,
        )

    def _yes_no_box(
        self, default_btn: QMessageBox.StandardButton, handler
    ) -> message_box_factory:
        """Return a partially initialized message box with yes and no buttons.

        :param handler: Event handler for click on the two yes | no buttons

        """
        return partial_factory(
            self.message_box_factory,
            standard_buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=default_btn,
            event_handler=handler,
        )

    def invalid_username_box(self, parent: str) -> None:
        """Show invalid username message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = self._invalid_item_box(item="username", parent=parent)
        box(informative_text="Username be at least 5 characters long.").exec_()

    def invalid_password_box(self, parent: str) -> None:
        """Show invalid password message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = self._invalid_item_box(item="password", parent=parent)
        box(
            informative_text=(
                """Password must be at least 8 characters long,
contain at least 1 capital letter,
contain at least 1 number and
contain at least one special character."""
            )
        ).exec_()

    def invalid_email_box(self, parent: str) -> None:
        """Show invalid email message box.

        :param str parent: Specifies which window instantiated current box

        """
        self._invalid_item_box(item="email", parent=parent)().exec_()

    def invalid_token_box(self, parent: str) -> None:
        """Show invalid token message box.

        :param str parent: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.forgot_password_event}
        )

        box = self._yes_no_box(QMessageBox.Yes, event_handler)
        box(
            parent=parent,
            text="This token is invalid",
            icon=QMessageBox.Warning,
            informative_text="Would you like to generate a token?",
        ).exec_()

    def username_already_exists_box(self, parent: str) -> None:
        """Show username already exists message box.

        :param str parent: Specifies which window instantiated current box

        """
        self._item_already_exists_box(item="username", parent=parent)().exec_()

    def email_already_exists_box(self, parent: str) -> None:
        """Show email already exists message box.

        :param str parent: Specifies which window instantiated current box

        """
        self._item_already_exists_box(item="email", parent=parent)().exec_()

    def passwords_do_not_match_box(self, parent: str) -> None:
        """Show passwords do not match message box.

        :param str parent: Specifies which window instantiated current box

        """
        self.message_box_factory(
            parent,
            "Passwords don't match.",
            QMessageBox.Warning,
            informative_text="Please try again.",
        ).exec_()

    def account_creation_box(self, parent: str) -> None:
        """Show successful account creation message box.

        :param str parent: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.login_event, "&No": self.events.register_event},
        )

        box = self._yes_no_box(QMessageBox.Yes, event_handler)
        box(
            parent=parent,
            text="Account successfully created.",
            icon=QMessageBox.Question,
            informative_text="Would you like to move to the login page?",
        ).exec_()

    def invalid_login_box(self, parent: str) -> None:
        """Show invalid login message box.

        :param str parent: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory(
            {"&Yes": self.events.forgot_password_event}
        )

        box = self._yes_no_box(QMessageBox.Yes, event_handler)
        box(
            parent=parent,
            text="Invalid login details.",
            icon=QMessageBox.Warning,
            informative_text="Forgot password?",
        ).exec_()

    def login_required_box(self, parent: str) -> None:
        """Show message box indicating that password can't be generated with current case type option.

        :param str parent: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory({"&Yes": self.events.login_event})

        box = self._yes_no_box(QMessageBox.No, event_handler)
        box(
            parent=parent,
            text="Please log in to access that page.",
            icon=QMessageBox.Warning,
            informative_text="Would you like to move to the login page?",
        ).exec_()

    def detail_updated_box(
        self,
        parent: str,
        detail: str,
    ) -> None:
        """Show message box indicating that a user details has been successfully updated.

        :param str detail: Specifies which detail was updated
        :param str parent: Specifies which window instantiated current box

        """
        self.message_box_factory(
            parent,
            f"Your {detail} has been successfully updated!",
            QMessageBox.Question,
        ).exec_()

    def reset_email_sent_box(self, parent: str) -> None:
        """Show message box indicating that a reset email has been sent.

        :param str parent: Specifies which window instantiated current box

        """
        event_handler = event_handler_factory({"&Yes": self.events.reset_token_event})

        box = self._yes_no_box(QMessageBox.Yes, event_handler)
        box(
            parent=parent,
            text="The reset email has been sent.",
            icon=QMessageBox.Question,
            informative_text="Would you like to move to the token page now?",
        ).exec_()

    def no_options_generate(self, parent: str) -> None:
        """Show a message box indicating that password can't be generated without a single option.

        :param str parent: Specifies which window instantiated current box

        """
        self.message_box_factory(
            parent,
            "Password can't be generate without a single parameter.",
            QMessageBox.Warning,
        ).exec_()


class InputDialogs(QWidget):
    def __init__(self, child: QMainWindow, parent: QMainWindow) -> None:
        """Class constructor."""
        super().__init__(parent)
        self.events = parent.events
        self.main_win = child
        self.title = "Lightning Pass"

    def master_password_dialog(self, parent: str, account_username: str) -> None:
        password, _ = QInputDialog.getText(
            self.main_win,
            parent,
            f"Master password for {account_username}:",
            QLineEdit.Password,
        )

        print(password)


__all__ = [
    "MessageBoxes",
]
