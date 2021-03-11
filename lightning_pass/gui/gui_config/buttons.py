"""Module containing the Buttons class.

Used for connecting each button on the GUI to various events or lambdas.

"""
from __future__ import annotations

from pathlib import Path

from lightning_pass.gui.gui import LightningPassWindow


class Buttons:
    """Used to setup buttons on the LightningPassWindow."""

    def __init__(
        self,
        parent: LightningPassWindow,
        *args: object,
        **kwargs: object,
    ) -> None:
        """Buttons constructor.

        :param LightningPassWindow parent: Main GUI window

        """
        super().__init__(*args, **kwargs)
        self.main_win = parent
        self.ui = parent.ui

    def setup_buttons(self) -> None:
        """Connect all buttons."""
        self.ui.home_login_btn.clicked.connect(self.main_win.events.login_event)
        self.ui.home_register_btn.clicked.connect(self.main_win.events.register_event)
        self.ui.home_generate_password_btn.clicked.connect(
            self.main_win.events.generate_pass_event,
        )

        self.ui.log_main_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.log_forgot_pass_btn.clicked.connect(
            self.main_win.events.forgot_password_event,
        )
        self.ui.log_login_btn_2.clicked.connect(self.main_win.events.login_user_event)

        self.ui.reg_main_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.reg_register_btn.clicked.connect(
            self.main_win.events.register_user_event,
        )

        self.ui.forgot_pass_main_menu_btn.clicked.connect(
            self.main_win.events.home_event,
        )

        self.ui.generate_pass_generate_btn.clicked.connect(
            self.main_win.events.generate_pass_phase2_event,
        )
        self.ui.generate_pass_main_menu_btn.clicked.connect(
            self.main_win.events.home_event,
        )
        self.ui.generate_pass_p2_main_btn.clicked.connect(
            self.main_win.events.home_event,
        )
        self.ui.generate_pass_p2_copy_btn.clicked.connect(
            self.main_win.events.copy_password_event,
        )

        self.ui.account_main_menu_btn.clicked.connect(self.main_win.events.home_event)
        self.ui.account_change_pfp_btn.clicked.connect(
            self.main_win.events.change_pfp_event,
        )
        self.ui.account_logout_btn.clicked.connect(self.main_win.events.logout_event)
        self.ui.account_change_pass_btn.clicked.connect(
            self.main_win.events.change_pass_event,
        )
        self.ui.account_edit_details_btn.clicked.connect(
            self.main_win.events.edit_details_event,
        )

    def setup_menu_bar(self) -> None:
        """Connect all menu bar actions."""
        self.ui.action_main_menu.triggered.connect(self.main_win.events.home_event)
        self.ui.action_light.triggered.connect(
            lambda: self.main_win.events.toggle_stylesheet_light(
                f"{Path(__file__).parent}/static/light.qss",
            ),
        )
        self.ui.action_dark.triggered.connect(
            lambda: self.main_win.events.toggle_stylesheet_dark(
                f"{Path(__file__).parent}/static/dark.qss",
            ),
        )
        self.ui.action_generate.triggered.connect(
            self.main_win.events.generate_pass_event,
        )
        self.ui.action_login.triggered.connect(self.main_win.events.login_event)
        self.ui.action_register.triggered.connect(self.main_win.events.register_event)
        self.ui.action_account.triggered.connect(self.main_win.events.account_event)
        self.ui.action_forgot_password.triggered.connect(
            self.main_win.events.forgot_password_event,
        )
