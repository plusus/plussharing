from PySide.QtCore import *
from PySide.QtGui import *
import ScriptShare
import SharingLogic

class PrivateForm:
    def __init__(self, inScriptShare):
        """
        Flow of initialisation to create and show the form in QT
        :param inScriptShare: The ScriptShare object containing the paths and names information
        """
        self.personnalDialog = QDialog()
        self.scriptObject = inScriptShare
        self.sharingLogic = SharingLogic.SharingLogic(inScriptShare)
        self.create_form()
        self.show_form()

    def create_form(self):
        """
        Creating the whole UI for the personnal sharing window
        """
        self.personnalDialog.setWindowTitle("Partage personnel")

        # Create the title and the main label of the window
        self.personnalDialog.questionLabel = QLabel("Veuillez selectionner le ou les destinataires dans la liste des utilisateurs.")
        self.personnalDialog.questionLabel.setWordWrap(True)
        self.personnalDialog.questionLabel.setFixedWidth(250)
        self.personnalDialog.titleFont = QFont()
        self.personnalDialog.titleFont.setBold(True)
        self.personnalDialog.questionLabel.setFont(self.personnalDialog.titleFont)
        self.personnalDialog.questionLayout = QVBoxLayout()
        self.personnalDialog.questionLayout.addWidget(self.personnalDialog.questionLabel)
        self.personnalDialog.questionLayout.setAlignment(self.personnalDialog.questionLabel, Qt.AlignTop)


        #Creates the view of the files list
        self.personnalDialog.sendingInfoLayout = QVBoxLayout()
        self.personnalDialog.sendingInfoLayout.setSpacing(10)
        self.personnalDialog.sendingInfoLayout.addWidget(QLabel("Fichier(s) qui sera(seront) remis : "))
        self.personnalDialog.filesSharedList = QListView()
        self.personnalDialog.filesSharedListModel = QStandardItemModel(self.personnalDialog.filesSharedList)
        fileIcon = QIcon("/usr/share/sharingfiles/icons/file.png")
        for fileName in self.scriptObject.get_files_list('Names'):
            # Create an item
            item = QStandardItem(fileName)
            item.setEditable(False)
            item.setCheckable(True)
            item.setCheckState(Qt.Checked)
            item.setSelectable(False)
            item.setIcon(fileIcon)
            self.personnalDialog.filesSharedListModel.appendRow(item)
        # Add the item to the model
        self.personnalDialog.filesSharedList.setModel(self.personnalDialog.filesSharedListModel)
        self.personnalDialog.sendingInfoLayout.addWidget(self.personnalDialog.filesSharedList)
        self.personnalDialog.questionLayout.addLayout(self.personnalDialog.sendingInfoLayout)
        self.personnalDialog.questionLayout.setAlignment(self.personnalDialog.sendingInfoLayout, Qt.AlignVCenter)


        #Create the users list
        self.personnalDialog.listTitleLabel = QLabel("Liste des utilisateurs : ")
        self.personnalDialog.receiversListWidget = QListView()
        self.personnalDialog.receiversListWidget.setMinimumSize(int(200), int(300))
        self.personnalDialog.receiversListModel = QStandardItemModel(self.personnalDialog.receiversListWidget)
        self.personnalDialog.colleagueIcon = QIcon("/usr/share/sharingfiles/icons/person.png")
        for colleague in self.sharingLogic.get_colleagues_list():
            # Create an item with a caption
            item = QStandardItem(colleague)
            item.setEditable(False)
            item.setIcon(self.personnalDialog.colleagueIcon)
            item.setCheckable(True)
            # Add the item to the model
            self.personnalDialog.receiversListModel.appendRow(item)
        self.personnalDialog.receiversListWidget.setModel(self.personnalDialog.receiversListModel)
        self.personnalDialog.listLayout = QVBoxLayout()
        self.personnalDialog.listLayout.addWidget(self.personnalDialog.listTitleLabel)
        self.personnalDialog.listLayout.addWidget(self.personnalDialog.receiversListWidget)


        #Create the buttons and their connections logic
        self.personnalDialog.yesButton = QPushButton("Partager")
        self.personnalDialog.noButton = QPushButton("Annuler")
        self.personnalDialog.yesButton.clicked.connect(lambda: self.share_clicked(self.personnalDialog.filesSharedListModel, self.personnalDialog.receiversListModel,
                                                                                 self.personnalDialog))  # Lamba needed to send parameter to function
        self.personnalDialog.noButton.clicked.connect(self.deny)
        self.personnalDialog.buttonsLayout = QHBoxLayout()
        self.personnalDialog.buttonsLayout.addWidget(self.personnalDialog.yesButton)
        self.personnalDialog.buttonsLayout.addWidget(self.personnalDialog.noButton)
        self.personnalDialog.questionLayout.addLayout(self.personnalDialog.buttonsLayout)
        self.personnalDialog.questionLayout.setAlignment(self.personnalDialog.buttonsLayout, Qt.AlignBottom)


        #Create the whole layout.
        self.personnalDialog.personnalLayout = QHBoxLayout()
        self.personnalDialog.personnalLayout.addLayout(self.personnalDialog.questionLayout)
        self.personnalDialog.personnalLayout.addLayout(self.personnalDialog.listLayout)
        self.personnalDialog.setLayout(self.personnalDialog.personnalLayout)
        self.personnalDialog.show()

    def show_form(self):
        """
        Simply calls the show function of the dialog to make it appear on the screen
        """
        self.personnalDialog.show()

    def confirm(self):
        """
        Will relay the confirmation to push all the files in the DB and FTP through the SharingLogic object
        """
        self.personnalDialog.close()

    def deny(self):
        """
        Called when the cancel button has been pressed Do nothing and close everything
        """
        self.personnalDialog.close()

    def share_clicked(self, inFileModel, inReceiverModel, inDialog):
        """
        Logic to control and do the verification of the form when the button "Partager" is clicked.
        :param inFileModel: The model containing the list of files shown in the dialog
        :param inReceiverModel: The model containing the list of colleagues shown in the dialog
        :param inDialog: The dialog containing both the upper models
        """
        errorMessage = ""
        filesList = []
        for fileIndex in range(inFileModel.rowCount()):
            file = inFileModel.item(fileIndex)
            if file.checkState() == Qt.Checked:
                filesList.append(file.text())

        receiversList = []
        for receiverIndex in range(inReceiverModel.rowCount()):
            receiver = inReceiverModel.item(receiverIndex)
            if receiver.checkState() == Qt.Checked:
                receiversList.append(receiver.text())

        if(len(receiversList) < 1 or len(filesList) < 1):
            inDialog.hide(); #We will get back to the original dialog after showing up the error, but hide it for now.

            errorMessage = "Veuillez vous assurez de sélectionner un minimum d'un fichier ainsi qu'un destinataire."
            errorDialog = QDialog()
            errorDialog.setWindowTitle("Informations incompletes")

            # Create Widget
            errorDialog.errorLabel = QLabel(errorMessage)
            errorDialog.okButton = QPushButton("Okay")
            errorDialog.okButton.connect(SIGNAL('clicked()'), errorDialog.close)

            # Create layout and add widgets
            errorDialog.vLayout = QVBoxLayout()
            errorDialog.vLayout.addWidget(errorDialog.errorLabel)
            errorDialog.vLayout.addWidget(errorDialog.okButton)

            # Set dialog layout
            errorDialog.setLayout(errorDialog.vLayout)
            errorDialog.setAttribute(Qt.WA_DeleteOnClose)
            errorDialog.exec_()
            inDialog.show()
        else:
            for receiver in receiversList:
                self.sharingLogic.personnal_share(receiver, filesList)
            self.confirm()