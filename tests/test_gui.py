"""Test module for the gui package."""
from __future__ import annotations

import pytest
from PyQt5 import QtCore
from pytestqt.qtbot import QtBot

from lightning_pass.gui.window import LightningPassWindow


@pytest.fixture()
def app(qtbot: QtBot) -> LightningPassWindow:
    """Fixture for GUI tests.

    :param QtBot qtbot: Click on buttons like a human

    :returns: app instance with QtBot widget

    """
    test_app = LightningPassWindow()
    qtbot.addWidget(test_app)
    return test_app


@pytest.mark.parametrize(
    "widget, index",
    [
        ("home_login_btn", 1),
        ("home_register_btn", 2),
        ("home_generate_password_btn", 4),
        ("log_main_btn", 0),
        ("log_forgot_pass_btn", 3),
        ("reg_main_btn", 0),
        ("forgot_pass_main_menu_btn", 0),
        ("generate_pass_main_menu_btn", 0),
        ("generate_pass_p2_main_btn", 0),
        ("account_main_menu_btn", 0),
    ],
)
def test_buttons(
    app: LightningPassWindow,
    qtbot: QtBot,
    widget: str,
    index: int,
) -> None:
    """Test if each button correctly switches to correct stacked_widget index.

    :param LightningPassWindow app: Main window instance
    :param QtBot qtbot: QtBot instance
    :param str widget: QPushButton pointer
    :param int index: stacked_widget expected index

    Index description:
        1) index 0: app.ui.home
        2) index 1: app.ui.login
        3) index 2: app.ui.register_2
        4) index 3: app.ui.forgot_password
        5) index 4: app.ui.generate_password
        6) index 5: app.ui.generate_pass_phase2
        7) index 6: app.ui.account

    Fails if stacked_widget didn't change index.

    """
    widget = getattr(app.ui, widget)

    qtbot.mouseClick(widget, QtCore.Qt.LeftButton)  # act

    assert app.ui.stacked_widget.currentIndex() == index


@pytest.mark.parametrize(
    "menu_bar_action, index",
    [
        ("action_main_menu", 0),
        ("action_generate", 4),
        ("action_login", 1),
        ("action_register", 2),
        ("action_forgot_password", 3),
    ],
)
def test_menu_bar(app: LightningPassWindow, menu_bar_action: str, index: int) -> None:
    """Test if each menu bar action correctly switches to correct stacked_widget index.

    :param LightningPassWindow app: Main window instance
    :param str menu_bar_action: QPushButton pointer
    :param int index: stacked_widget expected index

    Index description:
        1) index 0: app.ui.home
        2) index 1: app.ui.login
        3) index 2: app.ui.register_2
        4) index 3: app.ui.forgot_password
        5) index 4: app.ui.generate_password
        6) index 5: app.ui.generate_pass_phase2
        7) index 6: app.ui.account

    Fails if stacked_widget didn't change index.

    """
    action = getattr(app.ui, menu_bar_action)

    action.trigger()  # act

    assert app.ui.stacked_widget.currentIndex() == index
