from __future__ import annotations

import contextlib
import itertools
from typing import TYPE_CHECKING, Any, NamedTuple, Optional, Sequence, Iterator

from PyQt5 import QtWidgets

import lightning_pass.gui.mouse_randomness as mouse_randomness

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QMainWindow, QWidget

    from lightning_pass.users.vaults import Vault
    from lightning_pass.gui.mouse_randomness import PasswordOptions, PwdGenerator


class WidgetItem(NamedTuple):
    name: str
    fill_method: str | None = None
    fill_args: str | None = None
    clear_method: str | None = "clear"
    clear_args: Any | None = None


VAULT_WIDGET_DATA: set[WidgetItem] = {
    WidgetItem("vault_platform_line", fill_method="setText", fill_args="platform_name"),
    WidgetItem("vault_web_line", fill_method="setText", fill_args="website"),
    WidgetItem("vault_username_line", fill_method="setText", fill_args="username"),
    WidgetItem("vault_email_line", fill_method="setText", fill_args="email"),
    WidgetItem("vault_password_line"),
    WidgetItem("vault_page_lcd_number", fill_method="display", fill_args="vault_index"),
}


class WidgetUtil:

    mouse_randomness = mouse_randomness

    def __init__(self, parent: QMainWindow):
        """Construct the class."""
        self.parent = parent

    def __repr__(self) -> str:
        """Provide information about this class."""
        return f"{self.__class__.__name__}({self.parent})"

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

    def rebuild_vault_stacked_widget(self) -> None:
        """Rebuild ``vault_stacked_widget``."""
        self.parent.ui.vault_stacked_widget = QtWidgets.QStackedWidget(
            self.parent.ui.vault,
        )
        self.parent.ui.vault_stacked_widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.parent.ui.vault_stacked_widget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.parent.ui.vault_stacked_widget.setObjectName("vault_stacked_widget")
        self.parent.ui.vault_dummy_page1 = QtWidgets.QWidget()
        self.parent.ui.vault_dummy_page1.setEnabled(False)
        self.parent.ui.vault_dummy_page1.setObjectName("vault_dummy_page1")
        self.parent.ui.vault_stacked_widget.addWidget(self.parent.ui.vault_dummy_page1)
        self.parent.ui.gridLayout_12.addWidget(
            self.parent.ui.vault_stacked_widget,
            0,
            3,
            6,
            1,
        )

    @property
    def vault_stacked_widget_index(self) -> int:
        """Return the current ``vault_stacked_widget`` index."""
        return self.parent.ui.vault_stacked_widget.currentIndex()

    @vault_stacked_widget_index.setter
    def vault_stacked_widget_index(self, i) -> None:
        """Set a new ``vault_stacked_widget_index``."""
        self.parent.ui.vault_stacked_widget.setCurrentIndex(i)

    def setup_vault_page(self, page: Vault | None = None) -> None:
        """Set up and connect a new vault page

        :param page: Vault object containing the data which should be shown on the current page, defaults to None

        """
        self.parent.ui.vault_widget = self.parent.ui.vault_widget_obj()
        self.parent.ui.vault_stacked_widget.addWidget(
            self.parent.ui.vault_widget.widget,
        )

        if page:
            for data in VAULT_WIDGET_DATA:
                obj = getattr(self.parent.ui.vault_widget.ui, data.name)

                with contextlib.suppress(TypeError):
                    method = getattr(obj, data.fill_method)
                    args = getattr(page, data.fill_args)

                try:
                    method(args)
                except (TypeError, UnboundLocalError):
                    method()

        self.parent.ui.vault_stacked_widget.setCurrentWidget(
            self.parent.ui.vault_widget.widget,
        )
        self.parent.buttons.setup_vault_buttons()

    @property
    def vault_widget_vault(self) -> Vault:
        """Return ``Vault`` instantiated with the current vault widget values.

        Finds the new values by accessing the children objects of the current widget.
        Genexpr is used to filter the correct widget types and extract the text.

        """
        children_objects = itertools.chain(
            (self.parent.ui.vault_stacked_widget.currentWidget().children()),
        )
        return self.parent.events.current_user.vaults.Vault(
            *(
                self.parent.events.current_user.user_id,
                *(
                    widget.text()
                    for widget in children_objects
                    if isinstance(widget, QtWidgets.QLineEdit)
                ),
                self.vault_stacked_widget_index - 1,
            ),
        )


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


class ClearPreviousWidget:
    """Handle clearing the previous widget by accessing the WIDGET_DATA dict."""

    __slots__ = ("parent", "previous_index")

    def __init__(self, parent):
        """Context manager constructor.

        :param parent: The parent where the widget is located

        """
        self.parent = parent
        self.previous_index = parent.current_index

    def __enter__(self):
        """Do nothing on enter."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clear the previous widget."""
        widget_item: WidgetItem | None

        for widget_item in WIDGET_DATA[self.previous_index]:
            if not widget_item:
                break

            obj = getattr(self.parent.ui, widget_item.name)
            method = getattr(obj, widget_item.clear_method)

            try:
                method(widget_item.clear_args)
            except TypeError:
                method()


__all__ = ["WidgetItem", "WIDGET_DATA", "ClearPreviousWidget"]
