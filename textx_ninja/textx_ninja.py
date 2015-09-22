# -*- coding: UTF-8 -*-

import os
from PyQt4.QtGui import QMessageBox
from ninja_ide.core import plugin
from ninja_ide.core import settings
from ninja_ide.core.plugin_interfaces import IProjectTypeHandler
from ninja_ide.core import file_manager
from ninja_ide.tools import json_manager

from .textxsyntax import TEXTX_EXTENSION, TEXTX_SYNTAX
from .graph_widget import TextXGraphWidget

from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export
from textx.export import model_export
from textx.exceptions import TextXError

from ninja_ide.gui.main_panel import main_container

import pydot

PROJECT_TYPE = "textX Project"
SUPPORTED_EXTENSIONS = [".py",
                        ".jpg",
                        ".png",
                        ".rst",
                        ".tx",
                        ".dot"]

#Names for files
METAMODEL_SVG = "metamodel.svg"
MODEL_SVG = "model.svg"

METAMODEL = "metamodel"
MODEL = "model"

#Project path
PRJ_PATH = os.path.abspath(os.path.dirname(__file__)).decode('utf-8')


class TextXProjectType(IProjectTypeHandler):
    """
    A handler for textX type projects.
    """

    def __init__(self, locator):
        self.locator = locator

    def get_pages(self):
        """
        Returns a collection of QWizardPage
        """
        return ()

    def on_wizard_finish(self, wizard):
        """
        Called when the user finish the wizard
        @wizard: QWizard instance
        """
        global PROJECT_TYPE
        ids = wizard.pageIds()
        page = wizard.page(ids[1])
        path = unicode(page.txtPlace.text())
        if not path:
            QMessageBox.critical(wizard, wizard.tr("Incorrect Location"),
                wizard.tr("The project couldn\'t be create"))
            return
        project = {}
        name = unicode(page.txtName.text())
        project['name'] = name
        project['description'] = unicode(page.txtDescription.toPlainText())
        project['license'] = unicode(page.cboLicense.currentText())
        project['venv'] = unicode(page.vtxtPlace.text())
        project["project-type"] = PROJECT_TYPE
        project["supported-extensions"] = SUPPORTED_EXTENSIONS

        path = os.path.join(path, name)
        tx_path = os.path.join(path, 'metamodel.tx')

        try:
            # Create initial folder structure
            file_manager.create_folder(path, add_init_file=True)
            json_manager.create_ninja_project(path, name, project)
            self.create_tx_init_file(tx_path)
        except file_manager.NinjaIOException as e:
            QMessageBox.critical(wizard, wizard.tr("Error"), str(e))
            return False

        wizard._load_project(path)

    def get_context_menus(self):
        """"
        Returns a iterable of QMenu
        """
        return()

    def create_tx_init_file(self, fileName):
        if not os.path.isfile(fileName):
            f = open(fileName, 'w')
            f.flush()
            f.close()


class TextXNinja(plugin.Plugin):
    def initialize(self):
        # Init your plugin
        self.editor_s = self.locator.get_service('editor')
        self.explorer_s = self.locator.get_service('explorer')
        self.misc_s = self.locator.get_service('misc')

        # Set a project handler for NINJA-IDE Plugin
        self.explorer_s.set_project_type_handler(PROJECT_TYPE,
                TextXProjectType(self.locator))

        #Graph widget in misc container
        self.graph_widget = TextXGraphWidget()
        icon_path = os.path.join(PRJ_PATH, "img", "graph.png")
        description = "TextX meta-model visualization widget."

        self.misc_s.add_widget(self.graph_widget, icon_path, description)

        # Natural syntax support
        settings.EXTENSIONS[TEXTX_EXTENSION] = 'textx'
        settings.SYNTAX['textx'] = TEXTX_SYNTAX

        #Signals
        self.editor_s.fileSaved.connect(self._visualize)
        self.editor_s.fileOpened.connect(self._visualize)
        self.editor_s.currentTabChanged.connect(self._visualize)
        self.editor_s.editorKeyPressEvent.connect(self.file_changed)

    def file_changed(self):
        '''
        Handles key pressed event
        '''
        filename = self.editor_s.get_editor_path()
        fileType = self.get_file_type(filename)

        if not fileType == "py":
            text = self.editor_s.get_text()
            if text == "":
                if fileType == METAMODEL:
                    self.graph_widget.add_label("Metamodel", 0)
                elif fileType == MODEL:
                    self.graph_widget.add_label("Model", 1)
            else:
                name = file_manager.get_module_name(filename)
                if fileType == METAMODEL:
                    newFileName = name + ".tx"
                elif fileType == MODEL:
                    newFileName = name + ".ml"

                tmp_folder = os.path.join(PRJ_PATH, "temp")
                if not file_manager.folder_exists(tmp_folder):
                    file_manager.create_folder(tmp_folder)
                f = open(os.path.join(tmp_folder, newFileName), 'w')
                f.write(text)
                f.flush()
                f.close()
                self._visualize(os.path.join(tmp_folder, newFileName))

    def _visualize(self, fileName):
        fileType = self.get_file_type(fileName)
        if fileType == METAMODEL:
            # Get meta-model from language description
            try:
                self.meta_model = metamodel_from_file(fileName)
                if not self.graph_widget.isHidden():
                    # Export model to dot
                    path = os.path.join(PRJ_PATH, "meta.dot")
                    metamodel_export(self.meta_model, path)
                    svg_path = os.path.join(PRJ_PATH, "img", METAMODEL_SVG)
                    self.create_load_svg(path, svg_path,
                        file_manager.get_module_name(fileName), 0)
            except TextXError as error:
                self.handle_exception(fileName, 0, error.line)
        elif fileType == MODEL:
            if not self.graph_widget.isHidden():
                try:
                    self.model = self.meta_model.model_from_file(fileName)
                    path = os.path.join(PRJ_PATH, "model.dot")
                    model_export(self.model, path)
                    svg_path = os.path.join(PRJ_PATH, "img", MODEL_SVG)
                    self.create_load_svg(path, svg_path,
                        file_manager.get_module_name(fileName), 1)
                except TextXError as error:
                    self.handle_exception(fileName, 1, error.line)

    def create_load_svg(self, path, svg_path, name, tabIndex):
        f = pydot.graph_from_dot_file(path)
        f.write_svg(svg_path)

        self.graph_widget.load_graph(svg_path, name, tabIndex)
        os.remove(path)

    def get_file_type(self, fileName):
        fileExtension = file_manager.get_file_extension(fileName)
        if fileExtension == "tx":
            return METAMODEL
        elif not fileExtension == "py":
            return MODEL
        return "py"

    def handle_exception(self, fileName, tabindex, lineno):
        self.graph_widget.update_error_lbl(file_manager.get_module_name(
                    fileName), tabindex)
        main = main_container.MainContainer()
        main.editor_jump_to_line(lineno=int(lineno) - 1)

    def finish(self):
        # Shutdown your plugin
        file_manager.delete_folder(os.path.join(PRJ_PATH, "temp"))

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        pass
