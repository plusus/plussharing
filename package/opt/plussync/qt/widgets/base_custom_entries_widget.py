from PySide.QtGui import QFont, QTableWidgetItem

from plussync.proxy import Proxy


class BaseCustomEntriesWidget(Proxy):
    def __init__(self, delegate):
        """
        :type delegate: QTableWidget
        """
        Proxy.__init__(self, delegate)

        self._font = QFont()
        self._object_entries = {}

    def createCustomEntry(self, model):
        """
        :rtype: QTableWidgetItem
        """
        raise NotImplementedError()

    def getCurrentObjectEntry(self):
        return self.getObjectEntry(self.currentRow())

    def getObjectEntry(self, row):
        return self._object_entries.get(row)

    def getObjectEntries(self):
        return {self.getObjectEntry(row) for row in range(self.count())}

    def getSelectedObjectsEntries(self):
        return {self.getObjectEntry(row) for row in range(self.selectedItems().count())}

    def setEntries(self, entries):
        """
        :param entries: Iterable of custom type entry
        """
        self.clearContents()
        self.setRowCount(len(entries))
        for i, entry in zip(range(len(entries)), entries):
            items = self.createCustomEntry(entry)
            self.setColumnCount(len(items))
            for j, item in zip(range(len(items)), items):
                item.setFont(self._font)
                item.setTextAlignment(1)
                if j == (len(items)-1):
                    item.setTextAlignment(2)

                self.setItem(i, j, item)
            self._object_entries[i] = entry
