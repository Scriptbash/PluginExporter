# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginExporter
                                 A QGIS plugin
 Exports plugins
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-08-03
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Francis Lapointe
        email                : francis.lapointe5@usherbrooke.ca
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QLabel, QCheckBox, QComboBox
from qgis.gui import QgsPluginManagerInterface
from qgis.core import Qgis
import qgis.utils

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .plugin_exporter_dialog import PluginExporterDialog
import pyplugin_installer
import os.path
import csv
import json
import pathlib


class PluginExporter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PluginExporter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Plugin Exporter')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        #List that will contain the metadata of all installed plugins
        self.plugins_metadata = []

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PluginExporter', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/plugin_exporter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Export plugins'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Plugin Exporter'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = PluginExporterDialog()
            self.get_plugins()
            self.dlg.btn_select_all.clicked.connect(self.select_all)
            self.dlg.btn_deselect_all.clicked.connect(self.deselect_all)
            self.dlg.chk_active_plugins.stateChanged.connect(self.get_plugins)
            self.dlg.chk_official_plugins.stateChanged.connect(self.get_plugins)
            self.dlg.btn_refresh.clicked.connect(self.get_plugins)
            self.dlg.rd_import.toggled.connect(self.toggle_widget)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            if self.dlg.rd_export.isChecked():
                self.export_plugins()
            elif self.dlg.rd_import.isChecked():
                self.import_plugins()

    def get_plugins(self):
        if self.dlg.chk_active_plugins.isChecked():
            plugins = qgis.utils.active_plugins
        else:
            plugins = qgis.utils.available_plugins
        self.add_plugins_to_table(plugins)

    def add_plugins_to_table(self, plugins):
        self.clear_plugins_table()
        table = self.dlg.table_plugins

        for plugin in plugins:
            metadata = self.iface.pluginManagerInterface().pluginMetadata(plugin)
            if self.dlg.chk_official_plugins.isChecked():
                if metadata['zip_repository'] == 'QGIS Official Plugin Repository':
                    self.plugins_metadata.append(metadata)  #Adds the plugin metadata to the list
                else:
                    continue
            else:
                self.plugins_metadata.append(metadata)

            current_row = table.rowCount()  # Get the number of rows the table has
            table.insertRow(current_row)  # Inserts a new row below the last row
            chk_selected = QCheckBox()
            chk_selected.setChecked(True)
            lbl_plugin_name = QLabel()
            lbl_plugin_name.setText(metadata['name'])
            lbl_version = QLabel()
            lbl_version.setText(metadata['version_installed'])
            lbl_author = QLabel()
            lbl_author.setText(metadata['author_name'])

            table.setCellWidget(current_row, 0, chk_selected)
            table.setCellWidget(current_row, 1, lbl_plugin_name)
            table.setCellWidget(current_row, 2, lbl_version)
            table.setCellWidget(current_row, 3, lbl_author)

        table.resizeColumnsToContents()

    def select_all(self):
        table = self.dlg.table_plugins
        rows = table.rowCount()
        for row in range(rows):
            checkbox = table.cellWidget(row, 0)
            checkbox.setChecked(True)

    def deselect_all(self):
        table = self.dlg.table_plugins
        rows = table.rowCount()
        for row in range(rows):
            checkbox = table.cellWidget(row, 0)
            checkbox.setChecked(False)

    def clear_plugins_table(self):
        table = self.dlg.table_plugins
        while table.rowCount() > 0:
            table.removeRow(0)

    def export_plugins(self):
        file_format = self.dlg.combo_file_format.currentText()
        output_file = self.dlg.file_output_export.filePath()
        table = self.dlg.table_plugins
        plugin_list = []
        rows = table.rowCount()
        cols = table.columnCount()

        for row in range(rows):
            for col in range(cols):
                current_widget = table.cellWidget(row, col)
                if isinstance(current_widget, QCheckBox):
                    if not current_widget.isChecked():
                        break
                elif isinstance(current_widget, QLabel):
                    # plugin_list.append(current_widget.text())
                    # next((item for item in dicts if item["name"] == "Pam"), None)
                    current_plugin = next(
                        (item for item in self.plugins_metadata if item["name"] == current_widget.text()), None)
                    if current_plugin:
                        plugin_list.append(current_plugin)
        if plugin_list:
            if output_file:
                if file_format == '.csv':
                    with open(output_file, 'w', encoding='utf8', newline='') as f:
                            keys = plugin_list[0].keys()
                            dict_writer = csv.DictWriter(f, keys)
                            dict_writer.writeheader()
                            dict_writer.writerows(plugin_list)
                    self.iface.messageBar().pushSuccess("Success", "Selected plugins were exported successfully.")
                elif file_format == '.json':
                    with open(output_file, 'w') as file:
                        json.dump(plugin_list, file)
                    self.iface.messageBar().pushSuccess("Success", "Selected plugins were exported successfully.")
            else:
                self.iface.messageBar().pushMessage("Error",
                                                    "You must select an output directory.",
                                                    level=Qgis.Critical)
        else:
            self.iface.messageBar().pushMessage("Error",
                                                "At least one plugin must be selected.",
                                                level=Qgis.Critical)

    def import_plugins(self):
        input_file = self.dlg.file_input_import.filePath()
        file_extension = pathlib.Path(input_file).suffix
        installed_plugins = qgis.utils.available_plugins

        if file_extension == '.csv':
            try:
                with open(input_file, 'r') as f:
                    dict_reader = csv.DictReader(f)
                    plugins = list(dict_reader)
            except:
                self.iface.messageBar().pushMessage("Error",
                                                    "Unable to read the CSV file.",
                                                    level=Qgis.Critical)
        elif file_extension == '.json':
            try:
                f = open(input_file)
                plugins = json.load(f)
            except:
                self.iface.messageBar().pushMessage("Error",
                                                    "Unable to read the JSON file.",
                                                    level=Qgis.Critical)
        else:
            self.iface.messageBar().pushMessage("Error",
                                                "Unsupported file type.",
                                                level=Qgis.Critical)

        for plugin in plugins:
            if self.dlg.chk_skip_installed.isChecked():
                if plugin['id'] in installed_plugins:
                    self.iface.messageBar().pushInfo("Info",
                                                     "Skipped " + plugin['name'] + " as it's already installed.")
                    continue
            try:
               pyplugin_installer.instance().installPlugin(plugin['id'])
               self.iface.messageBar().pushSuccess("Success", plugin['name'] + " was installed successfully.")
            except KeyError:
                self.iface.messageBar().pushMessage("Error",
                                                    "Could not install " + plugin['name'] + ".",
                                                    level=Qgis.Critical)

    def toggle_widget(self):
        if self.dlg.rd_import.isChecked():
            self.dlg.file_output_export.setEnabled(False)
            self.dlg.combo_file_format.setEnabled(False)
            self.dlg.chk_skip_installed.setEnabled(True)
            self.dlg.file_input_import.setEnabled(True)
        else:
            self.dlg.file_input_import.setEnabled(False)
            self.dlg.chk_skip_installed.setEnabled(False)
            self.dlg.file_output_export.setEnabled(True)
            self.dlg.combo_file_format.setEnabled(True)
