from __future__ import annotations

import contextlib
import functools
import itertools as it
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

import lightning_pass.gui.mouse_randomness as mouse_randomness

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QMainWindow, QMenu, QWidget

    from lightning_pass.gui.mouse_randomness import PasswordOptions, PwdGenerator
    from lightning_pass.users.vaults import Vault


class ClearPreviousWidget:
    """Handle clearing the previous widget by accessing the WIDGET_DATA dict."""

    __slots__ = "parent", "previous_index"

    def __init__(self, parent):
        """Context manager constructor.

        :param parent: The parent where the widget is located

        """
        self.parent = parent
        self.previous_index = parent.events.widget_util.current_index

    def __enter__(self):
        """Do nothing on enter."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clear the previous widget."""
        widget_item: WidgetItem | None

        for item in WIDGET_DATA[self.previous_index]:
            if not item:
                break

            obj = getattr(self.parent.ui, item.name)
            method = getattr(obj, item.clear_method)

            try:
                method(item.clear_args)
            except TypeError:
                method()


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

    @functools.lru_cache(maxsize=None)
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
    def current_widget(self) -> str:
        """Return the current widget of the main stacked widget."""
        return self.parent.ui.stacked_widget.currentWidget().objectName()

    @property
    def current_index(self) -> int:
        """Return the current index of the main stacked widget."""
        return self.parent.ui.stacked_widget.currentIndex()

    def set_current_widget(self, widget: str) -> None:
        """Set a new current widget.

        Clears previous widget with the ClearPreviousWidget ctx manager.

        :param widget: The widget to switch to

        """
        with ClearPreviousWidget(self.parent):
            self.parent.ui.stacked_widget.setCurrentWidget(
                getattr(self.parent.ui, widget),
            )

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

    def input_dialog(self, input_dialog: str, *args: Any, **kwargs: Any) -> None:
        """Show a chosen message box with the given positional and keyword arguments.

        :param input_dialog: The input_dialog type to show
        :param args: Optional positional arguments
        :param kwargs: Optional keyword arguments

        """
        getattr(self.parent.ui.input_dialogs, input_dialog)(*args, **kwargs)

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

        Add 1 to it because it starts at 0 -> widget start at 1 so they're human-readable.

        """
        return self.parent.ui.vault_stacked_widget.currentIndex() + 1

    @vault_stacked_widget_index.setter
    def vault_stacked_widget_index(self, i) -> None:
        """Set a new index on the current vault_stacked_widget if new index is withing legal range."""
        if 1 <= i <= (self.number_of_real_vault_pages + 1):
            self.parent.ui.vault_stacked_widget.setCurrentIndex(
                # index starts at 0
                i
                - 1,
            )

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
            event=lambda: self.parent.events.change_vault_page_event(page.vault_index),
            menu=self.parent.ui.menu_platforms,
        )

    def current_vault_widget_children(self) -> Sequence[QWidget]:
        """Return the current QWidget on the vault_stacked_widget."""
        return self.parent.ui.vault_stacked_widget.currentWidget().children()

    @property
    def vault_widget_vault(self) -> Vault:
        """Return ``Vault`` instantiated with the current vault widget values.

        Finds the new values by accessing the children objects of the current widget.
        Genexpr is used to filter the correct widget types and extract the text.

        """
        children_objects = it.chain(self.current_vault_widget_children())
        return self.parent.events.current_user.vaults.Vault(
            *(
                self.parent.events.current_user.user_id,
                *(
                    widget.text()
                    for widget in children_objects
                    if isinstance(widget, QtWidgets.QLineEdit)
                ),
                self.vault_stacked_widget_index,
            ),
        )

    def clear_current_vault_page(self) -> None:
        """Clear all QLineEdit widgets on the current page."""
        for widget in self.current_vault_widget_children():
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.clear()

    def clear_vault_stacked_widget(self) -> None:
        """Clear QWidgets in the vault_stacked_widget."""
        for widget in self.parent.ui.vault_stacked_widget.children():
            if isinstance(widget, QtWidgets.QWidget):
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
        with db.EnableDBSafeMode(), db.database_manager() as db:
            sql = """UPDATE lightning_pass.vaults
                        SET password = {}
                      WHERE user_id = {}
                        AND vault_index = {}""".format(
                "%s",
                "%s",
                "%s",
            )
            db.execute(sql, (enc, vault.user_id, vault.vault_index))


WIDGET_DATA = (
    # index: 0
    {None},
    # index: 1
    {None},
    # index: 2
    {
        WidgetItem("log_username_line_edit"),
        WidgetItem("log_password_line_edit"),
    },
    # index: 3
    {
        WidgetItem("reg_username_line"),
        WidgetItem("reg_password_line"),
        WidgetItem("reg_conf_pass_line"),
        WidgetItem("reg_email_line"),
    },
    # index: 4
    {WidgetItem("forgot_pass_email_line")},
    # index: 5
    {WidgetItem("reset_token_token_line")},
    # index: 6
    {
        WidgetItem("reset_password_new_pass_line"),
        WidgetItem("reset_password_conf_new_pass_line"),
    },
    # index: 7
    {
        WidgetItem("change_password_current_pass_line"),
        WidgetItem("change_password_new_pass_line"),
        WidgetItem("change_password_conf_new_line"),
    },
    # index: 8
    {
        WidgetItem("generate_pass_spin_box", clear_method="setValue", clear_args=16),
        WidgetItem(
            "generate_pass_numbers_check",
            clear_method="setChecked",
            clear_args=True,
        ),
        WidgetItem(
            "generate_pass_symbols_check",
            clear_method="setChecked",
            clear_args=True,
        ),
        WidgetItem(
            "generate_pass_lower_check",
            clear_method="setChecked",
            clear_args=True,
        ),
        WidgetItem(
            "generate_pass_upper_check",
            clear_method="setChecked",
            clear_args=True,
        ),
    },
    # index: 9
    {WidgetItem("generate_pass_p2_final_pass_line")},
    # index: 10
    {
        WidgetItem("account_username_line"),
        WidgetItem("account_email_line"),
        WidgetItem("account_last_log_date"),
        WidgetItem("account_pfp_pixmap_lbl"),
    },
    # index: 11
    {None},
    # index: 12
    {
        WidgetItem("master_pass_current_pass_line"),
        WidgetItem("master_pass_master_pass_line"),
        WidgetItem("master_pass_conf_master_pass_line"),
    },
)


__all__ = [
    "ClearPreviousWidget",
    "WIDGET_DATA",
    "WidgetItem",
    "WidgetUtil",
]
