import sys, getpass, inspect, os, pwd, mysql, time, db_mysql, file_ftp, ScriptShare

class SharingLogic:

    def __init__(self, inScriptShare):
        self.username = getpass.getuser()
        self.idUser = '0'
        self.mx_sql = db_mysql.DbMysql()
        self.mx_ftp = file_ftp.Fileftp()
        self.scriptShareObject = inScriptShare
        self.init_server()

    def connect_server(self):
        self.mx_sql.open()
        self.mx_ftp.open()

    def close_server(self):
        self.mx_sql.close()
        self.mx_ftp.close()

    def init_server(self):
        self.connect_server()

        # Will load all the infos linked to the username
        ms_Username = self.username
        ms_UserHome = pwd.getpwuid(os.getuid())[5]
        msa_Fullname = (pwd.getpwuid(os.getuid())[4]).split(' ')

        # if there is no last name
        if len(msa_Fullname) <= 1:
            msa_Fullname = (msa_Fullname[0].split(',', 1)[0] + ' PlusUS').split(' ')

        ##################################NEW USER#################################
        # Validation query if the username is in the DB
        sRequest = "SELECT iduser FROM user WHERE username = '%s'"

        qResult = None
        try:
            # Execute Query
            qResult = self.mx_sql.executeReturnOne(sRequest % (ms_Username,))
        except:
            pass

        # Gotta insert if the user doesn't exist
        if qResult is None:
            sRequest = ("INSERT INTO user (first_name, last_name, username, type_user) "
                        "VALUES ('%s', '%s', '%s', %s)")

            data_user = (msa_Fullname[0], msa_Fullname[1], ms_Username, 1)

            # Execute Query
            self.mx_sql.executeNoReturn(sRequest % data_user)

            # Create private directory for the new user (using is login username)
            self.mx_ftp.createFolder('private/%s/' % ms_Username)


        # fetch the userid
        sRequest = "SELECT iduser FROM user WHERE username = '%s'"

        # Execute Query
        self.idUser = str(self.mx_sql.executeReturnOne(sRequest % ms_Username))
        self.close_server()

    #################################PersonnalShare#####################################
    # Function doing the sharing for the personnal share.
    def personnal_share(self, receiverUsername, filesNamesToShare):
        #There can be multiple files
        filesPathsNames = self.scriptShareObject.get_files_paths_from_names(filesNamesToShare)
        filesNames = filesNamesToShare

        fileIndex = 0
        for filePathName in filesPathsNames:
            if (filePathName != '' and filePathName != None):
                fileName = filesNames[fileIndex]
                fileIndex = fileIndex + 1

                #Format it and check if the Username is already on the file to share.
                if fileName.find(self.username) == -1:
                    fileName = self.username + '_' + fileName

                try:
                    #Fetch the Receiver's ID, we already have the username but we need the ID to give him access to the file.
                    fileSelectReceiverIDQuery = 'SELECT idUser FROM user u ' \
                                                + 'left join email e on e.user_iduser = u.iduser' \
                                                + ' WHERE u.username = ' \
                                                + '\'' + receiverUsername + '\'' \
                                                + ' OR e.email = ' \
                                                + '\'' + receiverUsername + '\''

                    # Execute Query
                    idReceiver = str(self.mx_sql.executeReturnOne(fileSelectReceiverIDQuery))

                    if receiverUsername.find("@") != -1 and idReceiver != None:
                        selectUsername = 'SELECT username FROM user ' \
                                         'WHERE idUser = \'' + idReceiver + '\''
                        receiverUsername = str(self.mx_sql.executeReturnOne(selectUsername))

                    #The ftp might throw an error if it cannot find/add the file. - the insertions will be skipped thanks to the try catch
                    self.mx_ftp.sendFile('private/' + receiverUsername + '/' + fileName, filePathName)

                    #Try to insert the file connection between both users in the DB.
                    fileInsertPrivateQuery = "INSERT INTO private_file_data (folder, name, owner) " \
                                             + "VALUES (" \
                                             + '\'' + receiverUsername + '\', ' \
                                             + '\'' + fileName + '\', ' \
                                             + self.idUser + ')'

                    # Execute Query
                    try:
                        self.mx_sql.executeNoReturn(fileInsertPrivateQuery)
                        #if the file already exists
                    except mysql.connector.errors.IntegrityError:
                        fileInsertPrivateQuery = "UPDATE private_file_data SET datemodify=CURRENT_TIMESTAMP " \
                                                 "WHERE owner=" + self.idUser \
                                                 + " AND name=\'" + fileName \
                                                 + "\' AND folder=\'" + receiverUsername + "\'"
                        self.mx_sql.executeNoReturn(fileInsertPrivateQuery)
                        print("UPDATED private_file_data instead of INSERTED : " + filePathName + " " + receiverUsername)
                        pass

                    #Verify if the insert has worked and fetches the ID of the new file added
                    fileSelectQuery = 'SELECT idFile FROM private_file_data' \
                                      " WHERE owner=" + self.idUser +\
                                      " AND name=\'" + fileName +\
                                      "\' AND folder=\'" + receiverUsername + "\'"
                    # Execute Query
                    idFile = str(self.mx_sql.executeReturnOne(fileSelectQuery))

                    if (idFile != None) or (idReceiver != None):
                        try:
                            #Give the user the access to the private shared file
                            fileInsertAccessQuery = "INSERT INTO access (file_data_idFile, user_idUser) " \
                                                    + "VALUES (" \
                                                    + str(idFile) + ', ' \
                                                    + str(idReceiver) + ')'
                            # Execute Query
                            self.mx_sql.executeNoReturn(fileInsertAccessQuery)
                        except:
                            fileInsertPrivateQuery = "UPDATE access SET date_download=CURRENT_TIMESTAMP " \
                                                     "WHERE file_data_idFile=" + idFile \
                                                     + " AND user_idUser=" + idReceiver
                            self.mx_sql.executeNoReturn(fileInsertPrivateQuery)
                            print("UPDATED access instead of INSERTED : " + filePathName + " " + receiverUsername)
                            pass

                    time.sleep(0.1) #Considering we can push multiple files to multiple users, we might want to slow down the whole thing for the server to be able to process everything.
                except:
                    print("The push was cancelled due to an error that occured during the process for file : " + filePathName + " " + receiverUsername)
                    print(sys.argv[0] + ' ' + sys.argv[1] + ' ' + sys.argv[2] + ' ' + sys.argv[3])

    # Function doing the sharing for the public share.RepoPersonnalShare
    def public_share(self):
        self.connect_server()

        # There can be multiple files
        filesPathsNames = self.scriptShareObject.get_files_list('Paths')
        filesNames = self.scriptShareObject.get_files_list('Names')

        fileIndex = 0
        for filePathName in filesPathsNames:
            fileName = filesNames[fileIndex]
            fileIndex = fileIndex + 1

            # Format it and check if the Username is already on the file to share.
            if fileName.find(self.username) == -1:
                fileName = self.username + '_' + fileName  # The Username to right on file might become the receiver's username.

            #try:
                self.mx_ftp.sendFile('public/' + fileName, filePathName)

                #Initial insertion into the table managing all the public files shared
                fileQuery = "INSERT INTO public_file_data (name, owner) " \
                            + "VALUES (" \
                            + '\'' + fileName + '\', ' \
                            + self.idUser + ')'

                # Execute Query
                try:
                    self.mx_sql.executeNoReturn(fileQuery)

                #if already exist then update it
                except mysql.connector.errors.IntegrityError:
                    fileQuery = "UPDATE public_file_data SET validatedby=0, datemodify=CURRENT_TIMESTAMP " \
                                "WHERE owner=" + self.idUser + " and name=\'" + fileName + "\' "
                    self.mx_sql.executeNoReturn(fileQuery)
                    pass

                time.sleep(0.1)
            #except:
            #    print("The push was cancelled due to an error that occured during the process for file : " + filePathName)

        self.close_server()
        sys.exit()

    def deny_share(self):
        self.close_server()
        sys.exit()

    #Return a list of string representing every users in the system
    def get_colleagues_list(self):
        self.connect_server()
        #Query to fetch the username and the email of every users in the system
        colleaguesQuery= "SELECT username FROM user " \
               " WHERE NOT(iduser = " + self.idUser + ")" \
               " UNION " \
               " SELECT email FROM email " \
               " WHERE NOT(user_iduser = " + self.idUser + ")"

        list = self.mx_sql.executeReturnAll(colleaguesQuery)

        #Fetch the result as strings(list of string is best)
        #list = ["Admin", "user"]# <---- result of query in here
        row = [item[0] for item in list]
        self.close_server()
        return row
