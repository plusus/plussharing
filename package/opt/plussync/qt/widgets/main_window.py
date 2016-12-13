"""main_window.py: This script is the main working system for the Plus-Sync.
This have all the dynamic interface for better work and to update the view
dynamically."""

from os import popen, path, getuid, walk, stat, makedirs
from pwd import getpwuid
from fnmatch import filter
from pickle import load, dump
from atexit import register
from datetime import datetime

from PySide.QtGui import QMainWindow, QWidget, QItemSelectionModel, QIcon, QHeaderView

from plussync.qt.widgets.search_bar import ClearableLineEdit
from plussync.qt.widgets.type_entries_widget import TypeEntry, TypeEntriesWidget
from plussync.qt.widgets.files_entries_widget import FileEntry, FileEntriesWidget
from plussync.qt.widgets.plus_sync import plus_sync
from plussync.qt.pyside_dynamic import loadUi
from plussync.utils import ui_filepath, resource_filepath
from plussync.qt.widgets.repeated_timer import RepeatedTimer
from plussync.qt.widgets.constant import Status, RGBColors

C_LOCAL_STATUS = "%s/.plussharing/status/" % getpwuid(getuid())[5]


class MainWindow(QMainWindow):

    C_FILENAME_COL = 1

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        """
        :type parent: QWidget
        """
        # Loading of the UI
        QMainWindow.__init__(self, parent)
        loadUi(ui_filepath('manager_window.ui'), self)

        self.setWindowIcon(QIcon(resource_filepath("plussync.svg")))

        # Set decorators for promoting widgets to custom types
        self.typeEntriesTableWidget = TypeEntriesWidget(
            self.typeEntriesTableWidget)
        """:type: QTableWidget | TypeEntriesWidget"""
        self.fileEntriesTableWidget = FileEntriesWidget(
            self.fileEntriesTableWidget)
        """:type: QTableWidget | FileEntriesWidget"""

        # Auto-completion definitions
        self.explicationLabel = self.explicationLabel
        """:type: QLabel"""
        self.mainSplitter = self.mainSplitter
        """:type: QSplitter"""
        self.leftSplitter = self.leftSplitter
        """:type: QVBoxLayout"""
        self.exploreButton = self.exploreButton
        """:type: QPushButton"""
        self.downloadButton = self.downloadButton
        """:type: QPushButton"""
        self.cancelButton = self.cancelButton
        """:type: QPushButton"""
        self.cancelButton.setVisible(False)
        self.horizontalLayout = self.horizontalLayout
        """:type: QHBoxLayout"""

        # Add the filter widget
        self.searchEditLine = ClearableLineEdit(self._updateFilter)
        self.horizontalLayout.addWidget(self.searchEditLine)

        # Adjust the mode of resize of the view
        self.typeEntriesTableWidget.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.typeEntriesTableWidget.horizontalHeader().setResizeMode(1, QHeaderView.ResizeToContents)

        self.fileEntriesTableWidget.horizontalHeader().setResizeMode(0, QHeaderView.ResizeToContents)
        self.fileEntriesTableWidget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.fileEntriesTableWidget.horizontalHeader().setResizeMode(2, QHeaderView.ResizeToContents)

        # Connect signals and events handlers
        self.typeEntriesTableWidget.cellClicked.connect(self.updateFilesView)
        self.fileEntriesTableWidget.cellDoubleClicked.connect(self.onDownloadButton)
        self.exploreButton.clicked.connect(self.onExploreButton)
        self.cancelButton.clicked.connect(self.onCancelButton)
        self.downloadButton.clicked.connect(self.onDownloadButton)

        # Set the layout
        self._layoutSplitter()

        # Load the class and initialise it
        self.plus_fct = plus_sync()

        # Init all Entries
        self.typeEntries = []
        self.publicEntries = []
        self.personnalEntries = []
        self.updateFilesEntries()

        # Setup the timer event generator
        self.updateTimer = RepeatedTimer(300, self.updateFilesEntries)
        self.updateTimer.start()

        # Set the view for the first lookout
        self.typeEntriesTableWidget.setEntries(self.getTypeEntries())
        self.typeEntriesTableWidget.selectRow(0)
        self.updateFilesView(0)

        # Set the End of program event handler
        register(self.exit_handler)
        self.fileEntriesTableWidget.itemSelectionChanged.connect(self.selectedFileEntries)

    # Function that will adjust the ratio of all splitter layout of the view
    def _layoutSplitter(self):
        # Setup all ratio of layer splitter
        self.mainSplitter.setStretchFactor(0, 1)
        self.mainSplitter.setStretchFactor(1, 2)
        self.leftSplitter.setStretchFactor(0, 1)
        # Allow to get the minimum size of the table
        self.leftSplitter.setStretchFactor(1, 70)

    # Call on close of class
    def closeEvent(self, event):
        self.updateTimer.stop()

    # Function that will update the view when the search bar as change
    def _updateFilter(self, filter_text):
        """
        :type filter_text: str
        """
        # Format to compatibility of comparison
        filter_formatted = filter_text.lower()
        # check the current type chosed by selection
        currentRow = self.typeEntriesTableWidget.currentRow()

        first_shown_software = 0
        # Loop for all type available
        for i in range(self.typeEntriesTableWidget.rowCount()):
            # For the type, get the Entry associated
            typeEntries = self.typeEntriesTableWidget.getObjectEntry(i)
            """:type: TypeEntry"""

            if typeEntries:
                # Count the number of file available into the type
                files_count = len(typeEntries.files)
                hidden_count = 0
                # Loop for all files identify
                for j in range(files_count):
                    # get the entry information about the file
                    file = typeEntries.files[j]
                    name = file.name.lower()
                    # If the filename is not the same as the filter than note
                    # that need to be hide
                    hide = name.find(filter_formatted) == -1  # and \

                    if i == currentRow:
                        self.fileEntriesTableWidget.setRowHidden(j, hide)
                    # Add an count about the number of hidden element
                    hidden_count += 1 if hide else 0
                # If not all the file are hidden then
                hide_file = hidden_count == len(typeEntries.files)
                if not first_shown_software and not hide_file:
                    # Show the type
                    first_shown_software = i
                # Set the type row as having element
                self.typeEntriesTableWidget.setRowHidden(i, hide_file)

        if not self.typeEntriesTableWidget.selectedIndexes() and self.typeEntriesTableWidget.rowCount() > 0:
            # Show the first type with the best solution of filter
            self.typeEntriesTableWidget.setCurrentCell(
                first_shown_software, 0, QItemSelectionModel.SelectCurrent)

    # Function that will open Nautilus on the root folder of the current user
    @staticmethod
    def onExploreButton():
        popen("nautilus ~/Documents")

    # Function that  will download all selected files of the selected type of
    # sharing
    def onDownloadButton(self):
        # Stop the refresh timer to make sur no interference of the view to
        # loose the selected elements
        self.updateTimer.stop()
        # Get all Entries about the current type
        currentType = self.typeEntriesTableWidget.currentItem().row()
        typeEntries = self.typeEntriesTableWidget.getObjectEntry(currentType)

        # Iterate through selected elements to get the correspondent entry
        entries = []
        for row in self.fileEntriesTableWidget.selectionModel().selectedRows():
            i = 0
            # noinspection PyBroadException
            try:
                # Loop for into all file entries and compare them to the view
                # (to find the good entry to get is information)
                while typeEntries.files[i].name != \
                        self.fileEntriesTableWidget.item(row.row(), self.C_FILENAME_COL).text():
                    i += 1
            except:
                pass
            # Ensure that the correct element was found
            if typeEntries.files[i].name == self.fileEntriesTableWidget.item(row.row(), self.C_FILENAME_COL).text():
                # Add the found entry host file path into an array of treatment
                entries.append(typeEntries.files[i])

        if len(entries) > 0:
            # Download all file path listed
            self.plus_fct.getFile(entries)

        # Update the view to show load all the new status
        self.updateFilesEntries()
        # Restart the refresh view timer
        self.updateTimer.start()

    # Function that quit the application
    def onCancelButton(self):
        self.updateTimer.stop()
        exit(0)

    # Function that get all the files entries on the server
    def getFilesEntries(self, sharingType):
        # Get a list of file from the server
        fileList = self.plus_fct.getListFile(sharingType)
        entries = []
        # root of file checkup for status manager
        root = '%s/Documents/' % getpwuid(getuid())[5]

        savedFiles = []
        if path.exists(C_LOCAL_STATUS + str(sharingType)):
            f = open(C_LOCAL_STATUS + str(sharingType), 'rb')
            savedFiles = load(f)
            f.close()

        # Loop of all listed file got from the server
        for fileInfo in fileList:
            filepath = 0
            status = 0

            # Finding the entry if it exist in the last binary and the SQL
            # noinspection PyBroadException
            try:
                foundSameEntry = [x for x in savedFiles
                                  if (x.name, x.hostFilePath) == (fileInfo.name, fileInfo.hostFilePath)][0]
                """:type: FileEntry"""
            except:
                foundSameEntry = []

            # Search for all loaded file in the root folder and is subfolder
            # for any file that correspond from the shared files
            # noinspection PyBroadException
            try:
                for roots, dirnames, filenames in walk(root):
                    for filename in filter(filenames, fileInfo.name):
                        filepath = path.join(roots, filename)
                        break
                    if filepath != 0:
                        break
            except:
                filepath = 0

            # If an file path was found
            if filepath != 0:
                # Check the date of file to compare it
                filedate = datetime.fromtimestamp(stat(filepath).st_mtime)

                if filedate < fileInfo.lastUpdate:
                    status = Status.Download_updated_server.value  # STATUS: Outdated local file by server
                    # If is different and have already a status, it will keep it
                    if foundSameEntry:
                        if foundSameEntry.status > Status.Null.value:
                            status = foundSameEntry.status
                elif filedate == fileInfo.lastUpdate:
                    status = Status.Download_same.value  # STATUS: same as on SERVER and LOCAL
                elif filedate > fileInfo.lastUpdate:
                    status = Status.Download_updated_user.value  # STATUS: Updated local file by USER
            else:  # New File
                status = Status.New_file.value  # STATUS: New or update File from server and not downloaded

                if foundSameEntry:
                    if fileInfo.lastUpdate == foundSameEntry.lastUpdate:
                        if foundSameEntry.status < Status.Download_updated_server.value:
                            status = foundSameEntry.status  # Old from server so keep status
                        else:
                            status = Status.Seen_user.value  # STATUS: Acknowledge file
                    elif fileInfo.lastUpdate > foundSameEntry.lastUpdate:
                        status = Status.Update_server.value  # STATUS: Updated file

            # Add the file to the entry list
            entries.append(FileEntry(status, fileInfo.name, fileInfo.hostFilePath, fileInfo.lastUpdate))
        # Sort all entries and return the list
        return sorted(entries)

    # Function that get and set all is files from is type of sharing
    def getTypeEntries(self):
        entries = []
        # List of all wanted available Type of sharing
        for p in [0, 1]:
            s_name = {
                0: 'Publique',
                1: 'Personnel'
            }[p]

            # Get all the file upon the type
            files = self.getFilesEntries(p)
            # Add the entry into an array
            entries.append(TypeEntry(s_name, files))
        # return the array (must not be sorted to have is position hard coded
        return entries

    # Function that update the table of files with the array of entry associated with the type of sharing
    def updateFilesView(self, row):
        if row >= 0:
            if row == 0:
                self.fileEntriesTableWidget.setEntries(self.publicEntries)
            elif row == 1:
                self.fileEntriesTableWidget.setEntries(self.personnalEntries)

    # Function that is updating the entries (of files and Type) and this also update the view
    def updateFilesEntries(self):
        # Get the current selected Type of sharing
        # noinspection PyBroadException
        try:
            selectedTypeRow = self.typeEntriesTableWidget.currentItem().row()
        except:
            selectedTypeRow = 0

        # Set all the global entries of class
        self.typeEntries = self.getTypeEntries()
        self.publicEntries = self.getFilesEntries(0)
        self.personnalEntries = self.getFilesEntries(1)

        # Set the Type table Widget with of new found entries
        self.typeEntriesTableWidget.setEntries(self.typeEntries)
        self.updateFilesView(selectedTypeRow)
        # Double because some time he doesn't select correctly
        self.typeEntriesTableWidget.selectRow(selectedTypeRow)
        self.typeEntriesTableWidget.selectRow(selectedTypeRow)

    # Function that is call on selection change on the file Table. It will adjust the status on the linked file entries
    def selectedFileEntries(self):
        # Get the actual selected type
        # noinspection PyBroadException
        try:
            currentType = self.typeEntriesTableWidget.currentItem().row()
        except:
            currentType = 0

        # Specification of data set to manipulate depending on the type
        data = {
            0: self.publicEntries,
            1: self.personnalEntries
        }

        # Loop in all selected row from the view
        for row in self.fileEntriesTableWidget.selectionModel().selectedRows():
            # noinspection PyBroadException
            try:
                # Search the index of the entry
                indexData = 0
                for x in data[currentType]:
                    if x.name != self.fileEntriesTableWidget.item(row.row(), self.C_FILENAME_COL).text():
                        indexData += 1
                    else:
                        break

                # Check the current status to manipulate of the row
                if data[currentType][indexData].status in [Status.New_file.value, Status.Update_server.value]:
                    # STATUS: user notified
                    data[currentType][indexData].status = Status.Seen_user.value
                    self.fileEntriesTableWidget.item(row.row(), 0).setIcon(QIcon(resource_filepath("viewed.svg")))
                    for column in range(self.fileEntriesTableWidget.columnCount()):
                        self.fileEntriesTableWidget.item(row.row(), column).setBackground(RGBColors.White.value)
                elif data[currentType][indexData].status == Status.Download_updated_server.value:
                    # STATUS: user notified and downloaded
                    data[currentType][indexData].status = Status.Download_seen_user.value
                    self.fileEntriesTableWidget.item(row.row(), 0).setIcon(QIcon(resource_filepath("viewed.svg")))
                    for column in range(self.fileEntriesTableWidget.columnCount()):
                        self.fileEntriesTableWidget.item(row.row(), column).setBackground(RGBColors.White.value)
            except:
                pass

        # Reinsert all modification done into the view
        self.typeEntries[currentType].files = data[currentType]
        self.typeEntries[currentType].news = self.typeEntries[currentType].calcNews()
        self.typeEntriesTableWidget.setEntries(self.typeEntries)
        self.typeEntriesTableWidget.selectRow(currentType)

        # Save all modification into binary files
        self.saveFileListing()

    # Function that will stop the time and save progress on end of program
    def exit_handler(self):
        self.updateTimer.stop()
        self.saveFileListing()

    # Function that is saving all entries into binary file
    def saveFileListing(self):
        if not path.exists(C_LOCAL_STATUS):
            makedirs(C_LOCAL_STATUS)

        # Data array to regroup all entries
        data = {
            0: self.publicEntries,
            1: self.personnalEntries
        }

        # Loop for each type of sharing, it will make or update an binary file
        # to encode the current entry associated
        for i in range(0, self.typeEntriesTableWidget.rowCount()):
            f = open(C_LOCAL_STATUS + str(i), 'wb')
            dump(data[i], f)
            f.close()
