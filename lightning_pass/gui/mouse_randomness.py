"""Module containing classes used for operations with mouse randomness generation."""
import random
import string
from typing import Generator, NamedTuple, Optional

from PyQt5 import QtCore, QtWidgets


class MouseTracker(QtCore.QObject):
    """This class contains functionality for setting up a mouse tracker over a chosen label.

    :param QLabel widget: QLabel widget which will be used for tracking

    """

    position_changed = QtCore.pyqtSignal(QtCore.QPoint)

    __slots__ = "widget"

    def __init__(self, widget: QtWidgets.QLabel) -> None:
        """Class constructor."""
        super().__init__(widget)
        self.widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    def eventFilter(
        self,
        label: QtWidgets.QLabel,
        event: QtCore.QEvent.MouseMove,
    ) -> object:
        """Event filter.

        :param QLabel label: Label object
        :param MouseMove event: Mouse move event

        :returns: eventFilter of super class

        """
        if label is self.widget and event.type() == QtCore.QEvent.MouseMove:
            self.position_changed.emit(event.pos())
        return super().eventFilter(label, event)

    @staticmethod
    def setup_tracker(
        label: QtWidgets.QLabel,
        on_change: QtCore.pyqtBoundSignal,
    ) -> None:
        """Set up a mouse tracker over a specified label."""
        tracker = MouseTracker(label)
        tracker.position_changed.connect(on_change)


class PasswordOptions(NamedTuple):
    length: int
    numbers: bool
    symbols: bool
    lowercase: bool
    uppercase: bool


class Chars(NamedTuple):
    chars: str
    length: int


def printable_options(options: PasswordOptions) -> Chars:
    """Return all of the printable chars to be used.

    :param options: The given options

    """
    final = "".join(
        (
            chars
            for option, chars in zip(
                # not using first integer value
                options[1:],
                (
                    string.digits,
                    string.punctuation,
                    string.ascii_lowercase,
                    string.ascii_uppercase,
                ),
            )
            if option
        ),
    )

    return Chars(final, len(final))


class PwdGenerator:
    """Holds user's chosen parameters for password generation and contains the password generation functionality.

    :param options: The ``NamedTuple`` containing the password options chosen by the user

    """

    __slots__ = "options", "chars", "password", "div", "coro"

    def __init__(self, options: PasswordOptions) -> None:
        """Construct the class."""
        self.options = options
        self.chars = printable_options(self.options)
        self.password = ""

        self.div = int(1_000 // self.options.length)
        self.coro = self.coro_div_check()
        # advance the generator to the first yield
        next(self.coro)

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"""{self.__class__.__qualname__}({self.options})"""

    def coro_div_check(self) -> Generator[bool, int, bool]:
        """Coroutine used to check whether a character should be collected."""
        # stops yielding if length has been reached
        while len(self.password) <= self.options.length:
            try:
                # waits for sent value
                yield True if (yield) % self.div == 0 else False
            except (ZeroDivisionError, TypeError):
                yield False
        return False

    def get_character(self, x: int, y: int) -> Optional[str]:
        """Get a eligible password character by generating a random seed from the mouse position axis.

        Chooses an item from the ``chars`` attribute based on the calculated index.

        :param x: The x axis mouse position
        :param y: The y axis mouse position

        """
        if len(self.password) > self.options.length:
            return

        random.seed(x + 1j * y)
        flt = random.random()
        div = 1 / self.chars.length

        index = int(flt // div)

        self.password += self.chars.chars[index]


__all__ = [
    "MouseTracker",
    "PwdGenerator",
]
