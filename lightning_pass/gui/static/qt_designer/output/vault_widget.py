# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vault_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.3
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_vault_widget(object):
    def setupUi(self, vault_widget):
        vault_widget.setObjectName("vault_widget")
        vault_widget.resize(416, 353)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(vault_widget.sizePolicy().hasHeightForWidth())
        vault_widget.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(vault_widget)
        self.gridLayout.setObjectName("gridLayout")
        self.vault_platform_line = QtWidgets.QLineEdit(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe Print")
        font.setPointSize(26)
        self.vault_platform_line.setFont(font)
        self.vault_platform_line.setText("")
        self.vault_platform_line.setClearButtonEnabled(True)
        self.vault_platform_line.setObjectName("vault_platform_line")
        self.gridLayout.addWidget(self.vault_platform_line, 0, 0, 1, 5)
        self.vault_website_lbl = QtWidgets.QLabel(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_website_lbl.setFont(font)
        self.vault_website_lbl.setObjectName("vault_website_lbl")
        self.gridLayout.addWidget(self.vault_website_lbl, 1, 0, 1, 3)
        self.vault_web_line = QtWidgets.QLineEdit(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_web_line.setFont(font)
        self.vault_web_line.setText("")
        self.vault_web_line.setClearButtonEnabled(True)
        self.vault_web_line.setObjectName("vault_web_line")
        self.gridLayout.addWidget(self.vault_web_line, 1, 3, 1, 1)
        self.vault_open_web_tool_btn = QtWidgets.QToolButton(vault_widget)
        self.vault_open_web_tool_btn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.vault_open_web_tool_btn.setAutoRaise(True)
        self.vault_open_web_tool_btn.setArrowType(QtCore.Qt.UpArrow)
        self.vault_open_web_tool_btn.setObjectName("vault_open_web_tool_btn")
        self.gridLayout.addWidget(self.vault_open_web_tool_btn, 1, 4, 1, 1)
        self.vault_username_lbl = QtWidgets.QLabel(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_username_lbl.setFont(font)
        self.vault_username_lbl.setObjectName("vault_username_lbl")
        self.gridLayout.addWidget(self.vault_username_lbl, 2, 0, 1, 3)
        self.vault_username_line = QtWidgets.QLineEdit(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_username_line.setFont(font)
        self.vault_username_line.setText("")
        self.vault_username_line.setClearButtonEnabled(False)
        self.vault_username_line.setObjectName("vault_username_line")
        self.gridLayout.addWidget(self.vault_username_line, 2, 3, 1, 1)
        self.vault_copy_username_tool_btn = QtWidgets.QToolButton(vault_widget)
        self.vault_copy_username_tool_btn.setCursor(
            QtGui.QCursor(QtCore.Qt.ArrowCursor)
        )
        self.vault_copy_username_tool_btn.setToolTipDuration(5)
        self.vault_copy_username_tool_btn.setAccessibleName("")
        self.vault_copy_username_tool_btn.setAccessibleDescription("")
        self.vault_copy_username_tool_btn.setCheckable(False)
        self.vault_copy_username_tool_btn.setToolButtonStyle(
            QtCore.Qt.ToolButtonIconOnly
        )
        self.vault_copy_username_tool_btn.setAutoRaise(True)
        self.vault_copy_username_tool_btn.setArrowType(QtCore.Qt.DownArrow)
        self.vault_copy_username_tool_btn.setObjectName("vault_copy_username_tool_btn")
        self.gridLayout.addWidget(self.vault_copy_username_tool_btn, 2, 4, 1, 1)
        self.vault_email_lbl = QtWidgets.QLabel(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_email_lbl.setFont(font)
        self.vault_email_lbl.setObjectName("vault_email_lbl")
        self.gridLayout.addWidget(self.vault_email_lbl, 3, 0, 1, 2)
        self.vault_email_line = QtWidgets.QLineEdit(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_email_line.setFont(font)
        self.vault_email_line.setText("")
        self.vault_email_line.setClearButtonEnabled(True)
        self.vault_email_line.setObjectName("vault_email_line")
        self.gridLayout.addWidget(self.vault_email_line, 3, 3, 1, 1)
        self.vault_copy_email_tool_btn = QtWidgets.QToolButton(vault_widget)
        self.vault_copy_email_tool_btn.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.vault_copy_email_tool_btn.setToolTipDuration(5)
        self.vault_copy_email_tool_btn.setAutoRaise(True)
        self.vault_copy_email_tool_btn.setArrowType(QtCore.Qt.DownArrow)
        self.vault_copy_email_tool_btn.setObjectName("vault_copy_email_tool_btn")
        self.gridLayout.addWidget(self.vault_copy_email_tool_btn, 3, 4, 1, 1)
        self.vault_password_lbl = QtWidgets.QLabel(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_password_lbl.setFont(font)
        self.vault_password_lbl.setObjectName("vault_password_lbl")
        self.gridLayout.addWidget(self.vault_password_lbl, 4, 0, 1, 3)
        self.vault_password_line = QtWidgets.QLineEdit(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_password_line.setFont(font)
        self.vault_password_line.setText("")
        self.vault_password_line.setEchoMode(QtWidgets.QLineEdit.Password)
        self.vault_password_line.setClearButtonEnabled(True)
        self.vault_password_line.setObjectName("vault_password_line")
        self.gridLayout.addWidget(self.vault_password_line, 4, 3, 1, 1)
        self.vault_copy_password_tool_btn = QtWidgets.QToolButton(vault_widget)
        self.vault_copy_password_tool_btn.setToolTipDuration(5)
        self.vault_copy_password_tool_btn.setAutoRaise(True)
        self.vault_copy_password_tool_btn.setArrowType(QtCore.Qt.DownArrow)
        self.vault_copy_password_tool_btn.setObjectName("vault_copy_password_tool_btn")
        self.gridLayout.addWidget(self.vault_copy_password_tool_btn, 4, 4, 1, 1)
        self.vault_backward_tool_btn = QtWidgets.QToolButton(vault_widget)
        self.vault_backward_tool_btn.setAutoRaise(True)
        self.vault_backward_tool_btn.setArrowType(QtCore.Qt.LeftArrow)
        self.vault_backward_tool_btn.setObjectName("vault_backward_tool_btn")
        self.gridLayout.addWidget(self.vault_backward_tool_btn, 5, 0, 1, 1)
        self.vault_page_lbl = QtWidgets.QLabel(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Black")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.vault_page_lbl.setFont(font)
        self.vault_page_lbl.setObjectName("vault_page_lbl")
        self.gridLayout.addWidget(self.vault_page_lbl, 5, 1, 1, 1)
        self.vault_forward_tool_btn = QtWidgets.QToolButton(vault_widget)
        self.vault_forward_tool_btn.setAutoRaise(True)
        self.vault_forward_tool_btn.setArrowType(QtCore.Qt.RightArrow)
        self.vault_forward_tool_btn.setObjectName("vault_forward_tool_btn")
        self.gridLayout.addWidget(self.vault_forward_tool_btn, 5, 2, 1, 1)
        self.vault_update_btn = QtWidgets.QPushButton(vault_widget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(10)
        self.vault_update_btn.setFont(font)
        self.vault_update_btn.setObjectName("vault_update_btn")
        self.gridLayout.addWidget(self.vault_update_btn, 5, 3, 1, 1)

        self.retranslateUi(vault_widget)
        QtCore.QMetaObject.connectSlotsByName(vault_widget)

    def retranslateUi(self, vault_widget):
        _translate = QtCore.QCoreApplication.translate
        vault_widget.setWindowTitle(_translate("vault_widget", "Form"))
        self.vault_platform_line.setPlaceholderText(
            _translate("vault_widget", "Platform name")
        )
        self.vault_website_lbl.setText(_translate("vault_widget", "Website:"))
        self.vault_web_line.setPlaceholderText(
            _translate("vault_widget", "Enter URL for your platform.")
        )
        self.vault_open_web_tool_btn.setStatusTip(
            _translate("vault_widget", "Launch website")
        )
        self.vault_open_web_tool_btn.setText(_translate("vault_widget", "..."))
        self.vault_username_lbl.setText(_translate("vault_widget", "Username:"))
        self.vault_username_line.setPlaceholderText(
            _translate("vault_widget", "Enter account username.")
        )
        self.vault_copy_username_tool_btn.setToolTip(
            _translate("vault_widget", "Copy username")
        )
        self.vault_copy_username_tool_btn.setStatusTip(
            _translate("vault_widget", "Copy username")
        )
        self.vault_copy_username_tool_btn.setWhatsThis(
            _translate("vault_widget", "Copy username")
        )
        self.vault_copy_username_tool_btn.setText(_translate("vault_widget", "..."))
        self.vault_email_lbl.setText(_translate("vault_widget", "Email:"))
        self.vault_email_line.setPlaceholderText(
            _translate("vault_widget", "Enter account email.")
        )
        self.vault_copy_email_tool_btn.setToolTip(
            _translate("vault_widget", "Copy email")
        )
        self.vault_copy_email_tool_btn.setStatusTip(
            _translate("vault_widget", "Copy email")
        )
        self.vault_copy_email_tool_btn.setWhatsThis(
            _translate("vault_widget", "Copy email")
        )
        self.vault_copy_email_tool_btn.setText(_translate("vault_widget", "..."))
        self.vault_password_lbl.setText(_translate("vault_widget", "Password:"))
        self.vault_password_line.setPlaceholderText(
            _translate("vault_widget", "Enter account password.")
        )
        self.vault_copy_password_tool_btn.setToolTip(
            _translate("vault_widget", "Copy password")
        )
        self.vault_copy_password_tool_btn.setStatusTip(
            _translate("vault_widget", "Copy password")
        )
        self.vault_copy_password_tool_btn.setWhatsThis(
            _translate("vault_widget", "Copy password")
        )
        self.vault_copy_password_tool_btn.setText(_translate("vault_widget", "..."))
        self.vault_backward_tool_btn.setText(_translate("vault_widget", "..."))
        self.vault_page_lbl.setText(_translate("vault_widget", " 0"))
        self.vault_forward_tool_btn.setText(_translate("vault_widget", "..."))
        self.vault_update_btn.setText(_translate("vault_widget", "Update"))
