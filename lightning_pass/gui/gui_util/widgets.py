"""Utilities for widgets and events."""
from __future__ import annotations

import contextlib
import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterator,
    NamedTuple,
    Optional,
    Sequence,
)

from PyQt5 import QtCore, QtGui, QtWidgets

from lightning_pass.gui import mouse_randomness

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QMainWindow, QMenu, QWidget

    from lightning_pass.gui.mouse_randomness import PasswordOptions, PwdGenerator
    from lightning_pass.users.vaults import Vault


class WidgetItem(NamedTuple):
    """Store data about widget."""

    name: str
    fill_method: Optional[str] = None
    fill_args: Optional[str] = None
    clear_method: Optional[str] = "clear"
    clear_args: Optional[Any] = None


VAULT_WIDGET_DATA: set[WidgetItem] = {
    WidgetItem("vault_platform_line", fill_method="setText", fill_args="platform_name"),
    WidgetItem("vault_web_line", fill_method="setText", fill_args="website"),
    WidgetItem("vault_username_line", fill_method="setText", fill_args="username"),
    WidgetItem("vault_email_line", fill_method="setText", fill_args="email"),
    WidgetItem("vault_password_line", fill_method="setText", fill_args="password"),
    WidgetItem("vault_page_lcd_number", fill_method="display", fill_args="vault_index"),
}


