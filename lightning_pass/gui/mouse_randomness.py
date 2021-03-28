"""Module containing classes used for operations with mouse randomness generation."""
import contextlib
import functools
import random
import string
from typing import Generator, Optional, Union

from PyQt5 import QtCore, QtWidgets

from lightning_pass.util.exceptions import StopCollectingPositions


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


CollectorSet = tuple[tuple[int, int]]


class Collector:
    """This class contains functionality for recording current mouse position."""

    def __init__(self, data: CollectorSet = None) -> None:
        """Class constructor."""
        self.randomness_set = CollectorSet
        if data:
            self.randomness_set = data

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"Collector({self.randomness_set})"

    def __iter__(self) -> Generator:
        """Yield mouse movement tuples."""
        yield from self.randomness_set

    def collect_position(self, pos: QtCore.QPoint) -> None:
        """Collect mouse position.

        :param QPoint pos: Current cursor position

        :raises StopCollectingPositions: if 1000 mouse positions have been collected

        """
        if len(self.randomness_set) > 1000:
            raise StopCollectingPositions

        self.randomness_set = (*self.randomness_set, (pos.x(), pos.y()))


class PwdGenerator:
    """Holds user's chosen parameters for password generation and contains the password generation functionality.

    :param int length: Password length
    :param bool numbers: Password option
    :param bool symbols: Password option
    :param bool lowercase: Password option
    :param bool uppercase: Password option

    """

    def __init__(
        self,
        length: int,
        numbers: bool,
        symbols: bool,
        lowercase: bool,
        uppercase: bool,
    ) -> None:
        """Construct the class."""
        self.length = length
        self.numbers = numbers
        self.symbols = symbols
        self.lowercase = lowercase
        self.uppercase = uppercase

        self.password = ""

    def get_character(self, position: tuple[int, int]) -> Optional[str]:
        """Get a eligible password character by generating a random seed from the mouse position tuple.

        Chooses an item from the string.printable property based on the calculated index.

        :returns: Generated password if it reached the wanted length

        """
        if len(self.password) > self.length:
            return self.password

        sd = position[0] + 1j * position[1]
        random.seed(sd)
        flt = random.random()
        div = 1 / 94  # 0.010638297872340425 : 94 eligible symbols in string.printable

        indx = flt / div

        char = str(string.printable)[int(indx)]

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
            (char.islower() and self.lowercase)
            or (char.isupper() and self.uppercase)
            or (self.symbols and not char.islower() and not char.isupper())
        ):
            self.password += char

    @collect_char.register(int)
    def _(self, char: int) -> None:
        """Evaluate int type.

        :param char: Character

        """
        if self.numbers:
            self.password += str(char)


__all__ = [
    "Collector",
    "MouseTracker",
    "PwdGenerator",
]
