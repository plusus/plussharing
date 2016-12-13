
from os import getuid
from pwd import getpwuid
from PySide.QtGui import QTableWidget, QTableWidgetItem

from plussync.qt.widgets.base_custom_entries_widget import BaseCustomEntriesWidget

C_LOCAL_STATUS = "%s/.plussharing/status/" % getpwuid(getuid())[5]


class TypeEntry:
    def __init__(self, name, files):
        """
        :type: str
        :type: List[Files]
        """
        self.name = name
        self.files = files
        self.news = self.calcNews()

    def calcNews(self):
        news = 0
        for x in self.files:
            if x.status in [1, 2, 4]:
                news += 1
        return news

    def __lt__(self, other):
        return self.name < other.name


class TypeEntriesWidget(BaseCustomEntriesWidget):
    def __init__(self, delegate):
        """
        :type delegate: QTableWidget
        """
        super().__init__(delegate)
        self._font.setPointSize(14)

    def createCustomEntry(self, model):
        """
        :type model: TypeEntry
        :rtype: QTableWidgetItem
        """
        return [QTableWidgetItem(model.name), QTableWidgetItem(str(model.news))]
