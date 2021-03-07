import sys

from lightning_pass import create_app

if __name__ == "__main__":
    app = create_app()
    sys.exit(app.exec_())
