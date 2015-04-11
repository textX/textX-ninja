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


PROJECT_TYPE = "textX Project"
SUPPORTED_EXTENSIONS = [".py",
                        ".jpg",
                        ".png",
                        ".rst",
                        ".tx",
                        ".dot"]

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

        try:
            # Create initial folder structure
            file_manager.create_folder(path, add_init_file=False)
            json_manager.create_ninja_project(path, name, project)

        except file_manager.NinjaIOException as e:
            QMessageBox.critical(wizard, wizard.tr("Error"), str(e))
            return False

        wizard._load_project(path)

    def get_context_menus(self):
        """"
        Returns a iterable of QMenu
        """
        return()


class TextXNinja(plugin.Plugin):
    def initialize(self):
        # Init your plugin
        self.editor_s = self.locator.get_service('editor')
        self.explorer_s = self.locator.get_service('explorer')
        self.misc_s = self.locator.get_service('misc')

        # Set a project handler for NINJA-IDE Plugin
        self.explorer_s.set_project_type_handler(PROJECT_TYPE,
                TextXProjectType(self.locator))

        # On file open change sidebar_widget to support code folding
        # for Natural code.
        #self.editor_s.fileOpened.connect(
            #get_change_sidebar_slot(self.editor_s))

        #Graph widget in misc container
        my_widget = TextXGraphWidget()
        icon_path = os.path.join(PRJ_PATH, "img", "graph.png")
        description = "TextX meta-model visualization widget."

        self.misc_s.add_widget(my_widget, icon_path, description)

        # Natural syntax support
        settings.EXTENSIONS[TEXTX_EXTENSION] = 'textx'
        settings.SYNTAX['textx'] = TEXTX_SYNTAX

        #Signals
        self.editor_s.beforeFileSaved.connect(self._export_model)

    def _export_model(self, fileName):
        # Get meta-model from language description
        model = metamodel_from_file(fileName)
        print(model)
        # Optionally export model to dot
        metamodel_export(model, 'example.dot')

    def finish(self):
        # Shutdown your plugin
        pass

    def get_preferences_widget(self):
        # Return a widget for customize your plugin
        pass
