"""Module with decorators to decorate events with extra functionality."""
import functools
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from lightning_pass.gui.events import Events


def login_required(func: Callable) -> Callable:
    """Decorate to ensure that a user has to be logged in to access a specific event.

    :param func: Function to decorate

    :return: the decorated function

    """

    @functools.wraps(func)
    def wrapper(self: "Events") -> Optional[Callable]:
        """Check the "current_user" attribute.

        :param self: Class instance to give access to its attributes

        :return: executed function or None and show a message box indicating need log in

        """
        if not hasattr(self, "current_user"):
            self.ui.message_boxes.login_required_box("Account")
        else:
            return func(self)

    return wrapper


def master_password_required(func: Callable) -> Callable:
    """Decorate to ensure that a master password is set up to access a specific event.

    :param func: Function to decorate

    :return: the decorated function

    """

    @functools.wraps(func)
    def wrapper(self: "Events") -> Optional[Callable]:
        """Check if current user has a master password setup."""
        if not self.current_user.master_password:
            self.ui.message_boxes.master_password_required_box()
        else:
            return func(self)

    return wrapper


def vault_unlock_required(func: Callable) -> Callable:
    """Decorate to ensure that a vault is unlocked to access a specific event.

    :param func: Function to decorate

    :return: the decorated function

    """

    @functools.wraps(func)
    def wrapper(self: "Events") -> Optional[Callable]:
        """Check the vault_unlocked attribute of the current user.

        If current user does not exist show normal login required box.
        If vault is not unlocked show box indicating need to unlock it.

        :param self: Class instance to give access to its attributes

        :return: executed function or None and show a message box indicating need log in

        """
        if not self.current_user.vault_unlocked:
            self.ui.message_boxes.vault_unlock_required_box()
        else:
            return func(self)

    return wrapper


__all__ = ["login_required", "master_password_required", "vault_unlock_required"]
