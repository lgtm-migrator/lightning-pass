"""Module containing classes used for operations with mouse randomness generation."""
import contextlib
import functools
import string
import random
from typing import Generator, Optional, Union, NamedTuple

from PyQt5 import QtCore, QtWidgets


class MouseTracker(QtCore.QObject):
    """This class contains functionality for setting up a mouse tracker over a chosen label.

    :param QLabel widget: QLabel widget which will be used for tracking

    """

    position_changed = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, widget: QtWidgets.QLabel) -> None:
        """Class constructor."""
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self) -> QtWidgets.QLabel:
        """Widget property.

        :return: Own widget

        """
        return self._widget

    def eventFilter(
        self, label: QtWidgets.QLabel, event: QtCore.QEvent.MouseMove
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
        label: QtWidgets.QLabel, on_change: QtCore.pyqtBoundSignal
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
    chars: tuple
    length: int


def printable_options(options: PasswordOptions) -> Chars:
    """Return all of the printable chars to be used.

    :param options: The given options

    """
    final = ()

    if options.numbers:
        final += tuple(string.digits)
    if options.lowercase:
        final += tuple(string.ascii_lowercase)
    if options.uppercase:
        final += tuple(string.ascii_uppercase)
    if options.symbols:
        final += tuple(string.punctuation)

    return Chars(final, len(final))


class PwdGenerator:
    """Holds user's chosen parameters for password generation and contains the password generation functionality.

    :param options: The NamedTuple containing the password options chosen by the user

    """

    def __init__(self, options: PasswordOptions) -> None:
        """Construct the class."""
        self.options = options
        self.chars = printable_options(self.options)

        self.div = int(1000 / self.options.length)
        self.div_check = self.div_check()
        # prepare generator for sending values
        next(self.div_check)

        self.password = ""

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"""{self.__class__.__name__}({self.options})"""

    def div_check(self) -> Generator[bool, int, bool]:
        """Generator used to check whether a character should be collected.

        Used to make password generation look smooth since characters are shown on the fly.

        """
        # stops yielding if length has been reached
        while self.options.length <= 1000:
            try:
                # waits for sent value
                yield True if (yield) % self.div == 0 else False
            except (ZeroDivisionError, TypeError):
                yield False
        return False

    def get_character(self, x: int, y: int) -> Optional[str]:
        """Get a eligible password character by generating a random seed from the mouse position tuple.

        Chooses an item from the string.printable property based on the calculated index.

        :returns: Generated password if it reached the wanted length

        """
        if len(self.password) > self.options.length:
            return

        sd = x + 1j * y
        random.seed(sd)
        flt = random.random()
        div = 1 / self.chars.length

        index = flt // div
        char = self.chars.chars[index]

        with contextlib.suppress(ValueError):
            char = int(char)

        self.collect_char(char)

    @functools.singledispatchmethod
    def collect_char(self, char: Union[int, str]) -> None:
        """Collect a password character.

        Password generation is based on the chosen parameters in the GUI.

        :param char: character to evaluate and potentially add to the current password.

        :raises NotImplementedError: if char type is not registered

        """
        raise NotImplementedError("This character type is not supported.")

    @collect_char.register(str)
    def _(self, char: str) -> None:
        """Evaluate string type.

        :param char: Character

        """
        if (
            (char.islower() and self.options.lowercase)
            or (char.isupper() and self.options.uppercase)
            or (self.options.symbols and not char.islower() and not char.isupper())
        ):
            self.password += char

    @collect_char.register(int)
    def _(self, char: int) -> None:
        """Evaluate int type.

        :param char: Character

        """
        if self.options.numbers:
            self.password += str(char)


__all__ = [
    "MouseTracker",
    "PwdGenerator",
]
