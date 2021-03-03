import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget


class Ui_login_widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        app = QtWidgets.QApplication(sys.argv)
        ex = Ui_login_widget()
        window = QtWidgets.QMainWindow()
        ex.setupUi(window)
        window.show()
        sys.exit(app.exec_())

    def setupUi(self, login_widget):
        login_widget.setObjectName("login_widget")
        login_widget.resize(614, 302)
        self.gridLayout = QtWidgets.QGridLayout(login_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(login_widget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 3, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(login_widget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(login_widget)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 2, 0, 1, 1)
        self.login_btn = QtWidgets.QPushButton(login_widget)
        self.login_btn.setObjectName("login_btn")
        self.gridLayout.addWidget(self.login_btn, 3, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(login_widget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 4, 0, 1, 2)
        self.label = QtWidgets.QLabel(login_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(26)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.retranslateUi(login_widget)
        QtCore.QMetaObject.connectSlotsByName(login_widget)

    def retranslateUi(self, login_widget):
        _translate = QtCore.QCoreApplication.translate
        login_widget.setWindowTitle(_translate("login_widget", "Form"))
        self.pushButton.setText(_translate("login_widget", "Forgot Password?"))
        self.lineEdit_2.setText(_translate("login_widget", "Username"))
        self.lineEdit.setText(_translate("login_widget", "Password"))
        self.login_btn.setText(_translate("login_widget", "Login"))
        self.label.setText(_translate("login_widget", "Login"))


class Second(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
