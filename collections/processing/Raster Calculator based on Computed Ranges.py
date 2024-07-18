from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingOutputRasterLayer)

from qgis import processing

class RasterClassificationUsingComputedRanges(QgsProcessingAlgorithm):
    """
    This script computes a threshold value from a raster layer using the Otsu Algorithm.
    """

    INPUT = 'INPUT'
    MINIMUM_VALUE = 'MINIMUM_VALUE'
    MAXIMUM_VALUE = 'MAXIMUM_VALUE'
    CLASSIFIED_RASTER = 'CLASSIFIED_RASTER'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return RasterClassificationUsingComputedRanges()

    def name(self):
        return 'rasterclassificationusingcomputedranges'

    def displayName(self):
        return self.tr('Raster Classification using Computed Ranges')

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
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MINIMUM_VALUE,
                self.tr('Minimum Value'),
                QgsProcessingParameterNumber.Double,
                minValue=0
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAXIMUM_VALUE,
                self.tr('Maximum Value'),
                QgsProcessingParameterNumber.Double,
                minValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.CLASSIFIED_RASTER, self.tr("Classified Raster"), None, False)
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Get input raster layer
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        # Get minimum and maximum values
        min_value = self.parameterAsDouble(parameters, self.MINIMUM_VALUE, context)
        max_value = self.parameterAsDouble(parameters, self.MAXIMUM_VALUE, context)

        # Define gdal_calc expression
        expression = f'logical_and((A >= {min_value}), (A <= {max_value}))'

        # Output file path
        output_file_path = self.parameterAsOutputLayer(parameters, self.CLASSIFIED_RASTER, context)

        # Process gdal_calc
        processing.run("gdal:rastercalculator", {
            'INPUT_A': input_raster,
            'BAND_A': 1,
            'FORMULA': expression,
            'RTYPE': 0,
            'NO_DATA': None,
            'OPTIONS': '',
            'OUTPUT': output_file_path
        }, context=context, feedback=feedback)

        return {self.CLASSIFIED_RASTER: output_file_path}