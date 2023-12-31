# Plugin Exporter <img src="https://github.com/Scriptbash/PluginExporter/blob/main/plugin_exporter/icon.png?raw=true" alt="PluginExporter" width="90"/>
A QGIS plugin for exporting plugins

## Description

Plugin Exporter is a QGIS plugin that can export installed plugins into a .csv or .json file. The user can export all the installed plugins or select the plugins they want to export.
Plugin Exporter can also use the generated file to install the plugins back in QGIS. Third party repositories are also supported as of v0.2.0.

## Getting Started

### Dependencies

* QGIS 3.28 or above (I did not test the plugin with older versions).

### Installing
Plugin Exporter is now available in the QGIS repos! https://plugins.qgis.org/plugins/plugin_exporter/
* Go in the Plugins menu and click on Manage and Install Plugins
* Search for Plugin Exporter
* Click on install

### How to use Plugin Exporter
#### Export plugins
* Click on the Plugin Exporter icon <img src="https://github.com/Scriptbash/PluginExporter/blob/main/plugin_exporter/icon.png?raw=true" alt="drawing" width="30"/> or go in the "Plugins" menu, select "Plugin Exporter" and click on "Export plugins"
* You can then select which plugins to export
* By default, third party repositories (either enabled or disabled) are also exported
* Select a format (.csv or .json)
* Select an output file and click on "OK"
* The plugin will export the plugins

#### Import plugins
* Click on the Plugin Exporter icon <img src="https://github.com/Scriptbash/PluginExporter/blob/main/plugin_exporter/icon.png?raw=true" alt="drawing" width="30"/> or go in the "Plugins" menu, select "Plugin Exporter" and click on "Export plugins"
* Select the "Import" option
* Select a file to import and click on "OK"
* The plugin will add third party repositories if they were exported and install the plugins. By default it will skip those already installed

## Screenshot
![image](https://github.com/Scriptbash/PluginExporter/assets/98601298/0a1c4ee9-14fc-449c-a431-c60afde489db)

## Help

If you have an issue, a feature request or feedback, please let me know by opening an issue here : https://github.com/Scriptbash/PluginExporter/issues
