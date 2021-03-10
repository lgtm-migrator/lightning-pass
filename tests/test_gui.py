from __future__ import annotations

import pytest
from PyQt5 import QtCore
from pytestqt.qtbot import QtBot

from lightning_pass.gui.gui import LightningPassWindow


@pytest.fixture
def app(qtbot: QtBot) -> LightningPassWindow:
    """Fixture for GUI tests.

    :param QtBot: clicks on buttons

    :returns test_app: app instance
    :rtype LightningPassWindow

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
    app: LightningPassWindow, qtbot: QtBot, widget: str, index: int
) -> None:
    """Test if each button correctly switches to correct stacked_widget index.

    :param LightningPassWindow app: main window instance
    :param QtBot qtbot: QtBot instance
    :param str widget: QPushButton pointer
    :param int index: stacked_widget expected index,
        index 0: app.ui.home
        index 1: app.ui.login
        index 2: app.ui.register_2
        index 3: app.ui.forgot_password
        index 4: app.ui.generate_password
        index 5: app.ui.generate_pass_phase2
        index 6: app.ui.account

    """
    widget = getattr(app.ui, widget)
    qtbot.mouseClick(widget, QtCore.Qt.LeftButton)
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
    action = getattr(app.ui, menu_bar_action)
    action.trigger()
    assert app.ui.stacked_widget.currentIndex() == index
