import re

from PyQt5.QtWidgets import QMessageBox, QWidget


class MessageBoxes(QWidget):
    def __init__(self, parent):
        """Class constructor."""
        super().__init__(parent)
        self.main_win = parent
        self.title = "Lightning Pass"

    def invalid_username_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "This username is invalid.",
            QMessageBox.Warning,
        )

    def invalid_password_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "This password is invalid.",
            QMessageBox.Warning,
        )

    def invalid_email_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "This email is invalid.",
            QMessageBox.Warning,
        )

    def invalid_login_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "An account with that username or password doesn't exist.",
            QMessageBox.Warning,
        )

    def username_already_exists_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "This username already exists.",
            QMessageBox.Warning,
        )

    def email_already_exists_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "This email already exists.",
            QMessageBox.Warning,
        )

    def passwords_do_not_match_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "The passwords you entered do not match.",
            QMessageBox.Warning,
        )

    def account_creation_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "Account successfully created!",
            QMessageBox.Question,
            successful_registration=True,
        )

    def no_case_type_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "Can't generate password without any case type.",
            QMessageBox.Warning,
        )

    def login_required_box(self, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            "Please log in to access that page.",
            QMessageBox.Warning,
        )

    def details_updated_box(self, detail, widget):
        self.show_message_box(
            f"{self.title} - {widget}",
            f"Your {detail} has been successfully updated!",
            QMessageBox.Question,
        )

    def message_box_event(self, btn):
        """Handler for clicks on message box window"""
        if re.findall("Yes", btn.text()):
            self.login_event()
        if re.findall("Cancel", btn.text()):
            self.register_event()

    def show_message_box(self, title, text, icon, successful_registration=False):
        """Show message box with information about registration process"""
        er = QMessageBox(self.main_win)
        er.setWindowTitle(title)
        er.setText(text)
        er.setIcon(icon)
        if successful_registration is True:
            er.setInformativeText("Would you like to move to the login page?")
            er.setStandardButtons(QMessageBox.Yes | QMessageBox.Close)
            er.setDefaultButton(QMessageBox.Yes)
            er.buttonClicked.connect(self.message_box_event)
        _ = er.exec_()
