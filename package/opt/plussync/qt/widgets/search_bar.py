from PySide.QtGui import QToolButton, QIcon, QLineEdit, QStyle

from plussync.utils import resource_filepath


class ClearableLineEdit(QLineEdit):

    HEIGHT = 32

    def __init__(self, filter_updater, parent=None):
        """
        :type filter_updater: (str) -> None
        :type parent: QWidget
        """
        super().__init__(parent)

        self._filter_updater = lambda: filter_updater(self.text())

        self.setFixedHeight(self.HEIGHT)
        self.setMaxLength(48)
        self.setMaximumWidth(200)

        self._tool_button = QToolButton(self)
        self._tool_button.setIcon(QIcon(resource_filepath("clear.png")))
        self._tool_button.setStyleSheet(
            "QToolButton {"
            "   border: none;"
            "   padding: 0px;"
            "}")

        frame_width = self._getFrameWidth()
        icon_side = self.HEIGHT - 2 * frame_width
        self._tool_button.setFixedSize(icon_side, icon_side)
        self._tool_button.clicked.connect(self.onClearButton)
        self._tool_button.hide()
        self.textChanged.connect(self.updateFilter)
        stylesheet = \
            "QLineEdit {{" \
            "   padding-right: {}px;" \
            "   background-color: #FFFFFF;" \
            "}}".format(self._tool_button.sizeHint().width() + frame_width + 1)
        self.setStyleSheet(stylesheet)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._updateSize()

    def _updateSize(self):
        size = self._tool_button.size()
        """:type: QSize"""
        frame_width = self._getFrameWidth()
        rect = self.rect()
        """:type: QRect"""
        x = rect.right() - frame_width - size.width()
        y = (rect.bottom() + 1 - size.height()) / 2
        self._tool_button.move(x, y)

    def _getFrameWidth(self):
        return self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)

    def onClearButton(self):
        self.clear()

    def updateFilter(self):
        self._tool_button.setVisible(len(self.text()) > 0)
        self._filter_updater()
