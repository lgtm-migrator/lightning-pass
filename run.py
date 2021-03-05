import sys

from lightning_pass import create_app

app = create_app()

if __name__ == "__main__":
    sys.exit(app.exec_())
