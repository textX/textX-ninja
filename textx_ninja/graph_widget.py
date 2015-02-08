# -*- coding: utf-8 -*-

import os
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from ninja_ide.gui.main_panel import main_container
from ninja_ide.gui.explorer import explorer_container

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
        graph_widget = GraphWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(graph_widget)
        scroll_area.setWidgetResizable(False)
        self._graph = scroll_area

        #Buttons
        self._start_button = QPushButton(self.tr("Start"))
        self._stop_button = QPushButton(self.tr("Stop"))

        #Main Layout
        main_hbox = QHBoxLayout(self)

        #Graph Layout
        vboxGph = QVBoxLayout()
        vboxGph.addWidget(self._graph)

        #Buttons Layout
        vboxBtn = QVBoxLayout()
        vboxBtn.addWidget(self._start_button)
        vboxBtn.addWidget(self._stop_button)

        main_hbox.addLayout(vboxGph)
        main_hbox.addLayout(vboxBtn)


class GraphWidget(QLabel):
    """
    Widget for meta-model visualization.
    """
    def __init__(self):
        QLabel.__init__(self)
        pixmap = QPixmap(os.path.join(PRJ_PATH, "img", "example.dot.png"))
        self.setPixmap(pixmap)




