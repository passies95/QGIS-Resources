'''This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.'''

import os
import subprocess
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import *
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox

class configureRESOURCES(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()

    def tr(self, string):
        return QCoreApplication.translate("Configure Resources", string)
       
    def name(self):
        return "Configure Resources"

    def displayName(self):
        return self.tr("Configure Resources (Dependencies)")

    def group(self):
        return self.tr('IDP Site Mapping')

    def shortHelpString(self):
        return self.tr('''This script will attempt to install the dependencies required for IDP Site Mapping tool for Windows users.
        If the tool fails, manual installation will be required using 'pip install '. ''')

    def helpUrl(self):
        return "https://github.com/passies95/QGIS-Resources/wiki"

    def groupId(self):
        return "Configure"

    def createInstance(self):
        return configureRESOURCES()

    def initAlgorithm(self, config=None):
        pass

    def processAlgorithm(self, parameters, context, feedback):

        if os.name == 'nt': ##GUI for python installer via subprocess module
            reply = QMessageBox.question(iface.mainWindow(), 'Install Dependencies',
                 'Attempting to install Dependencies. Do you wish to continue?', QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    is_admin = os.getuid() == 0
                except AttributeError:
                    import ctypes
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

                modules = ['numpy==1.24.1', 'rasterio==1.3.9', 'opencv-python==4.5.5.64', 'networkx==3.2.1', 'scikit-image==0.22.0',
                            'scikit-learn==1.4.2', ]

                for module in modules:
                    try:
                        if is_admin:
                            status = subprocess.check_call(['python3','-m', 'pip', 'install', module])
                        else:
                            status = subprocess.check_call(['python3','-m', 'pip', 'install', module,'--user'])

                        if status != 0:
                            feedback.reportError(self.tr('Warning','Failed to install %s - consider installing manually'%(module)))
                    except subprocess.CalledProcessError:
                        feedback.reportError(self.tr('Warning','Failed to install %s - consider installing manually'%(module)))
                        return {}
            else:
                feedback.reportError(self.tr('Installation canceled by user.'))
                return None

        else:
            feedback.reportError(self.tr('Warning','macOS and Linux users - manually install the segment-geospatial python package.'))
            return {}

        return {}
