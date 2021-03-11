"""Module containing the MessageBoxes class used for showing various message boxes."""
from __future__ import annotations

import re

from PyQt5.QtWidgets import QMessageBox, QPushButton, QWidget


class MessageBoxes(QWidget):
    """This class holds the functionality to show various message boxes."""

    def __init__(self, child, parent):
        """Class constructor."""
        super().__init__(parent)
        self.events = parent.events
        self.main_win = child
        self.title = "Lightning Pass"

    def invalid_username_box(self, parent: str) -> None:
        """Show invalid username message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("This username is invalid.")
        box.setIcon(QMessageBox.Warning)

        box.setInformativeText("Username be at least 5 characters long.")
        box.exec_()

    def invalid_password_box(self, parent: str) -> None:
        """Show invalid password message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("This password is invalid.")
        box.setIcon(QMessageBox.Warning)

        box.setInformativeText(
            """Password must be at least 8 characters long,
contain at least 1 capital letter,
contain at least 1 number
contain at least one special character."""
        )
        box.exec_()

    def invalid_email_box(self, parent: str) -> None:
        """Show invalid email message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("Please enter a valid email.")
        box.setIcon(QMessageBox.Warning)
        box.exec_()

    def invalid_login_box(self, parent: str) -> None:
        """Show invalid login message box.

        :param str parent: Specifies which window instantiated current box

        """

        def event_handler(btn: QPushButton) -> None:
            """Handler for clicks on message box window

            :param btn: Clicked button

            """
            if re.findall("Yes", btn.text()):
                self.events.forgot_password_event()
            elif re.findall("No", btn.text()):
                self.events.login_event()

        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("Invalid login details.")
        box.setIcon(QMessageBox.Warning)

        box.setInformativeText("Forgot password?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.Yes)
        box.buttonClicked.connect(event_handler)
        box.exec_()

    def username_already_exists_box(self, parent: str) -> None:
        """Show username already exists message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("This username already exists.")
        box.setIcon(QMessageBox.Warning)
        box.exec_()

    def email_already_exists_box(self, parent: str) -> None:
        """Show email already exists message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("This email already exists.")
        box.setIcon(QMessageBox.Warning)
        box.exec_()

    def passwords_do_not_match_box(self, parent: str) -> None:
        """Show passwords do not match message box.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("Passwords don't match.")
        box.setIcon(QMessageBox.Warning)
        box.exec_()

    def account_creation_box(self, parent: str) -> None:
        """Show successful account creatio message box.

        :param str parent: Specifies which window instantiated current box

        """

        def event_handler(btn: QPushButton) -> None:
            """Handler for clicks on message box window

            :param btn: Clicked button

            """
            if re.findall("Yes", btn.text()):
                self.events.login_event()
            elif re.findall("No", btn.text()):
                self.events.register_event()

        box = QMessageBox(self.main_win)
        box.setWindowTitle(parent)
        box.setText("Account successfuly created.")
        box.setIcon(QMessageBox.Question)

        box.setInformativeText("Would you like to move to the login page?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.Yes)
        box.buttonClicked.connect(event_handler)
        box.exec_()

    def no_case_type_box(self, parent: str) -> None:
        """Show message box indicating that password can't be generated with current case type option.

        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("Passwords can't be generate without any case type.")
        box.setIcon(QMessageBox.Warning)
        box.exec_()

    def login_required_box(self, parent: str) -> None:
        """Show message box indicating that password can't be generated with current case type option.

        :param str parent: Specifies which window instantiated current box

        """

        def event_handler(btn: QPushButton) -> None:
            """Handler for clicks on message box window

            :param btn: Clicked button

            """
            if re.findall("Yes", btn.text()):
                self.events.login_event()

        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText("Please log in to access that page.")
        box.setIcon(QMessageBox.Warning)

        box.setInformativeText("Would you like to move to the login page?")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        box.setDefaultButton(QMessageBox.No)
        box.buttonClicked.connect(event_handler)
        box.exec_()

    def details_updated_box(self, detail: str, parent: str) -> None:
        """Show message box indicating that password can't be generated with current case type option.

        :param str detail: Specifies which detail was updated
        :param str parent: Specifies which window instantiated current box

        """
        box = QMessageBox(self.main_win)
        box.setWindowTitle(f"{self.title} - {parent}")
        box.setText(f"Your {detail} has been successfully updated!")
        box.setIcon(QMessageBox.Question)
        box.exec_()
