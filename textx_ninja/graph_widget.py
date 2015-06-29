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
from PyQt4.QtCore import QSize
from PyQt4.QtWebKit import QGraphicsWebView
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QSizePolicy
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

        path = os.path.join(PRJ_PATH, "img", 'textX-ninja.svg')
        self.scene.webview = QGraphicsWebView()
        self.create_webview(path)

        self.scene.addItem(self.scene.webview)

        self._graph.setScene(self.scene)
        self._graph.setDragMode(QGraphicsView.ScrollHandDrag)
        self._graph.setRenderHints(QPainter.SmoothPixmapTransform)

        self._graph.setBackgroundBrush(QBrush(QColor(255, 255, 255, 255)))

        self.label = QLabel(self)
        self.label.setStyleSheet(
            "QLabel { color : black; background-color: white;}")

        #Main Layout
        main_hbox = QVBoxLayout(self)
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)
        main_hbox.addWidget(self.label)
        main_hbox.addWidget(self._graph)

    def create_webview(self, path):
        self.scene.webview.load(QUrl(path))
        self.scene.webview.setFlags(QGraphicsItem.ItemClipsToShape)
        self.scene.webview.setCacheMode(QGraphicsItem.NoCache)
        self.scene.webview.setZValue(0)

        self.w = self._graph.size().width()
        self.h = self._graph.size().height()

        self.scene.webview.setSizePolicy(QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.scene.webview.page().setPreferredContentsSize(QSize(
            self._graph.size().width(), self._graph.size().height()))
        self.scene.webview.setResizesToContents(True)

        frame = self.scene.webview.page().mainFrame()
        frame.setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        frame.setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

    def load_meta_model(self, path, name):
        self.scene.clear()

        self.scene = GraphicsScene(self._graph)

        self.scene.webview = QGraphicsWebView()
        self.create_webview(path)

        self.scene.addItem(self.scene.webview)

        self.add_label(name)

        self._graph.setScene(self.scene)

        self._graph.fitInView(
            self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def update_error_lbl(self, fileName):
        self.add_label(fileName, True)

    def add_label(self, fileName, isError=False):
        err = 'There is an error in '  # mozda kao konstanta
        if isError:
            txtLbl = err + fileName[fileName.rfind('/') + 1:fileName.rfind('.')]
        else:
            txtLbl = fileName[fileName.rfind('/') +
                1:fileName.rfind('.')].capitalize()

        self.label.setText(txtLbl)
        self.label.repaint()


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
