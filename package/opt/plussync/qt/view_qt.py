import sys
from os.path import join

from PySide.QtCore import QTranslator
from PySide.QtGui import QApplication

from plussync.definitions.mvp import View, Controller
from plussync.qt.widgets.main_window import MainWindow
from plussync.utils import project_root


class ViewQt(View):
    """
    Main view of the application
    """

    QT_APPLICATION = QApplication(["Plus Sync"], QApplication.GuiClient)
    # TRANSLATOR = QTranslator()
    # i18n = join(project_root(), "i18n", "fr_CA")
    # TRANSLATOR.load(i18n)
    # QT_APPLICATION.installTranslator(TRANSLATOR)

    def __init__(self, controller):
        """
        :type controller: Controller
        """
        self._controller = controller
        self._main_window = MainWindow()

    def launch(self):
        """
        Launch the view (blocking call)
        """
        self._main_window.show()
        sys.exit(ViewQt.QT_APPLICATION.exec_())
