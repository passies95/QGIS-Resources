from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingOutputRasterLayer,
                       QgsProcessingParameterRasterDestination,
                       QgsProcessingParameterNumber)
import cv2
import numpy as np  # Added import for numpy
import rasterio

class SIFT(QgsProcessingAlgorithm):
    """
    This script applies Scale Invariant Feature Transform (SIFT) to a raster layer using OpenCV.
    """

    INPUT = 'INPUT'
    SIFT_IMAGE = 'SIFT_IMAGE'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SIFT()

    def name(self):
        return 'SIFT'

    def displayName(self):
        return self.tr('Scale Invariant Feature Transform - SIFT')

    def group(self):
        return self.tr('IDP Site Mapping')

    def groupId(self):
        return 'idpsitemapping'

    def shortHelpString(self):
        return self.tr("Scale Invariant Feature Transform - SIFT")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Grayscale Raster Layer')
            )
        )
      
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.SIFT_IMAGE, self.tr("SIFT Image"), None, False)
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        output_layer_path = self.parameterAsOutputLayer(parameters, self.SIFT_IMAGE, context)

        # Get input raster path
        input_raster_path = input_raster.source()

        # Read input raster using rasterio
        with rasterio.open(input_raster_path) as src:
            img = src.read(1)  # Read the first band
            #print(type(img))

        # Create SIFT object
        sift = cv2.SIFT_create()
        
        # Detect keypoints
        kp = sift.detect(img, None)

        # Draw keypoints on the image
        img_with_keypoints = cv2.drawKeypoints(img, kp, None, flags=0)

        # Write the image with keypoints to the output file
        cv2.imwrite(output_layer_path, img_with_keypoints)

        return {self.SIFT_IMAGE: output_layer_path}