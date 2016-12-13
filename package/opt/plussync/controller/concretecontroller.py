from os.path import join

from plussync.definitions.mvp import Controller, View
from plussync.utils import project_root


class ConcreteController(Controller):
    def __init__(self):
        self._view = None
        """:type: View"""

    def setView(self, view):
        """
        :type view: View
        """
        self._view = view

    def startApp(self):
        assert self._view
        self._view.launch()
