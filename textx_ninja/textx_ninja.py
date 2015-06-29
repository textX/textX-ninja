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

import pydot

PROJECT_TYPE = "textX Project"
SUPPORTED_EXTENSIONS = [".py",
                        ".jpg",
                        ".png",
                        ".rst",
                        ".tx",
                        ".dot"]

TMP_METAMODEL = "tmp_metamodel.tx"
TMP_MODEL = "tmp_model.ml"
METAMODEL = "metamodel.svg"
MODEL = "model.svg"

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
        self.my_widget = TextXGraphWidget()
        icon_path = os.path.join(PRJ_PATH, "img", "graph.png")
        description = "TextX meta-model visualization widget."

        self.misc_s.add_widget(self.my_widget, icon_path, description)

        # Natural syntax support
        settings.EXTENSIONS[TEXTX_EXTENSION] = 'textx'
        settings.SYNTAX['textx'] = TEXTX_SYNTAX

        #Signals
        self.editor_s.fileSaved.connect(self._export_model)
        self.editor_s.fileOpened.connect(self._export_model)
        self.editor_s.currentTabChanged.connect(self._export_model)
        self.editor_s.editorKeyPressEvent.connect(self.file_changed)

    def file_changed(self):
        filename = self.editor_s.get_editor_path()
        filePath, fileExtension = os.path.splitext(filename)
        text = self.editor_s.get_text()
        if fileExtension == '.tx':
            newFileName = TMP_METAMODEL
        else:
            newFileName = TMP_MODEL
        f = open(os.path.join(PRJ_PATH, newFileName), 'w')
        f.write(text)
        f.flush()
        f.close()
        self._export_model(os.path.join(PRJ_PATH, newFileName))

    def _export_model(self, fileName):
        filePath, fileExtension = os.path.splitext(fileName)
        if fileExtension == '.tx':
            # Get meta-model from language description
            try:
                self.meta_model = metamodel_from_file(fileName)
                # Optionally export model to dot
                path = os.path.join(PRJ_PATH, "meta.dot")

                metamodel_export(self.meta_model, path)

                svg_path = os.path.join(PRJ_PATH, "img", METAMODEL)
                self.create_load_svg(path, svg_path)
            except:
                self.my_widget.update_error_lbl(fileName)

        elif not fileExtension == '.py':
            try:
                self.model = self.meta_model.model_from_file(fileName)
                path = os.path.join(PRJ_PATH, "model.dot")
                model_export(self.model, path)
                svg_path = os.path.join(PRJ_PATH, "img", MODEL)
                self.create_load_svg(path, svg_path)
            except:
                self.my_widget.update_error_lbl(fileName)

    def create_load_svg(self, path, svg_path):
        f = pydot.graph_from_dot_file(path)
        f.write_svg(svg_path)

        self.my_widget.load_meta_model(svg_path, svg_path)
        os.remove(path)

    def finish(self):
        # Shutdown your plugin
        os.remove(os.path.join(PRJ_PATH, TMP_METAMODEL))
        os.remove(os.path.join(PRJ_PATH, TMP_MODEL))
        os.remove(os.path.join(PRJ_PATH, "img", MODEL))

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        pass
