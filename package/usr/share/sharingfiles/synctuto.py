#!/usr/bin/python3

"""synctuto.py: Script that pull all shared tutoriel from the server associated with the installed local cache"""

# IMPORTS
from os import path, makedirs, mkdir, getuid
from pwd import getpwuid
from apt import Cache
from db_mysql import DbMysql
from file_ftp import Fileftp

__author__ = "Sam Charland"
__copyright__ = "Copyright 2016, PLUS-US"


# CONSTANTS

# GLOBAL VAR
# Local path to the inbox of all tutoriel into the home directory of the current user
C_LOCAL_TUTO = "%s/.local/share/libtuto/" % getpwuid(getuid())[5]

C_HOST_TUTO = "tutorial/"

# INITIALIZATION

with DbMysql() as db, Fileftp() as ftp:

    if not path.exists(C_LOCAL_TUTO):
        makedirs(C_LOCAL_TUTO)

    # GET ALL SOFTWARE AND THERE TUTORIAL
    cache = Cache()

    # SQL query to get all software and there version handle by our community
    s_query = 'Select sv.idversion,st.name,sv.number from software_tuto st join soft_version sv on st.idsoft=sv.idsoft'
    l_result = db.executeReturnAll(s_query)

    for pkgQuery in l_result:
        i_id, s_tutosoft, s_tutovers = pkgQuery

        found = False
        if s_tutosoft in cache:
            if cache[s_tutosoft].is_installed:
                if cache[s_tutosoft].installed.source_version == s_tutovers:
                    found = True

        if found:
            # Query to get the file name and path of the tutorial
            s_query = 'SELECT file_name from tutoriel_file_data where idversion=' + str(i_id)
            a_res = db.executeReturnAll(s_query)
            # Loop into all tutorial associated with the software
            for filename in a_res:
                # Determine the path into the local folder
                s_localpathdir = C_LOCAL_TUTO + s_tutosoft + '/'
                s_localpath = s_localpathdir + filename[0]
                # Make the path of the host folder
                s_hostpath = C_HOST_TUTO + s_tutosoft + '/' + s_tutovers + '/' + filename[0]
                # Create the local folder if it's doesn't exist
                if not path.exists(s_localpathdir):
                    mkdir(s_localpathdir)

                try:
                    # FTP request of file
                    ftp.getFile(s_hostpath, s_localpath)
                except Exception as inst:
                    print("Host path: " + s_hostpath + "\nLocal path: " +
                          s_localpath + "\nType: " + str(type(inst)) +
                          "\nArgument: " + str(inst.args) + "\nAll Arg printed:" +
                          str(inst))

    # SCRIPT ENDING
