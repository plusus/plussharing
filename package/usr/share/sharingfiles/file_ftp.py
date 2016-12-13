"""file_ftp.py: Module that do the management of the FTP server (allow you to
send, receive or interact with information, file and folder). no error handler
put except on the opening of connection."""

# IMPORTS
import pysftp
from paramiko.ssh_exception import SSHException
from configparser import ConfigParser
from plussync.qt.widgets.constant import WarningBox

__author__ = "Sam Charland"
__copyright__ = "Copyright 2016, PLUS-US"


class Fileftp:

    # FUNCTIONS
    def __init__(self):
        self.mc_cnxsftp = None
        # Load the configuration parser
        config = ConfigParser()
        # read the file configuration
        config.read('/etc/plussharing.conf')

        confSet = ''
        if 'FTPSERVER' in config:
            confSet = 'FTPSERVER'
        elif 'DEFAULT' in config:
            confSet = 'DEFAULT'

        # Load the configurations
        if len(confSet) > 0:
            self.C_USER = config[confSet]['UserLogin']
            self.C_PASS = config[confSet]['PassPhrase']
            self.C_IP = config[confSet]['HostAddress']
            self.C_PORTFILE = config[confSet]['HostPort']

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        self.open()
        return self

    # Connection openning
    def open(self):
        try:
            # Force to accept the RSA key of the server...
            cnOpt = pysftp.CnOpts()
            cnOpt.hostkeys = None
            # Connect to the secured server FTP
            self.mc_cnxsftp = pysftp.Connection(self.C_IP, username=self.C_USER, password=self.C_PASS, cnopts=cnOpt)
        except SSHException as err:
            WarningBox.warningDialogBox("Échec lors de la connexion",
                                        "Une erreur s'est produite lors de la "
                                        "connexion au serveur de partage. </p> "
                                        "<p align='center'>" + err.args[0],
                                        WarningBox.Ok)

    # Closing connection
    def close(self):
        self.mc_cnxsftp.close()

    # Create private directory for the new user (using is login username)
    def createFolder(self, s_HostPath):
        self.mc_cnxsftp.makedirs(s_HostPath)

    # Get a file from a specific host path to an local path
    def getFile(self, s_HostPath, s_LocalPath):
        self.mc_cnxsftp.get(s_HostPath, s_LocalPath, None, True)

    # Send a file frome a specific local path to an host path
    def sendFile(self, s_HostPath, s_LocalPath):
        self.mc_cnxsftp.put(s_LocalPath, s_HostPath, None, True)

    def delFile(self, s_HostPath):
        self.mc_cnxsftp.remove(s_HostPath)
