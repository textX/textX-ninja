# -*- coding: utf-8 -*-

import os
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGraphicsView
from PyQt4.QtGui import QGraphicsItem
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtGui import QPainter
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QTabWidget
from PyQt4.QtCore import QSize
from PyQt4.QtWebKit import QGraphicsWebView
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QSizePolicy
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
#Error message
ERROR_MESSAGE = "There is an error in "

PRJ_PATH = os.path.abspath(os.path.dirname(__file__)).decode('utf-8')


class TextXGraphWidget(QWidget):
    """
    Widget for graph representation of textX grammar
    """

    def __init__(self):
        QWidget.__init__(self)
        self._main_container = main_container.MainContainer()
        self._explorer_container = explorer_container.ExplorerContainer()

        self.tabs = QTabWidget(self)

        #Graph widget
        self._graph = GraphicsView()
        self._graphMl = GraphicsView()

        # Graph scene
        self.scene = GraphicsScene(self._graph)
        self.sceneMl = GraphicsScene(self._graphMl)

        path = os.path.join(PRJ_PATH, "img", 'textX-ninja.svg')
        self.scene.webview = QGraphicsWebView()
        self.create_webview(path, self.scene, self._graph)
        self.scene.addItem(self.scene.webview)

        self._graph.setScene(self.scene)
        self.set_view(self._graph)

        self._graphMl.setScene(self.sceneMl)
        self.set_view(self._graphMl)

        self.tabs.addTab(self._graph, "Metamodel")
        self.tabs.addTab(self._graphMl, "Model")

        #Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tabs)

    def set_view(self, graph):
        graph.setDragMode(QGraphicsView.ScrollHandDrag)
        graph.setRenderHints(QPainter.SmoothPixmapTransform)
        graph.setBackgroundBrush(QBrush(QColor(255, 255, 255, 255)))

        # Main view Layout
        main_hbox = QVBoxLayout()
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)
        main_hbox.addWidget(graph)

    def create_webview(self, path, scene, graph):
        scene.webview.load(QUrl(path))
        scene.webview.setFlags(QGraphicsItem.ItemClipsToShape)
        scene.webview.setCacheMode(QGraphicsItem.NoCache)
        scene.webview.setZValue(0)

        self.w = graph.size().width()
        self.h = graph.size().height()

        scene.webview.setSizePolicy(QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        scene.webview.page().setPreferredContentsSize(QSize(
            graph.size().width(), graph.size().height()))
        scene.webview.setResizesToContents(True)

        frame = scene.webview.page().mainFrame()
        frame.setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        frame.setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

    def load_graph(self, path, name, tabIndex):
        if tabIndex == 0:
            self.scene.clear()
            self.scene.webview = QGraphicsWebView()
            self.create_webview(path, self.scene, self._graph)
            self.scene.addItem(self.scene.webview)
            self._graph.setScene(self.scene)
            self._graph.fitInView(
                self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        elif tabIndex == 1:
            self.sceneMl.clear()
            self.sceneMl.webview = QGraphicsWebView()
            self.create_webview(path, self.sceneMl, self._graphMl)
            self.sceneMl.addItem(self.sceneMl.webview)
            self._graphMl.setScene(self.sceneMl)
            self._graphMl.fitInView(
                self.sceneMl.itemsBoundingRect(), Qt.KeepAspectRatio)

        self.add_label(name, tabIndex)
        # focus on tab
        self.tabs.setCurrentIndex(tabIndex)

    def update_error_lbl(self, name, tabIndex):
        self.add_label(name, tabIndex, True)
        if tabIndex == 0:
            self.scene.clear()
        elif tabIndex == 1:
            self.sceneMl.clear()

    def add_label(self, name, tabIndex, isError=False):
        if isError:
            txtLbl = ERROR_MESSAGE + name
        else:
            txtLbl = name.capitalize()
        self.tabs.setTabText(tabIndex, txtLbl)


class GraphicsView(QGraphicsView):

    def __init__(self):
        super(GraphicsView, self).__init__()
        self.label = QLabel(self)

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

    def mousePressEvent(self, event):
        self.parent.setDragMode(1)
        self.startPos = event.scenePos()

    def mouseReleaseEvent(self, event):
        self.parent.setDragMode(0)
