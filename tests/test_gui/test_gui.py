import pytest
from PyQt5 import QtCore

from lightning_pass.gui.gui import UiLightningPass


@pytest.fixture
def app(qtbot):
    test_app = UiLightningPass()
    qtbot.addWidget(test_app)
    return test_app


"""
Test if each button correctly switches to correct stackedWidget.

Index description:
Index 0: app.home
Index 1: app.login
Index 2: app.register_2
Index 3: app.forgot_password
Index 4: app.generate_password
Index 5: app.generate_pass_phase2
Index 6: app.account
"""


def test_home_buttons(app, qtbot):
    qtbot.mouseClick(app.home_login_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 1
    qtbot.mouseClick(app.home_register_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 2
    qtbot.mouseClick(app.home_generate_password_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 4


def test_login_buttons(app, qtbot):
    qtbot.mouseClick(app.log_main_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 0
    qtbot.mouseClick(app.log_forgot_pass_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 3


def test_register_2_buttons(app, qtbot):
    qtbot.mouseClick(app.reg_main_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 0


def test_forgot_password_buttons(app, qtbot):
    qtbot.mouseClick(app.forgot_pass_main_menu_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 0


def test_generate_pass_buttons(app, qtbot):
    qtbot.mouseClick(app.generate_pass_main_menu_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 0


def test_generate_pass_phase2_buttons(app, qtbot):
    qtbot.mouseClick(app.generate_pass_p2_main_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 0


def test_account_buttons(app, qtbot):
    qtbot.mouseClick(app.account_main_menu_btn, QtCore.Qt.LeftButton)
    assert app.stacked_widget.currentIndex() == 0
