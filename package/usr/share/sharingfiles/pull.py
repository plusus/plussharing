#!/usr/bin/python3

"""pull.py: Script that pull all file into an Inbox of the user to allow him to get all the needed file shared to him by a public alogrithme or an private sharing algorithme into a dedicated server."""

__author__      = "Sam Charland"
__copyright__   = "Copyright 2016, PLUS-US"

#Imports
import getpass
import os
import pwd

import db_mysql
import file_ftp

class PullSystem():
    #CONSTANT VAR

    #Path where the pull system put all files received
    C_LOCAL_PUB = "%s/.plussharing/public/"
    C_LOCAL_PRI = "%s/.plussharing/private/"

    C_HOST_PUB = 'public/%s'
    C_HOST_PRI = 'private/%s'


    #GLOBAL VAR

    #Add module for connexion management
    x_SQL = db_mysql
    x_FTP = file_ftp

    #Global var linked to the current user
    mi_IdUser = 0
    msa_Fullname = ''
    ms_Username = ''

    #INITIALIZATION

    def init(self):
        #Get needed information from the linux account system
        self.ms_Username = getpass.getuser()
        self.ms_UserHome = pwd.getpwuid(os.getuid())[5]
        self.msa_Fullname = (pwd.getpwuid(os.getuid())[4]).split(' ')

        #If it has no last name
        if (len(self.msa_Fullname) <= 1):
            #it will add PlusUS as lastname
            self.msa_Fullname = (self.msa_Fullname[0].split(',', 1)[0] + ' PlusUS').split(' ')

        #openning connection to the serveur
        self.x_SQL.open()
        self.x_FTP.open()

    #MAKE NEW USER

    def checkUser(self):
        #SQL request to informe the script if the user exist
        s_RequestID = "SELECT iduser FROM user WHERE username = '%s' " % self.ms_Username

        o_Result = None
        try:
            #try to send the request
            o_Result = self.x_SQL.executeReturnOne(s_RequestID)
        except:
            pass #if it do not respond, we do nothing

        #Check if we reseive an answer on our request, if none than it doesn't exist
        if o_Result is None:
            #Will insert the user in the table wit all his needed information
            s_Request = ("INSERT INTO user (first_name, last_name, username, type_user) "
                           "VALUES ('%s', '%s', '%s', %s)")
            #Insert dynamic information into the query
            a_DataUser = (self.msa_Fullname[0], self.msa_Fullname[1], self.ms_Username, 1)

            #Execute the SQL request ans inserting is data
            self.x_SQL.executeNoReturn(s_Request % a_DataUser)

            #Create his folder in the FTP
            self.x_FTP.createFolder( self.C_HOST_PRI % self.ms_Username + '/')

            #Ask the the SQL what is his ID user
            o_Result = self.x_SQL.executeReturnOne(s_RequestID)

        #Insert his found number into a global var
        self.mi_IdUser = o_Result

    #ALL PULL REQUEST

    #PULL FOR PUBLIC

    def getPublic(self):
        #Get the path for the file inbox
        s_localPath = self.C_LOCAL_PUB % self.ms_UserHome

        #If path do not exist, it create it
        if not os.path.exists(s_localPath):
            os.makedirs(s_localPath)

        #SQL request toget a list of validated file in the public registry
        s_Request = "SELECT name FROM public_file_data WHERE validatedby!=0 "

        #Execute the request
        o_Result = self.x_SQL.executeReturnAll(s_Request)

        #Loop in the list of file received
        for s_Result in o_Result:
            #Path into the ftp server to get the source file
            s_target = self.C_HOST_PUB % (s_Result[0])
            #Path into the local system for destination inbox and with the same name
            s_local = (s_localPath + '%s') % (s_Result[0])

            #Do the Download
            self.x_FTP.getFile(s_target,s_local)

    #PULL FOR PRIVATE

    def getPrivate(self):
        #Get the local path for the destination private folder
        s_localPath = self.C_LOCAL_PRI % self.ms_UserHome

        #if folder doesn't exist, it make it
        if not os.path.exists(s_localPath):
            os.makedirs(s_localPath)

        #SQL request to get all private shared linked to is user as receiver
        s_Request = "SELECT CONCAT(folder,'/',name) FROM private_file_data pfa LEFT " \
                   "JOIN access a ON a.file_data_idfile = pfa.idfile " \
                   "WHERE (a.user_iduser = %s)"


        # Execute SQL request to get a liste of item
        o_Result = self.x_SQL.executeReturnAll(s_Request % self.mi_IdUser)

        #Loop in all the result list
        for s_Result in o_Result:
            #Path into the ftp server to get the source file
            s_target = self.C_HOST_PRI % (s_Result[0])
            # Path into the local system for destination inbox and with the same name
            s_local = (s_localPath + '%s') % (s_Result[0].split('/', 1)[1])

            # Do the Download
            self.x_FTP.getFile(s_target, s_local)

    #CLOSING AND ENDING
    def end(self):
        #Fermeture des connexions
        self.x_SQL.close()
        self.x_FTP.close()


#MAIN
ps_test = PullSystem()

ps_test.init()
ps_test.checkUser()
ps_test.getPublic()
ps_test.getPrivate()
ps_test.end()