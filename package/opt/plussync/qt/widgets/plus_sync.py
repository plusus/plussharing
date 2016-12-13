"""plus_sync.py: Module for the pull system. That will register the
user et will do the the management of the user access (all created user by this
script are consider end user or professor)"""

# Imports
from getpass import getuser
from os import getuid, path, makedirs, utime
from time import mktime
from pwd import getpwuid

from PySide.QtGui import QMessageBox

from plussync.qt.widgets.db_mysql import DbMysql
from plussync.qt.widgets.file_ftp import Fileftp
from plussync.qt.widgets.files_entries_widget import FileEntry
from plussync.qt.widgets.constant import WarningBox

__author__ = "Sam Charland"
__copyright__ = "Copyright 2016, PLUS-US"


class plus_sync:
    # Path where the pull system put all files received
    C_LOCAL = "%s/Documents/"

    C_HOST_PUB = 'public/%s'
    C_HOST_PRI = 'private/%s'

    # GLOBAL VAR

    # Add module for connexion management
    x_SQL = DbMysql()
    x_FTP = Fileftp()

    # Global var linked to the current user
    mi_IdUser = 0
    msa_Fullname = ''
    ms_Username = ''
    ms_UserHome = ''

    # CHECK IF EXISTING USER OR MAKE IT
    # Function that look if the user exist and if not, it will register him
    def checkUser(self):
        # Opening of connection to the server
        self.x_SQL.open()
        self.x_FTP.open()

        # SQL request to informe the script if the user exist
        s_RequestID = "SELECT iduser FROM user WHERE username = '%s' " % self.ms_Username

        o_Result = None
        # noinspection PyBroadException
        try:
            # try to send the request
            o_Result = self.x_SQL.executeReturnOne(s_RequestID)
        except:
            pass  # if it do not respond, we do nothing

        # Check if we receive an answer on our request, if none than it doesn't exist
        if o_Result is None:
            # Will insert the user in the table wit all his needed information
            s_Request = ("INSERT INTO user (first_name, last_name, username, type_user) "
                         "VALUES ('%s', '%s', '%s', %s)")
            # Insert dynamic information into the query
            a_DataUser = (self.msa_Fullname[0], self.msa_Fullname[1], self.ms_Username, 1)

            # Execute the SQL request ans inserting is data
            self.x_SQL.executeNoReturn(s_Request % a_DataUser)

            # Create his folder in the FTP
            self.x_FTP.createFolder(self.C_HOST_PRI % self.ms_Username + '/')

            # Ask the the SQL what is his ID user
            o_Result = self.x_SQL.executeReturnOne(s_RequestID)

        # Insert his found number into a global var
        self.mi_IdUser = o_Result

        self.x_SQL.close()
        self.x_FTP.close()

    # INITIALIZE ALL CONNECTION AND GLOBAL VAR
    def __init__(self):
        # Get needed information from the linux account system
        self.ms_Username = getuser()
        self.ms_UserHome = getpwuid(getuid())[5]
        self.msa_Fullname = (getpwuid(getuid())[4]).split(' ')

        # If it has no last name
        if len(self.msa_Fullname) <= 1:
            # it will add PlusUS as last name
            self.msa_Fullname = (self.msa_Fullname[0].split(',', 1)[0] + ' PlusUS').split(' ')

        self.checkUser()

    # Function on destruction of class that will close all existing connection
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.x_SQL.close()
        self.x_FTP.close()

    # Function that it making a list of available files from an type of user
    # i_type : value that represent the type of pulling (0 = Public, 1 = Private)
    def getListFile(self, i_type):
        """
        :type i_type: integer
        """
        # Open connections
        self.x_SQL.open()

        # SQL queries needed to get valid information
        s_Request = {
            0: 'SELECT name, CONCAT(\'public/\', name), datemodify FROM public_file_data WHERE validatedby!=0 ',
            1: 'SELECT name, CONCAT(\'private/\', folder, \'/\', name), datemodify FROM private_file_data pfa LEFT '
               'JOIN access a ON a.file_data_idfile = pfa.idfile '
               'WHERE (a.user_iduser = %s)' % self.mi_IdUser
        }[i_type]

        # Execute the request
        o_Result = self.x_SQL.executeReturnAll(s_Request)

        # Close connection
        self.x_SQL.close()

        entResult = []
        if o_Result:
            for rowResult in o_Result:
                entResult.append(FileEntry(0, rowResult[0], rowResult[1], rowResult[2]))

        return entResult

    # Function that is downloading a list of file path from the server
    def getFile(self, File):
        """
        :type: list[FileEntry]
        """
        self.x_SQL.open()
        self.x_FTP.open()

        s_local_path = self.C_LOCAL % self.ms_UserHome

        # If path do not exist, it create it
        if not path.exists(s_local_path):
            makedirs(s_local_path)

        # Loop into the parameter list
        for fileInfo in File:
            """:type fileInfo: FileEntry"""
            name = fileInfo.name

            # If the file does exist into the download directory
            if path.exists(s_local_path + name):
                choice = WarningBox.warningDialogBox("Attention - Documents duplique",
                                               "Dans le dossier Documents, un fichier au nom de \'" +
                                               name + "\' est déjà situé à cette emplacement.</p> "
                                               "<p align='center'>Souhaitez-vous ecraser ce fichier par "
                                               "celui téléchargé?</p> <p align='center'>Si oui, vous allez "
                                               "perdre les informations de l'ancien fichier.",
                                               WarningBox.YesNo)
            else:
                choice = QMessageBox.Yes

            # If the answer from the user is yes than download the file and
            # adjust is modified date to the current lastUpdate time on the server
            if choice == QMessageBox.Yes:
                self.x_FTP.getFile(fileInfo.hostFilePath, s_local_path + name)
                lastTime = mktime(fileInfo.lastUpdate.timetuple())
                utime(s_local_path + name, (lastTime, lastTime))

        # At the end of all download, an popup show to say all download ar completed
        WarningBox.warningDialogBox("Téléchargement(s) complété(s)",
                                    "Tous les téléchargements ont été complétés",
                                    WarningBox.Ok)

        # Close connection
        self.x_SQL.close()
        self.x_FTP.close()
