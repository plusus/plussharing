"""db_mysql.py: MySQL module for request handler... no error handler put except
on the opening of connection."""

# IMPORT
import mysql.connector
from configparser import ConfigParser
from plussync.qt.widgets.constant import WarningBox

__author__ = "Sam Charland"
__copyright__ = "Copyright 2016, PLUS-US"


class DbMysql:

    # FUNCTIONS

    def __init__(self):
        # Global variable for SQL
        self.mc_cursor = None
        self.mc_cnxsql = None

        # Load the configuration parser
        config = ConfigParser()
        # read the file configuration
        config.read('/etc/plussharing.conf')

        confSet = ''
        if 'DATABASE' in config:
            confSet = 'DATABASE'
        elif 'DEFAULT' in config:
            confSet = 'DEFAULT'

        # Load the configurations
        if len(confSet) > 0:
            self.C_USER = config[confSet]['UserLogin']
            self.C_PASS = config[confSet]['PassPhrase']
            self.C_HOST = config[confSet]['HostAddress']

            # MySQL configuration needed as pointer
            self.SQL_Config = {
                'user': self.C_USER,
                'password': self.C_PASS,
                'host': self.C_HOST,
                'database': 'db_sharing'
            }

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        self.open()
        return self

    #Connection Opening
    def open(self):
        try:
            # Open a connection with the db with our needed configuration
            self.mc_cnxsql = mysql.connector.connect(**self.SQL_Config)
            # Activation of the cursor
            self.mc_cursor = self.mc_cnxsql.cursor()
        except mysql.connector.errors.InterfaceError as err:
            WarningBox.warningDialogBox("Échec lors de la connexion",
                                        "Une erreur s'est produite lors de la "
                                        "connexion à la Base de Données. </p> "
                                        "<p align='center'>" + str(err.msg),
                                        WarningBox.Ok)

    # Connection ending
    def close(self):
        self.mc_cursor.close()
        self.mc_cnxsql.close()

    # Execute a SQL query and dont return any information, it will also force
    # a commit at the server side to make sur that the query is complited.
    # Excellent for Insert, Update, etc.
    def executeNoReturn(self, s_Query):
        self.mc_cursor.execute(s_Query)
        self.commit()

    # Execute an SQL query and will return the first object received
    # Excellent for Select (and one element waited or at least the first needed)
    def executeReturnOne(self, s_Query):
        self.mc_cursor.execute(s_Query)
        return self.mc_cursor.fetchone()[0]

    # Execute a SQL query et return a liste of item (can be NxMxO), not tested
    # with higher dimension
    def executeReturnAll(self, s_Query):
        self.mc_cursor.execute(s_Query)
        a_Respond = self.mc_cursor.fetchall()
        return a_Respond

    # Force an commit on the server to make sure that all is executed
    # Use it if you do Insert or update
    def commit(self):
        self.mc_cnxsql.commit()
