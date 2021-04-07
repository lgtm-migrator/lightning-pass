from typing import NamedTuple, Optional


class WidgetItem(NamedTuple):
    name: str
    method: Optional[str] = "clear"
    args: Optional[any] = None


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
        WidgetItem("generate_pass_spin_box", "setValue", 16),
        WidgetItem("generate_pass_numbers_check", "setChecked", True),
        WidgetItem("generate_pass_symbols_check", "setChecked", True),
        WidgetItem("generate_pass_lower_check", "setChecked", True),
        WidgetItem("generate_pass_upper_check", "setChecked", True),
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

VAULT_WIDGET_DATA: set[WidgetItem] = {
    WidgetItem("vault_platform_line", "setText", "platform_name"),
    WidgetItem("vault_web_line", "setText", "website"),
    WidgetItem("vault_username_line", "setText", "username"),
    WidgetItem("vault_email_line", "setText", "email"),
    WidgetItem("vault_password_line"),
    WidgetItem("vault_page_lbl", "setText", "vault_index"),
}


class ClearPreviousWidget:
    """Handle clearing the previous widget by accessing the WIDGET_DATA dict."""

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
        widget_item: Optional[WidgetItem]

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
