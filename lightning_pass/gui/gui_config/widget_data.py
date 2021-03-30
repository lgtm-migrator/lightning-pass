import contextlib
from typing import Any, NamedTuple, Optional


_c = ("clear", None)
_s_ch = ("setChecked", True)


class WidgetItem(NamedTuple):
    name: str
    method: Optional[str] = _c[0]
    args: Optional[Any] = _c[1]


WIDGET_DATA: dict[int : set[Optional[WidgetItem]]] = {
    1: {None},
    2: {
        WidgetItem("log_username_line_edit"),
        WidgetItem("log_password_line_edit"),
    },
    3: {
        WidgetItem("reg_username_line"),
        WidgetItem("reg_password_line"),
        WidgetItem("reg_conf_pass_line"),
        WidgetItem("reg_email_line"),
    },
    4: {WidgetItem("forgot_pass_email_line")},
    5: {WidgetItem("reset_token_token_line")},
    6: {
        WidgetItem("reset_pass_new_pass_line"),
        WidgetItem("reset_pass_conf_new_line"),
    },
    7: {
        WidgetItem("generate_pass_spin_box", "setValue", 16),
        WidgetItem("generate_pass_numbers_check", *_s_ch),
        WidgetItem("generate_pass_symbols_check", *_s_ch),
        WidgetItem("generate_pass_lower_check", *_s_ch),
        WidgetItem("generate_pass_upper_check", *_s_ch),
    },
    8: {WidgetItem("generate_pass_p2_final_pass_line")},
    11: {
        WidgetItem("master_pass_current_pass_line"),
        WidgetItem("master_pass_master_pass_line"),
        WidgetItem("master_pass_conf_master_pass_line"),
    },
}


class ClearPreviousWidget:
    """Handle clearing the previous widget by accessing the WIDGET_DATA dict."""

    def __init__(self, parent):
        """Context manager constructor.

        :param parent: The parent where the widget is located

        """
        self.parent = parent
        self.previous_index = parent.ui.stacked_widget.currentIndex()

    def __enter__(self):
        """Do nothing on enter."""

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clear the previous widget."""
        widget_item: Optional[WidgetItem]

        # TODO: add all indexes into DATA_DICT
        with contextlib.suppress(KeyError):
            for widget_item in WIDGET_DATA[self.previous_index]:
                if not widget_item:
                    break

                obj = getattr(self.parent.ui, widget_item.name)
                method = getattr(obj, widget_item.method)

                try:
                    method(widget_item.args)
                except TypeError:
                    method()


__all__ = ["WidgetItem", "WIDGET_DATA", "ClearPreviousWidget"]