"""Module with decorators to decorate events with extra functionality."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from lightning_pass.gui.events import Events


def login_required(page_to_access: str | None = None) -> Callable:
    """Decorate to ensure that a user has to be logged in to access a specific event.

    :param page_to_access: The page user tried to access, used to modify the message box, defaults to None

    :return: the decorated function

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(self: Events) -> Callable | None:
            """Check the "current_user" attribute.

            :param self: Class instance to give access to its attributes

            :return: executed function or None and show a message box indicating need log in

            """
            if hasattr(self, "current_user"):
                return func(self)
            else:
                self.ui.message_boxes.login_required_box(
                    "Account",
                    page_to_access,
                )

        return wrapper

    return decorator


def master_password_required(page_to_access: str | None = None) -> Callable:
    """Decorate to ensure that a master password is set up to access a specific event.

    :param page_to_access: The page user tried to access, used to modify the message box, defaults to None

    :return: the decorated function

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(self: Events) -> Callable | None:
            """Check if current user has a master password setup.

            :param self: Class instance to give access to its attributes

            :return: executed function or None and show message box indicating need to set up the master password

            """
            if self.current_user.master_password:
                return func(self)
            else:
                self.ui.message_boxes.master_password_required_box(page=page_to_access)

        return wrapper

    return decorator


def vault_unlock_required(page_to_access: str | None = None) -> Callable:
    """Decorate to ensure that a vault is unlocked to access a specific event.

    :param page_to_access: The page user tried to access, used to modify the message box, defaults to None

    :return: the decorated function

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(self: Events) -> Callable | None:
            """Check the vault_unlocked attribute of the current user.

            :param self: Class instance to give access to its attributes

            :return: executed function or None and show a message box indicating unlock vault

            """
            if self.current_user.vault_unlocked:
                return func(self)
            else:
                self.ui.message_boxes.vault_unlock_required_box(page=page_to_access)

        return wrapper

    return decorator


__all__ = ["login_required", "master_password_required", "vault_unlock_required"]
