from PySide.QtGui import QMessageBox


class QuickWarningBox():
    def warningDialogBox (self, title, message, typeButton='ok'):
        msgBox = QMessageBox()
        msgBox.setText("<p align='center'>" + title + "</p>")
        msgBox.setInformativeText("<p align='center'>" + message + "</p>")

        if typeButton:
            if typeButton.lower() == "yesno":
                msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                msgBox.setDefaultButton(QMessageBox.No)
            elif typeButton.lower() == "yesnoall":
                msgBox.setStandardButtons(QMessageBox.No | QMessageBox.NoToAll| QMessageBox.Yes | QMessageBox.YesToAll)
                msgBox.setDefaultButton(QMessageBox.No)
            elif typeButton.lower() == "savedisccan":
                msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Save)

        return msgBox.exec_()
