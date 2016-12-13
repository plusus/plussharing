from PySide.QtCore import *
from PySide.QtGui import *
import ScriptShare
import SharingLogic

class PublicForm:
    def __init__(self, inScriptShare):
        """
        Flow of initialisation to create and show the form in QT
        :param inScriptShare: The ScriptShare object containing the paths and names information
        """
        self.publicDialog = QDialog()
        self.sharingLogic = SharingLogic.SharingLogic(inScriptShare)
        self.create_form()
        self.show_form()


    def create_form(self):
        """
        Creating the whole UI for the public sharing window
        """
        self.publicDialog.setWindowTitle("Partage publique")
        self.publicDialog.questionLabel = QLabel("Voulez-vous vraiment partager ce(s) fichier(s) de facon publique?\n"
                                            "Tous les utilisateurs ayant acces au serveur pourront le(s) consulter.")  # Do not put any weird letter like accents :P!
        self.publicDialog.yesButton = QPushButton("Oui")
        self.publicDialog.noButton = QPushButton("Non")
        self.publicDialog.yesButton.clicked.connect(self.confirm)
        self.publicDialog.noButton.clicked.connect(self.deny)  # This doesn't do anything beside exiting properly.

        vLayout = QVBoxLayout()
        vLayout.addWidget(self.publicDialog.questionLabel)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.publicDialog.yesButton)
        buttonsLayout.addWidget(self.publicDialog.noButton)
        vLayout.addLayout(buttonsLayout)

        self.publicDialog.setLayout(vLayout)


    def show_form(self):
        """
        Simply calls the show function of the dialog to make it appear on the screen
        """
        self.publicDialog.show()

    def confirm(self):
        """
        Will relay the confirmation to push all the files in the DB and FTP through the SharingLogic object
        """
        self.sharingLogic.public_share()
        self.publicDialog.close()

    def deny(self):
        """
        Called when the cancel button has been pressed Do nothing and close everything
        """
        self.publicDialog.close()