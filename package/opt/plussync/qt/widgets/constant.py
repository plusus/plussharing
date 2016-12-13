"""constant.py: Module that have have many constant value of enumaration.
That allow us to have many information linked in one file if in need of
modification. That also help on sharing some information between python codes"""

from enum import Enum

from PySide.QtGui import QColor
from PySide.QtGui import QMessageBox


# Enumeration class for all available status and wait they represent
class Status(Enum):
    Null = 0
    New_file = 1
    Update_server = 2
    Seen_user = 3
    Download_updated_server = 4
    Download_same = 5
    Download_updated_user = 6
    Download_seen_user = 7


# Enumeration class for all color set we use (in RGB order)
class RGBColors(Enum):
    # RGB colors for Qt frame
    White = QColor(255, 255, 255)
    Emerald = QColor(0, 201, 87)


# class for generating an popup box (use to warn the user)
class WarningBox:
    Ok = 0
    YesNo = 1
    YesNoAll = 2
    SaveDiscCan = 3

    # Function that is creating an Warning dialog box with option to popup
    # (warning this is a blocking function)
    @staticmethod
    def warningDialogBox(title, message, typeButton=Ok):
        msgBox = QMessageBox()
        msgBox.setText("<p align='center'>" + title + "</p>")
        msgBox.setInformativeText("<p align='center'>" + message + "</p>")

        if typeButton:
            if typeButton == WarningBox.YesNo:
                msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                msgBox.setDefaultButton(QMessageBox.No)
            elif typeButton == WarningBox.YesNoAll:
                msgBox.setStandardButtons(QMessageBox.No | QMessageBox.NoToAll | QMessageBox.Yes | QMessageBox.YesToAll)
                msgBox.setDefaultButton(QMessageBox.No)
            elif typeButton == WarningBox.SaveDiscCan:
                msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Save)

        return msgBox.exec_()
