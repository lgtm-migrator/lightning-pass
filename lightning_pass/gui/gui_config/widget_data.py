from typing import Any, NamedTuple, Optional, Union

_c = ("clear", None)
_s_ch = ("setChecked", True)


class WidgetItem(NamedTuple):
    name: str
    method: Optional[str]
    args: Optional[Any]


WIDGET_DATA: dict[int : set[Optional[WidgetItem]]] = {
    1: {None},
    2: {
        WidgetItem("log_username_line_edit", *_c),
        WidgetItem("log_password_line_edit", *_c),
    },
    3: {
        WidgetItem("reg_username_line", *_c),
        WidgetItem("reg_password_line", *_c),
        WidgetItem("reg_conf_pass_line", *_c),
        WidgetItem("reg_email_line", *_c),
    },
    4: {WidgetItem("forgot_pass_email_line", *_c)},
    5: {WidgetItem("reset_token_token_line", *_c)},
    6: {
        WidgetItem("reset_pass_new_pass_line", *_c),
        WidgetItem("reset_pass_conf_new_line", *_c),
    },
    7: {
        WidgetItem("generate_pass_spin_box", "setValue", 16),
        WidgetItem("generate_pass_numbers_check", *_s_ch),
        WidgetItem("generate_pass_symbols_check", *_s_ch),
        WidgetItem("generate_pass_lower_check", *_s_ch),
        WidgetItem("generate_pass_upper_check", *_s_ch),
    },
    8: {WidgetItem("generate_pass_p2_final_pass_line", *_c)},
}


class ClearPreviousWidget:
    def __init__(self, parent):
        """Context manager constructor.

        :param parent: The parent where the widget is located

        """
        self.ui = parent.ui
        self.previous_index = parent.ui.stacked_widget.currentIndex()

    def __enter__(self):
        """Do nothing on enter."""

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Clear the previous widget."""
        for widget_item in WIDGET_DATA[self.previous_index]:
            if not widget_item:
                break

            obj = getattr(self.ui, widget_item.name)
            method = getattr(obj, widget_item.method)

            if not widget_item.args:
                method()
            else:
                method(widget_item.args)
