import cv2
import numpy as np
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingOutputRasterLayer,
                       QgsProcessingParameterRasterDestination)
import rasterio

class Grabcut(QgsProcessingAlgorithm):
    """
    This script applies GrabCut segmentation to a raster layer using OpenCV.
    """

    INPUT = 'INPUT'
    MASK = 'MASK'
    CLASSIFIED_IMAGE = 'CLASSIFIED_IMAGE'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Grabcut()

    def name(self):
        return 'Grabcut'

    def displayName(self):
        return self.tr('Grabcut')

    def group(self):
        return self.tr('IDP Site Mapping')

    def groupId(self):
        return 'idpsitemapping'

    def shortHelpString(self):
        return self.tr("Grabcut")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input Raster Layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.MASK,
                self.tr('Input Mask Layer')
            )
        )
      
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.CLASSIFIED_IMAGE, self.tr("Classified Image"), None, False)
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        mask_raster = self.parameterAsRasterLayer(parameters, self.MASK, context)
        output_layer_path = self.parameterAsOutputLayer(parameters, self.CLASSIFIED_IMAGE, context)

        # Get input raster path
        input_raster_path = input_raster.source()
        mask_raster_path = mask_raster.source()

        # Read input raster using rasterio
        with rasterio.open(input_raster_path) as img_src:
            img = img_src.read(1)  # Read the first band
        
        # Read binary mask using rasterio
        with rasterio.open(mask_raster_path) as mask_src:
            mask = mask_src.read(1)  # Read the first band

        # Apply GrabCut
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        rect = (0, 0, img.shape[1], img.shape[0])
        result_mask, _, _ = cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)

        # Convert result mask to binary
        result_mask_binary = np.where((result_mask == cv2.GC_PR_BGD) | (result_mask == cv2.GC_BGD), 0, 1).astype(np.uint8)

        # Apply result mask to input image
        segmented_img = img * result_mask_binary[:, :, np.newaxis]

        # Write segmented image to output raster
        with rasterio.open(output_layer_path, 'w', **img_src.meta) as dst:
            dst.write(segmented_img, 1)

        return {self.CLASSIFIED_IMAGE: output_layer_path}