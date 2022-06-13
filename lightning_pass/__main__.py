"""Run the application."""
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parent.parent.as_posix())

import lightning_pass.gui.window as window
from lightning_pass.settings import setup_database

if __name__ == "__main__":
    setup_database()
    window.run_main_window(splash=True)
