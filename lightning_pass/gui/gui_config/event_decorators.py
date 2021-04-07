"""Module with decorators to decorate events with extra functionality."""
from __future__ import annotations

import functools
from typing import Callable, Optional


def login_required(
    function: Optional[Callable] = None, page_to_access: str | None = None
) -> Callable:
    """Decorate to ensure that a user has to be logged in to access a specific event.

    :param function: Will become the actual function if decorator is used without parenthesis, defaults to None
    :param page_to_access: The page user tried to access, used to modify the message box, defaults to None

    :return: the decorated function

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Callable | None:
            """Check the "current_user" attribute.

            :param args: Positional arguments, first one should be the class attribute which contains
                the data about the state of currently logged user (or not).
            :param kwargs: Keyword arguments

            :return: executed function or None and show a message box indicating need log in

            """
            self = args[0]
            if hasattr(self, "current_user"):
                return func(*args, **kwargs)
            else:
                self.ui.message_boxes.login_required_box(
                    "Account",
                    page=page_to_access,
                )

        return wrapper

    if function:
        return decorator(function)
    return decorator


def master_password_required(
    function: Optional[Callable] = None, page_to_access: str | None = None
) -> Callable:
    """Decorate to ensure that a master password is set up to access a specific event.

    :param function: Will become the actual function if decorator is used without parenthesis, defaults to None
    :param page_to_access: The page user tried to access, used to modify the message box, defaults to None

    :return: the decorated function

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Callable | None:
            """Check if current user has a master password setup.

            :param args: Positional arguments, first one should be the class attribute which contains
                the data about the master password state (or not).
            :param kwargs: Keyword arguments

            :return: executed function or None and show message box indicating need to set up the master password

            """
            self = args[0]
            if self.current_user.master_password:
                return func(*args, **kwargs)
            else:
                self.ui.message_boxes.master_password_required_box(page=page_to_access)

        return wrapper

    if function:
        return decorator(function)
    return decorator


def vault_unlock_required(
    function: Optional[Callable] = None, page_to_access: str | None = None
) -> Callable:
    """Decorate to ensure that a vault is unlocked to access a specific event.

    :param function: Will become the actual function if decorator is used without parenthesis, defaults to None
    :param page_to_access: The page user tried to access, used to modify the message box, defaults to None

    :return: the decorated function

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Callable | None:
            """Check the vault_unlocked attribute of the current user.

            :param args: Positional arguments, first one should be the class attribute which contains
                the data about vault state (or not).
            :param kwargs: Keyword arguments

            :return: executed function or None and show a message box indicating unlock vault

            """
            self = args[0]
            if self.current_user.vault_unlocked:
                return func(*args, **kwargs)
            else:
                self.ui.message_boxes.vault_unlock_required_box(page=page_to_access)

        return wrapper

    if function:
        return decorator(function)
    return decorator


__all__ = ["login_required", "master_password_required", "vault_unlock_required"]
