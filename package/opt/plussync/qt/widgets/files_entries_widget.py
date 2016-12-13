from PySide.QtGui import QIcon, QTableWidget, QTableWidgetItem

from plussync.utils import resource_filepath

from plussync.qt.widgets.base_custom_entries_widget import BaseCustomEntriesWidget
from plussync.qt.widgets.constant import Status, RGBColors


class FileEntry:
    def __init__(self, status, name, hostFilePath, lastUpdate):
        """
        :type status: int
        :type name: str
        :type hostFilePath: str
        :type lastUpdate: datetime
        """
        self.status = status
        self.name = name
        self.hostFilePath = hostFilePath
        self.lastUpdate = lastUpdate

    def __lt__(self, other):
        return self.name < other.name


class FileEntriesWidget(BaseCustomEntriesWidget):
    def __init__(self, delegate):
        """
        :type delegate: QTableWidget
        """
        super().__init__(delegate)
        self._font.setPointSize(14)

    def createCustomEntry(self, model):
        """
        :type model: FileEntry
        :rtype: QTableWidgetItem
        """
        nameItem = QTableWidgetItem(model.name)
        dateItem = QTableWidgetItem(str(model.lastUpdate.date()))
        iconItem = QTableWidgetItem()

        if model.status in [Status.Seen_user.value, Status.Download_seen_user.value]:
            iconItem.setIcon(QIcon(resource_filepath("viewed.svg")))
        elif model.status in [Status.Update_server.value, Status.Download_updated_server.value]:
            iconItem.setIcon(QIcon(resource_filepath("updated.svg")))
        elif model.status == Status.Download_same.value:
            iconItem.setIcon(QIcon(resource_filepath("downloaded.svg")))

        if model.status == 1:
            nameItem.setBackground(RGBColors.Emerald.value)
            dateItem.setBackground(RGBColors.Emerald.value)
            iconItem.setBackground(RGBColors.Emerald.value)

        return [iconItem, nameItem, dateItem]
