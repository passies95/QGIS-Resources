from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       QgsProcessingOutputNumber,
                       QgsProcessingOutputString,
                       QgsProcessingParameterFileDestination)

import rasterio
from skimage.filters import threshold_otsu
import tempfile
import os


class ThresholdUsingOtsuAlgorithm(QgsProcessingAlgorithm):
    """
    This script computes a threshold value from a raster layer using the Otsu Algorithm.
    """

    INPUT = 'INPUT'
    OUTPUT_HTML = 'OUTPUT_HTML'
    OUTPUT_THRESHOLD = 'OUTPUT_THRESHOLD'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ThresholdUsingOtsuAlgorithm()

    def name(self):
        return 'computethresholdwithotsu'

    def displayName(self):
        return self.tr('Compute Threshold with Otsu')

    def group(self):
        return self.tr('IDP Site Mapping')

    def groupId(self):
        return 'idpsitemapping'

    def shortHelpString(self):
        return self.tr("Input Layer is a raster layer with a single band.")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input raster layer')
            )
        )

        # Add a parameter to allow the user to choose a save location for the HTML document
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_HTML,
                self.tr('Output HTML document'),
                fileFilter='HTML files (*.html)',
                defaultValue='',
                optional=True
            )
        )

        # Add a parameter to hold the output threshold value
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_THRESHOLD,
                self.tr('Threshold Value')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        input_raster_path = input_raster.source()

        with rasterio.open(input_raster_path) as src:
            img = src.read()

        # Compute threshold using Otsu's method
        thresh_value = threshold_otsu(img)

        # Return the threshold value as output
        output_values = {
            self.OUTPUT_THRESHOLD: thresh_value
        }

        # Create an HTML document containing the threshold value
        html_output = f'<p>Threshold Value: {thresh_value}</p>'

        # Get the output HTML file path from the parameters
        html_output_param = self.parameterAsString(parameters, self.OUTPUT_HTML, context)

        # If no output HTML file path is provided, save to a temporary file
        if not html_output_param:
            temp_dir = tempfile.gettempdir()
            html_output_param = os.path.join(temp_dir, 'output.html')
        else:
            # If a custom location is provided, use it
            html_output_param = html_output_param

        # Write the HTML content to the output file
        with open(html_output_param, 'w') as output_file:
            output_file.write(html_output)

        # Add the HTML file path to the output values
        output_values[self.OUTPUT_HTML] = html_output_param

        return output_values