class WidgetUtil:
    """Various utilities to be used with event handling or account management."""

    __slots__ = "parent"

    mouse_randomness = mouse_randomness

    def __init__(self, parent: QMainWindow):
        """Construct the class."""
        self.parent = parent

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__qualname__}({self.parent!r})"

    @functools.cache
    def font(self, family: str, size: int):
        """Return the specified font and memoize it.

        :param family: The font family
        :param size: The font size

        """
        font = QtGui.QFont()
        font.setFamily(family)
        font.setPointSize(size)
        return font

    @property
    def current_widget(self) -> QWidget:
        """Return the current widget of the main stacked widget."""
        return self.parent.ui.stacked_widget.currentWidget()

    @current_widget.setter
    def current_widget(self, widget: str) -> None:
        """Set a new current widget.

        :param widget: The new widget to switch to

        """
        if (name := (w := self.current_widget).objectName()) == "generate_pass":
            self.reset_generator_page()
        elif name not in {"account", "vault"}:
            for line in w.findChildren(QtWidgets.QLineEdit):
                line.clear()

        self.parent.ui.stacked_widget.setCurrentWidget(getattr(self.parent.ui, widget))

    @contextlib.contextmanager
    def disable_widget(*widgets: Sequence[QWidget]) -> Iterator[None]:
        """Simple context manager to momentarily disable given widgets.

        :param widgets: Positional arguments containing the widgets which should be disabled

        """
        for widget in widgets:
            widget.setEnabled(False)
        try:
            yield
        finally:
            for widget in widgets:
                widget.setEnabled(True)

    @staticmethod
    def waiting_loop(seconds: int) -> None:
        """Stop the application for the given amount of seconds.

        :param seconds: The length of the event loop

        """
        loop = QtCore.QEventLoop()
        # turn to milliseconds
        QtCore.QTimer.singleShot(seconds * 1_000, loop.quit)
        loop.exec()

    def message_box(self, message_box: str, *args: Any, **kwargs: Any) -> None:
        """Show a chosen message box with the given positional and keyword arguments.

        :param message_box: The message box type to show
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        """
        getattr(self.parent.ui.message_boxes, message_box)(*args, **kwargs)

    def input_dialog(self, input_dialog: str, *args: tuple, **kwargs: dict) -> None:
        """Show a chosen message box with the given positional and keyword arguments.

        :param input_dialog: The input_dialog type to show
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        """
        getattr(self.parent.ui.input_dialogs, input_dialog)(*args, **kwargs)

    def clear_account_page(self) -> None:
        """Clear the account page."""
        for widget in self.parent.ui.account.findChildren(QtWidgets.QLineEdit):
            widget.clear()

    @property
    def password_options(self) -> PasswordOptions:
        """Return current password generation values in the ``PasswordOptions``."""
        return self.mouse_randomness.PasswordOptions(
            self.parent.ui.generate_pass_spin_box.value(),
            self.parent.ui.generate_pass_numbers_check.isChecked(),
            self.parent.ui.generate_pass_symbols_check.isChecked(),
            self.parent.ui.generate_pass_lower_check.isChecked(),
            self.parent.ui.generate_pass_upper_check.isChecked(),
        )

    def get_generator(self) -> PwdGenerator:
        """Get Generator from current password params.

        :returns: the ``PwdGenerator`` with current values

        """
        return self.mouse_randomness.PwdGenerator(self.password_options)

    def reset_generator_page(self) -> None:
        """Change the password generator value back to the defaults."""
        ui = self.parent.ui
        for check_box in (page := getattr(ui, "generate_pass")).findChildren(
            QtWidgets.QCheckBox,
        ):
            check_box.setChecked(True)
        page.findChild(QtWidgets.QSpinBox).setValue(16)

    def setup_menu(self, obj_name: str, title: str) -> QMenu:
        """Setup a new ``QMenu`` tied to the root ``QMenuBar``.

        :param obj_name: Reference to the new object
        :param title: Text on the actual widget

        :returns: The new ``QMenu`` object

        """
        if not hasattr(self.parent.ui, obj_name):
            setattr(
                self.parent.ui,
                obj_name,
                QtWidgets.QMenu(self.parent.ui.menu_bar),
            )
            (menu := getattr(self.parent.ui, obj_name)).setTitle(title)
            menu.setFont(self.font("Segoe UI Light", 10))
        return getattr(self.parent.ui, obj_name)

    def setup_action(
        self,
        obj_name: str,
        text: str,
        event: Callable[[], None],
        menu: QMenu,
    ) -> None:
        """Setup a new ``QAction``.

        :param obj_name: Reference to the new object
        :param text: Text on the actual widget
        :param event: What will happen when the action is triggered
        :param menu: The root ``QMenu`` for the new action

        :returns: The newly instantiated ``QAction``

        """
        obj_name = f"action_{obj_name}"
        try:
            action = getattr(self.parent.ui, obj_name)
        except AttributeError:
            setattr(self.parent.ui, obj_name, QtWidgets.QAction(self.parent.main_win))
            (action := getattr(self.parent.ui, obj_name)).setText(text)
            action.setFont(self.font("Segoe UI", 9))
        finally:
            action.triggered.connect(event)

        if obj_name not in menu.actions():
            menu.addAction(action)

    @property
    def vault_stacked_widget_index(self) -> int:
        """Return the current ``vault_stacked_widget`` index.

        Add 1 to it because it starts at 0 -> widgets start at 1 so they're in human-readable form.

        """
        return self.parent.ui.vault_stacked_widget.currentIndex() + 1

    @vault_stacked_widget_index.setter
    def vault_stacked_widget_index(self, i) -> None:
        """Set a new index on the current vault_stacked_widget if new index is withing legal range."""
        if 1 <= i <= (self.number_of_real_vault_pages + 1):
            self.parent.ui.vault_stacked_widget.setCurrentIndex(i - 1)

    @property
    def number_of_real_vault_pages(self) -> int:
        """Return the amount of vault pages a user has registered."""
        return len(self.parent.ui.menu_platforms.actions())

    def setup_vault_widget(self, page: Vault | None = None) -> None:
        """Set up and connect a new vault page.

        :param page: Vault object containing the data which should be shown on the current page, defaults to None

        """
        self.parent.ui.vault_widget_instance = self.parent.ui.vault_widget_obj()
        self.parent.ui.vault_stacked_widget.addWidget(
            self.parent.ui.vault_widget_instance.widget,
        )

        if page:
            self.setup_vault_page(page)

        self.parent.ui.vault_stacked_widget.setCurrentWidget(
            self.parent.ui.vault_widget_instance.widget,
        )
        self.parent.buttons.setup_vault_buttons()

    def setup_vault_page(self, page):
        """Setup a single page.

        Connect buttons to their corresponding events.
        Set text on universal labels.

        :param page: The data which will be used during the setup

        """
        for data in VAULT_WIDGET_DATA:
            obj = getattr(self.parent.ui.vault_widget_instance.ui, data.name)
            method = getattr(obj, data.fill_method)
            args = getattr(page, data.fill_args)

            method(args)

        self.setup_action(
            obj_name=page.platform_name,
            text=page.platform_name,
            event=lambda: self.parent.events.vault.change_vault_page(page.vault_index),
            menu=self.parent.ui.menu_platforms,
        )

    @property
    def vault_widget_vault(self) -> Vault:
        """Return ``Vault`` instantiated with the current vault widget values.

        Finds the new values by accessing the children objects of the current widget.
        Genexpr is used to filter the correct widget types and extract the text.

        """
        return self.parent.events.current_user.vaults.Vault._make(
            (
                self.parent.events.current_user.user_id,
                *(
                    widget.text()
                    for widget in self.parent.ui.vault_stacked_widget.currentWidget().findChildren(
                        QtWidgets.QLineEdit,
                    )
                ),
                self.vault_stacked_widget_index,
            ),
        )

    def clear_current_vault_page(self) -> None:
        """Clear all ``QLineEdit`` widgets on the current vault page."""
        for widget in self.parent.ui.vault_stacked_widget.currentWidget().findChildren(
            QtWidgets.QLineEdit,
        ):
            widget.clear()

    def clear_vault_stacked_widget(self) -> None:
        """Clear QWidgets in the vault_stacked_widget."""
        for widget in self.parent.ui.vault_stacked_widget.findChildren(
            QtWidgets.QWidget,
        ):
            self.parent.ui.vault_stacked_widget.removeWidget(widget)

    def clear_platform_actions(self) -> None:
        """Clear the current ``QActions`` connected to the current platforms ``QMenu``."""
        (m := self.parent.ui.menu_platforms).clear()
        m.setEnabled(False)

    def rehash_vault_password(self, vault: Vault):
        """Replace password in the given vault by a new one hashed with current master key.

        :param vault: The data container with the information about the vault

        """
        user = self.parent.events.current_user

        enc = user.encrypt_vault_password(vault.password)

        db = user.database
        with db.enable_db_safe_mode(), db.database_manager() as db:
            sql = """UPDATE lightning_pass.vaults
                        SET password = {}
                      WHERE user_id = {}
                        AND vault_index = {}""".format(
                "%s",
                "%s",
                "%s",
            )
            db.execute(sql, (enc, vault.user_id, vault.vault_index))


__all__ = [
    "WidgetItem",
    "WidgetUtil",
]
