#PUT THIS FILE UNDER /HOMEDIR/.LOCAL/SHARE/NAUTILUS-PYTHON/FILE.PY
#The extension nautilus-python will fetch all the scripts under that folder on startup.
from gi.repository.GObject import GObject
from gi.repository.Nautilus import MenuItem
from gi.repository.Nautilus import MenuProvider
import os
import urllib


def format_file_name(fileString):
    """
    Returns the string of the fileString without the file:://, file::\\, file:/ or file::\\
    :param fileString: the string of the filename or filepath to be formatted
    :return: the string with the right format applied to it. Ready to be shared
    """
    #For future reference, it seems that the extension uses different formatting of the "file:://" depending on where it is launched. So we can never be too safe.
    return str(fileString.replace('file::\\', '').replace('file://', '').replace('file:/', '').replace('file:\\', ''))

def get_all_names(files, pathOrName):
    """
    Returns a string of the files paths in " " and each separated by a space
    :param files: list of nautilus.fileinfos
    :return: the list of filePaths found in the list of nautilus.fileinfos
    """
    if (pathOrName == 'Paths'):
        filesPathsString = ""
        for file in files:
            if file != None and not (file.is_directory()):
                filesPathsString += str(format_file_name(urllib.unquote(file.get_uri()))) + ' '

        return str(filesPathsString)

    elif (pathOrName == 'Names'):
        filesNamesString = ""
        for file in files:
            if file != None and not (file.is_directory()):
                filesNamesString += str(format_file_name(file.get_name())) + ' '

        return str(filesNamesString)


class ColumnExtension(GObject, MenuProvider):
    def __init__(self):
        pass


    def menu_share(self, menu, files, sharingType):
        """
        Will call the Python3 sharing script with the right parameters
        :param menu: menuprovider object coming from nautiluspython
        :param files: the list of filesinfo selected in nautilus
        :param sharingType: the specified sharing type between Sync, Personnal, Public
        """
        cmd = ""

        if sharingType == 'Personnal' or sharingType == 'Public':
            filesPaths = get_all_names(files, "Paths")
            filesNames = get_all_names(files, "Names")
            if filesPaths != "":
                cmd = "python3 /usr/share/sharingfiles/src %s %s %s"%(sharingType,
                                                                           filesPaths,
                                                                           filesNames)
        elif sharingType == 'Sync':
            cmd = "python3 /opt/plussync"

        os.system(cmd)


    def get_file_items(self, window, files):
        """
        Overriding function of NautilusPython
        :param window: The Nautilus window instance
        :param files: the list of fileinfos selected in nautilus file manager
        :return: Return the list of menu options that we created
        """
        if len(files) == 1 and files[0].is_directory():
            return
        if len(files) < 1:
            return

        personnalShareItem = MenuItem(
            name="SimpleMenuExtension::PrivateShare",
            label="Partage Personnel",
            tip="Partage Personnel",
            icon="/usr/share/sharingfiles/icons/personnal.png"
        )
        personnalShareItem.connect('activate', self.menu_share, files, 'Personnal')

        publicShareItem = MenuItem(
            name="SimpleMenuExtension::PublicShare",
            label="Partage Publique",
            tip="Partage Publique",
            icon="/usr/share/sharingfiles/icons/public.png"
        )
        publicShareItem.connect('activate', self.menu_share, files, 'Public')

        # syncShareItem = MenuItem(
        #     name="SimpleMenuExtension::Synchronization",
        #     label="Synchronisation des Fichiers",
        #     tip="Synchronisation des Fichiers",
        #     icon="/usr/share/sharingfiles/icons/sync.png"
        # )
        # syncShareItem.connect('activate', self.menu_share, files, 'Sync')

        return personnalShareItem, publicShareItem
