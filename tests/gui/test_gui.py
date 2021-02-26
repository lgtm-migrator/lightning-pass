import pytest
from PyQt5 import QtCore
from lightning_pass.gui import gui


@pytest.fixture()
def app(qtbot):
    app = gui.Gui()

