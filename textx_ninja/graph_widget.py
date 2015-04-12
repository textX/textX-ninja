# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGraphicsView
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QGraphicsPixmapItem
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

PRJ_PATH = os.path.abspath(os.path.dirname(__file__)).decode('utf-8')


class TextXGraphWidget(QWidget):
    """
    Widget for graph representation of textX grammar
    """

    def __init__(self):
        QWidget.__init__(self)
        self._main_container = main_container.MainContainer()
        self._explorer_container = explorer_container.ExplorerContainer()

        #Graph widget
        self._graph = GraphicsView()

        # Graph scene
        self.scene = GraphicsScene(self._graph)
        self._graph.setScene(self.scene)
        self._graph.setDragMode(QGraphicsView.ScrollHandDrag)
        self._graph.setRenderHints(QPainter.Antialiasing)
        #self._graph.fitInView()

        #Main Layout
        main_hbox = QHBoxLayout(self)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)

        #Graph Layout
        vboxGph = QVBoxLayout()
        vboxGph.addWidget(self._graph)

        main_hbox.addLayout(vboxGph)


class GraphicsView(QGraphicsView):

    def __init__(self):
        super(GraphicsView, self).__init__()

    def wheelEvent(self, event):
        # zoom when control key is pressed otherwise move scrollbars
        if event.modifiers() == Qt.ControlModifier:
            # zooming with mouse as center
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            scaleFactor = 1.15

            steps = event.delta()

            # if zooming out update scale factor
            if(steps < 0):
                scaleFactor = 1.0 / scaleFactor

            self.scale(scaleFactor, scaleFactor)
        else:
            super(QGraphicsView, self).wheelEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        On doble click event on graph make that position center of graph
        """
        # get coordinates for centering from position of event
        mousePoint = self.mapToScene(event.pos())
        self.centerOn(mousePoint)


class GraphicsScene(QGraphicsScene):

    def __init__(self, parent):
        super(GraphicsScene, self).__init__(parent)
        self.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))
        self.image = QPixmap(os.path.join(PRJ_PATH, "img", "test.png"))
        self.item = self.addPixmap(self.image)




