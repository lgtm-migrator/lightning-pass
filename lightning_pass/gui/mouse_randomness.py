"""Module containing classes used for operations with mouse randomness generation."""
import random
import string
from typing import Generator

from PyQt5 import QtCore, QtWidgets

from lightning_pass.util.exceptions import StopCollectingPositions


class MouseTracker(QtCore.QObject):
    """This class contains functionality for setting up a mouse tracker over a chosen label.

    :param QLabel widget: QLabel widget which will be used for tracking

    """

    position_changed = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, widget: QtWidgets.QLabel) -> None:
        """Class contructor."""
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


class Collector:
    """This class contains functionality for recording current mouse position."""

    def __init__(self) -> None:
        """Class contructor."""
        self.randomness_lst: list[tuple[int, int]] = []

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"Collector({self.randomness_lst})"

    def collect_position(self, pos: QtCore.QPoint) -> None:
        """Collect mouse position.

        :param QPoint pos: Current cursor position

        :raises StopCollectingPositions: if 1000 mouse positions have been collected

        """
        if len(self.randomness_lst) > 999:
            raise StopCollectingPositions
        self.randomness_lst.append((pos.x(), pos.y()))

    def generator(self) -> Generator:
        """Yield mouse movement tuples."""
        yield from self.randomness_lst


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
        """Class constructor."""
        self.length = length
        self.numbers = numbers
        self.symbols = symbols
        self.lowercase = lowercase
        self.uppercase = uppercase

        self.password = ""

    def get_character(self, position: tuple[int, int]) -> None:
        """Get a eligible password character by generating a random seed from the mouse position tuple.

        :raises StopIteration: if password length matches the given length

        """
        sd = position[0] + 1j * position[1]
        random.seed(sd)
        flt = random.random()

        indx = flt / (1 / 94)  # 0.010638297872340425  # 94 symbols...
        self._collect_char(str(string.printable)[int(indx)])

    def _collect_char(self, char: str) -> None:
        """Collect a password character.

        Password generation is based on the chosen parameters in the GUI.

        :param str char: character to evaluate and potentially add to the current password.

        :returns: False if password is already long enough

        :raises StopIteration: if password length matches the given length

        """
        if len(self.password) > self.length:
            raise StopIteration
        if (
            (char.isdigit() and self.numbers)
            or (char.islower() and self.lowercase)
            or (char.isupper() and self.uppercase)
            or (
                not char.isdigit()
                and not char.islower()
                and not char.isupper()
                and self.symbols
            )
        ):
            self.password += char

    def get_password(self) -> str:
        """Return generated password.

        :returns: generated password

        """
        return self.password


__all__ = [
    "Collector",
    "MouseTracker",
    "PwdGenerator",
]
