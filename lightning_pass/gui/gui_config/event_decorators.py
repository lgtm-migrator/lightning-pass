"""Module with decorators to decorate events with extra functionality."""
from __future__ import annotations

import functools
from typing import Callable, Optional


def _base_decorator(
    __function: Optional[Callable] = None,
    /,
    *,
    __base_obj: Optional[str] = None,
    __condition_object: Optional[Callable] = None,
    __message_box: Optional[str] = None,
    __box_parent_lbl: Optional[str] = None,
    page_to_access: Optional[str] = None,
) -> Callable:
    """Create a custom decorator which can be altered at runtime.

    Decorate to ensure that a specific condition is true in order access a specific event.
    All additional params passed into the deco factory must be used as keyword arguments.
        If they were passed in as positional, they would override the _function param.

    :param __function: Will become the actual function if decorator is used without parenthesis
        Not supposed to be used manually, defaults to Non
    :param __base_obj: The parent object of the item to check
    :param __condition_object: The object to be called to check whether decorator should advance
        or show the previously defined message box
    :param __message_box: The message box to be shown if the condition check fails
    :param __box_parent_lbl: The label to be shown on the message box
    :param page_to_access: The page user tried to access, used to modify the message box.
        As of right now, the only kwarg to be used with the actual decorator, defaults to None

    :return: the decorated function decorated with the specified decorator

    """

    def decorator(func: Callable) -> Callable:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Callable | None:
            """Wrap the original function.

            :param args: Positional arguments, first one should be the class attribute which contains
                the information about the data we're trying to check
            :param kwargs: Optional keyword arguments

            :return: executed function or None and show a message box indicating need log in

            """
            self = args[0]
            if __condition_object(
                obj=getattr(self, __base_obj) if __base_obj else self
            ):
                return _func_executor(func, *args, **kwargs)
            else:
                getattr(self.parent.ui.message_boxes, __message_box)(
                    __box_parent_lbl,
                    page=page_to_access,
                )

        return wrapper

    if __function:
        # decorator was used without parenthesis
        return decorator(__function)
    return decorator


def _attr_checker(*, obj: any, attr: str) -> bool:
    """Check class attributes.

    All params must be passed in as keyword arguments.
    This function is supposed to be used as a partial function.
    Partial functions with positional arguments do not work very well.

    :param obj: The object which should contain the given attribute
    :param attr: The attribute

    """
    try:
        return bool(getattr(obj, attr))
    except AttributeError:
        return False


def _func_executor(func: Callable, *args, **kwargs) -> None:
    """Simple function execution wrapper.

    :param func: The function to execute
    :param args: Optional positional arguments
    :param kwargs: Optional keyword arguments

    """
    try:
        return func(*args, **kwargs)
    except TypeError:
        return func(args[0])


login_required = functools.partial(
    _base_decorator,
    __condition_object=functools.partial(_attr_checker, attr="current_user"),
    __message_box="login_required_box",
    __box_parent_lbl="Account",
)
master_password_required = functools.partial(
    _base_decorator,
    __base_obj="current_user",
    __condition_object=functools.partial(_attr_checker, attr="master_password"),
    __message_box="master_password_required_box",
)
vault_unlock_required = functools.partial(
    _base_decorator,
    __base_obj="current_user",
    __condition_object=functools.partial(_attr_checker, attr="vault_unlocked"),
    __message_box="vault_unlock_required_box",
)


__all__ = ["login_required", "master_password_required", "vault_unlock_required"]
