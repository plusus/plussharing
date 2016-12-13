from plussync.controller.concretecontroller import ConcreteController
from plussync.qt.view_qt import ViewQt


controller = ConcreteController()
controller.setView(ViewQt(controller))
controller.startApp()
