import pytest

from lightning_pass.gui import gui


@pytest.fixture()
def app(qtbot):
    gui.Gui()
