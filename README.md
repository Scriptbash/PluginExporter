# Plugin Exporter
A QGIS plugin for exporting plugins

## Description

Plugin Exporter is a QGIS plugin that can export installed plugins into a .csv or .json file. The user can export all the installed plugins or select the plugins they want to export.
Plugin Exporter can also use the generated file to install the plugins back in QGIS.

## Getting Started

### Dependencies

* QGIS 3.28 or above (I did not test the plugin with older versions).

### Installing
I am planning on releasing the plugin in the official QGIS repo soon. In the meantime, please use my custom repository.
* In the QGIS plugin manager, click on settings
* Add the following URL: https://scriptbash.github.io/plugins.xml
* Search for "Plugin Exporter" in the "all" menu
* Click on install

### How to use Plugin Exporter
#### Export plugins
* Click on the "Plugins" menu
* Select "Plugin Exporter" and click on "Export plugins"
* You can then select which plugins to export
* Select a format (.csv or .json)
* Select an output file and click on "OK"
* The plugin will export the plugins

#### Import plugins
* Click on the "Plugins" menu
* Select "Plugin Exporter" and click on "Export plugins"
* Select the "Import" option
* Select a file to import and click on "OK"
* The plugin will install the plugins and by default will skip those already installed

## Help

If you have an issue, a feature request or feedback, please let me know by opening an issue here : https://github.com/Scriptbash/PluginExporter/issues
