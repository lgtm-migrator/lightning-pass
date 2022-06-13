"""Module with decorators to decorate events with extra functionality."""
from __future__ import annotations

import functools
from typing import Any, Callable, NewType, TypeVar, overload

_F = TypeVar("_F", bound=Callable[..., Any])
_Condition = NewType("_Condition", Callable[[str], bool])
_EventArgs = NewType("_Event_args", tuple["Events", ...])


@overload
def _base_decorator(__func: _F, _condition_object: _Condition, message_box: str) -> _F:
    """Bare decorator usage."""
    ...


@overload
def _base_decorator(
    __func: _F,
    *,
    _condition_object: _Condition,
    message_box: str,
    page_to_access: str | None = None,
) -> Callable[[_F], _F]:
    """Decorator with arguments."""
    ...


def _base_decorator(
    __func: _F = None,
    /,
    *,
    _condition_object: _Condition,
    _message_box: str,
    _base_obj: str | None = None,
    _box_parent_lbl: str | None = None,
    page_to_access: str | None = None,
) -> Callable:
    """Create a custom decorator factory.

    Decorate to ensure that a specific condition is true in order access a specific event.
    All additional params passed into the deco factory (the actual decorator) must be used as keyword arguments.
    If they were passed in as positional, they would override the __func param.

    :param __func: Will become the actual function if decorator is used without parenthesis
        Not supposed to be used manually, defaults to None
    :param _condition_object: The object to be called to check whether decorator should advance
        or show the previously defined message box
    :param _message_box: The message box to be shown if the condition check fails
    :param _base_obj: The parent object of the item to check, must have the specified Callable signature
    :param _box_parent_lbl: The label to be shown on the message box
    :param page_to_access: The page user tried to access, used to modify the message box.
        As of right now, the only kwarg to be used with the actual decorator, defaults to None

    :return: the decorated function decorated with the specified decorator

    """

    def decorator(func: _F) -> _F:
        """Decorate the original function.

        :param func: Function to decorate

        :return: the decorated function

        """

        @functools.wraps(func)
        def wrapper(*args: _EventArgs, **kwargs: dict) -> _F | None:
            """Wrap the original function.

            :param args: Positional arguments, first one should be the class attribute which contains
                the information about the data we're trying to check
            :param kwargs: Optional keyword arguments

            :return: executed function or None and show the specified message box

            """
            self = args[0]
            events = self.parent.events
            if _condition_object(
                obj=getattr(events, _base_obj) if _base_obj else events,
            ):
                return _func_executor(func, *args, **kwargs)

            getattr(self.parent.ui.message_boxes, _message_box)(
                _box_parent_lbl,
                page=page_to_access,
            )

        return wrapper

    if __func:
        # decorator was used without parenthesis
        return decorator(__func)
    return decorator


def _func_executor(func: Callable, *args: _EventArgs, **kwargs: dict) -> None:
    """Simple function execution wrapper.

    :param func: The function to execute
    :param args: Optional positional arguments
    :param kwargs: Optional keyword arguments

    """
    try:
        return func(*args, **kwargs)
    except TypeError:
        return func(args[0])


def _attr_checker(*, obj: Any, attr: str) -> bool:
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


def widget_changer(func: _F) -> _F:
    """Execute the given function only if the new widget page is not the same as the current one.

    :param func: The function to decorate

    :returns: the decorated function

    """

    @functools.wraps(func)
    def wrapper(*args: _EventArgs, **kwargs: dict) -> _F | None:
        """Wrap the original function.

        :param args: Positional arguments, first one 'should' be the ``Events`` instance
        :param kwargs: Optional keyword arguments

        :returns: The executed function if the condition is passed

        """
        self = args[0]
        if not self.widget_util.current_widget.objectName() == func.__name__:
            try:
                return func(*args, **kwargs)
            except TypeError:
                return func(self)

    return wrapper


login_required = functools.partial(
    _base_decorator,
    _condition_object=functools.partial(_attr_checker, attr="current_user"),
    _message_box="login_required_box",
    _box_parent_lbl="Account",
)
master_password_required = functools.partial(
    _base_decorator,
    _condition_object=functools.partial(_attr_checker, attr="vault_salt"),
    _message_box="master_password_required_box",
    _base_obj="current_user",
    _box_parent_lbl="Master Password",
)
vault_unlock_required = functools.partial(
    _base_decorator,
    _condition_object=functools.partial(_attr_checker, attr="vault_unlocked"),
    _message_box="vault_unlock_required_box",
    _base_obj="current_user",
    _box_parent_lbl="Vault",
)


__all__ = [
    "login_required",
    "master_password_required",
    "vault_unlock_required",
]
