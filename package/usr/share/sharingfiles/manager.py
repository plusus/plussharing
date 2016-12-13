#!/usr/bin/python3

"""manager.py: Class that will allow the user to delete one or many file shared in the public environnement of PlusSync"""

__author__      = "Sam Charland"
__copyright__   = "Copyright 2016, PLUS-US"

#Imports
import getpass

from db_mysql import DbMysql
from file_ftp import Fileftp
from warning_box import QuickWarningBox

class ManagerSharingSystem():
    #CONTANT
    CI_ADMIN = 3
    CI_VALIDATOR = 2
    CI_ENDUSER = 1


    mx_db = DbMysql()
    mx_ftp = Fileftp()

    ms_UserName = ''
    mi_idUser = 0
    mi_UserLevel = 0

    def __init__(self):
        # Get needed information from the linux account system
        self.ms_UserName = getpass.getuser()

        #Open connection
        self.mx_db.open()
        self.mx_ftp.open()

        #Check the user id and is autorisation level
        s_Request = "Select iduser, type_user from user where username='%s'" % self.ms_UserName
        a_Respond = self.mx_db.executeReturnAll(s_Request)

        #if the answer got at least 2 item
        if not(a_Respond is None):
            #save those informations
            self.mi_idUser = a_Respond[0][0]
            self.mi_UserLevel = a_Respond[0][1]
        #is not
        else:
            #Popup a warning message to say that is not register in the database
            QuickWarningBox().warningDialogBox('Avertissement : Enregistrement manquant',
                                             'Votre nom d\'utilisateur ne semble pas enregistré. <br>' \
                                             'Veuilliez contacter votre administrateur pour vous enregistrer dans le système.',
                                             'ok')
        #Check is autorisation level and if it's not at least a validator or an Admin, it will do an popup
        # to warn that is doesn't have the acces
        if self.mi_UserLevel < self.CI_VALIDATOR:
            QuickWarningBox().warningDialogBox('Avertissement : Activité non autorisé',
                                             'Attention : Vous n\'êtes pas autorisé par l\'administration à effectuer des changements. <br>' \
                                             'Veuilliez contacter votre administrateur pour plus de renseignement.',
                                             'ok')

    def __del__(self):
        self.mx_db.close()
        self.mx_ftp.close()

    def deleteSharedFile(self, pi_type, ps_name):
        if (self.mi_UserLevel != self.CI_ADMIN): #Have an admin
            return

        s_Request = {
            0:"SELECT idfile FROM public_file_data WHERE name='%s'" % ps_name,
            1:"SELECT idfile FROM private_file_data WHERE folder='%s' AND name='%s'" % ps_name.split('/')
            }[pi_type]
        i_idfile = self.mx_db.executeReturnOne(s_Request)

        i_Error = 0

        if not(i_idfile is None):
            if pi_type == 0:
                s_Request = "DELETE FROM public_file_data WHERE idfile=%s" % i_idfile
                try:
                    self.mx_db.executeNoReturn(s_Request)
                except:
                    i_Error = 1
            elif pi_type == 1:
                s_Request = "DELETE FROM access WHERE file_data_idfile=%s" % i_idfile
                s_Request2 = "DELETE FROM private_file_data WHERE idfile=%s" % i_idfile
                try:
                    self.mx_db.executeNoReturn(s_Request)
                    self.mx_db.executeNoReturn(s_Request2)
                except:
                    i_Error = 1
        else:
            i_Error = 1

        if i_Error >= 0:
            print("Une erreur s\'est produit lors de la recherche de votre fichier.")
            # QuickWarningBox().warningDialogBox('Avertissement : Erreur de recherche',
            #                                  'Une erreur s\'est produit lors de la recherche de votre fichier.',
            #                                  'ok')
            # return

    def validateSharingFile(self, ps_name):
        if (self.mi_UserLevel >= self.CI_VALIDATOR): #Have an admin
            return

        s_Request = "UPDATE public_file_data SET validatedby=%s WHERE name='%s'" % self.mi_idUser, ps_name
        try:
            self.mx_db.executeNoReturn(s_Request)
        except:
            QuickWarningBox().warningDialogBox('Avertissement : Erreur de recherche',
                                             'Une erreur s\'est produit lors de la validation de votre fichier.',
                                             'ok')


    # i_type : value that represent the type of pulling (0 = Public, 1 = Private)
    def getListFile(self, i_type):
        """
        :type i_type: integer
        """

        s_Request = {
            0: 'SELECT name, CONCAT(\'public/\', name), datemodify FROM public_file_data ',
            1: 'SELECT name, CONCAT(\'private/\', folder, \'/\', name),  folder, datemodify FROM private_file_data pfa ' \
               'LEFT JOIN access a ON a.file_data_idfile = pfa.idfile '
        }[i_type]

        # Execute the request
        o_Result = self.mx_db.executeReturnAll(s_Request)

        return o_Result

MSS = ManagerSharingSystem()
test = MSS.getListFile(0)
test = MSS.getListFile(1)