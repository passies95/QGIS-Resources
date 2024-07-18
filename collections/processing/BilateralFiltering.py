from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingOutputRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber)
import cv2
import rasterio

class BilateralFiltering(QgsProcessingAlgorithm):
    """
    This script applies bilateral filtering to a raster layer using rasterio and OpenCV.
    """

    INPUT = 'INPUT'
    FILTERED_IMAGE = 'FILTERED_IMAGE'
    N = 'N'
    SIGMA_S = 'SIGMA_S'
    SIGMA_R = 'SIGMA_R'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return BilateralFiltering()

    def name(self):
        return 'bilateralfiltering'

    def displayName(self):
        return self.tr('Bilateral Filtering')

    def group(self):
        return self.tr('IDP Site Mapping')

    def groupId(self):
        return 'idpsitemapping'

    def shortHelpString(self):
        return self.tr("Apply bilateral filtering to remove noise from the input raster layer.")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Raster Layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.N,
                self.tr('Filter Support Size'),
                QgsProcessingParameterNumber.Integer,
                defaultValue=9
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIGMA_S,
                self.tr('Geometric Weight Decay'),
                QgsProcessingParameterNumber.Double,
                defaultValue=75
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SIGMA_R,
                self.tr('Intensity Weight Decay'),
                QgsProcessingParameterNumber.Double,
                defaultValue=75
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.FILTERED_IMAGE, self.tr("Filtered Raster"), None, False)
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        output_layer_path = self.parameterAsOutputLayer(parameters, self.FILTERED_IMAGE, context)
        N = self.parameterAsInt(parameters, self.N, context)
        sigma_s = self.parameterAsDouble(parameters, self.SIGMA_S, context)
        sigma_r = self.parameterAsDouble(parameters, self.SIGMA_R, context)

        # Get input raster path
        input_raster_path = input_raster.source()

        # Read input raster using rasterio
        with rasterio.open(input_raster_path) as src:
            img = src.read(1)  # Read the first band
            
            # Apply bilateral filtering using OpenCV
            #filtered_img = cv2.bilateralFilter(img, 10, 75, 75)
            filtered_img = cv2.bilateralFilter(img, d=N, sigmaColor=sigma_s, sigmaSpace=sigma_r)

            # Write filtered image to output raster layer
            self.array_to_raster(filtered_img, src.bounds, src.meta, output_layer_path)

        return {self.FILTERED_IMAGE: output_layer_path}

    def array_to_raster(self, array, bounds, metadata, output_path):
        # Write array to raster using rasterio
        with rasterio.open(output_path, 'w', **metadata) as dst:
            dst.write(array, 1)