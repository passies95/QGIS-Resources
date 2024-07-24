"""
Model exported as python.
Name : Tent Extraction
Group : idpsitemapping
With QGIS : 32814
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class TentExtraction(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('satellite_image', 'Satellite Image', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('sample_bare_areas', 'Sample Bare Areas', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Structures', 'Structures', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(26, model_feedback)
        results = {}
        outputs = {}

        # Compute Soil Brightness
        alg_params = {
            'channels.blue': 3,
            'channels.green': 2,
            'channels.mir': None,
            'channels.nir': None,
            'channels.red': 1,
            'in': parameters['satellite_image'],
            'list': [18],  # Soil:BI
            'outputpixeltype': 5,  # float
            'out': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeSoilBrightness'] = processing.run('otb:RadiometricIndices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Sample Soil BI
        alg_params = {
            'COLUMN_PREFIX': 'BI',
            'INPUT': parameters['sample_bare_areas'],
            'RASTERCOPY': outputs['ComputeSoilBrightness']['out'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SampleSoilBi'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # split raster bands
        # Split the Raster Image into Single Bands
        alg_params = {
            'GRASS_RASTER_FORMAT_META': '',
            'GRASS_RASTER_FORMAT_OPT': '',
            'GRASS_REGION_CELLSIZE_PARAMETER': 0,
            'GRASS_REGION_PARAMETER': None,
            'input': parameters['satellite_image'],
            'blue': QgsProcessing.TEMPORARY_OUTPUT,
            'green': QgsProcessing.TEMPORARY_OUTPUT,
            'red': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SplitRasterBands'] = processing.run('grass7:r.rgb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # compute g
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '"\'Green\' from algorithm \'split raster bands\'@1" /  ( "\'Red\' from algorithm \'split raster bands\'@1" + "\'Green\' from algorithm \'split raster bands\'@1" + "\'Blue\' from algorithm \'split raster bands\'@1" ) ',
            'EXTENT': None,
            'LAYERS': [outputs['SplitRasterBands']['red'],outputs['SplitRasterBands']['green'],outputs['SplitRasterBands']['blue']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeG'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Bare Areas Statistics
        alg_params = {
            'FIELD_NAME': 'BI1',
            'INPUT_LAYER': outputs['SampleSoilBi']['OUTPUT']
        }
        outputs['BareAreasStatistics'] = processing.run('qgis:basicstatisticsforfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # compute r
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '"\'Red\' from algorithm \'split raster bands\'@1" /  ( "\'Red\' from algorithm \'split raster bands\'@1" + "\'Green\' from algorithm \'split raster bands\'@1" + "\'Blue\' from algorithm \'split raster bands\'@1" ) ',
            'EXTENT': None,
            'LAYERS': [outputs['SplitRasterBands']['red'],outputs['SplitRasterBands']['green'],outputs['SplitRasterBands']['blue']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeR'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # compute f3 part a
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '("\'Green\' from algorithm \'split raster bands\'@1" -  min("\'Red\' from algorithm \'split raster bands\'@1","\'Blue\' from algorithm \'split raster bands\'@1"))',
            'EXTENT': None,
            'LAYERS': [outputs['SplitRasterBands']['red'],outputs['SplitRasterBands']['green'],outputs['SplitRasterBands']['blue']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeF3PartA'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # compute absolute difference Green
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': 'abs("\'Output\' from algorithm \'compute g\'@1" - "\'Green\' from algorithm \'split raster bands\'@1")',
            'EXTENT': outputs['SplitRasterBands']['green'],
            'LAYERS': [outputs['SplitRasterBands']['green'],outputs['ComputeG']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeAbsoluteDifferenceGreen'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Compute Bare Areas
        alg_params = {
            'INPUT': outputs['ComputeSoilBrightness']['out'],
            'MAXIMUM_VALUE': outputs['BareAreasStatistics']['THIRDQUARTILE'],
            'MINIMUM_VALUE': outputs['BareAreasStatistics']['MIN'],
            'CLASSIFIED_RASTER': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeBareAreas'] = processing.run('script:rasterclassificationusingcomputedranges', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # compute absolute difference Red
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': 'abs("\'Output\' from algorithm \'compute r\'@1" - "\'Red\' from algorithm \'split raster bands\'@1")',
            'EXTENT': outputs['SplitRasterBands']['red'],
            'LAYERS': [outputs['SplitRasterBands']['red'],outputs['ComputeR']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeAbsoluteDifferenceRed'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # compute f3 part b
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': '( ("\'Output\' from algorithm \'compute f3 part a\'@1" < 0 )  * 0) +  (( "\'Output\' from algorithm \'compute f3 part a\'@1">= 0) * "\'Output\' from algorithm \'compute f3 part a\'@1")',
            'EXTENT': None,
            'LAYERS': outputs['ComputeF3PartA']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeF3PartB'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # compute f1 b
        alg_params = {
            'CELLSIZE': 0,
            'CRS': None,
            'EXPRESSION': ' ( "\'Output\' from algorithm \'compute absolute difference Red\'@1" + "\'Output\' from algorithm \'compute absolute difference Green\'@1" )  / 2',
            'EXTENT': None,
            'LAYERS': [outputs['ComputeAbsoluteDifferenceRed']['OUTPUT'],outputs['ComputeAbsoluteDifferenceGreen']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeF1B'] = processing.run('qgis:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # f1 layer statistics
        alg_params = {
            'BAND': 1,
            'INPUT': outputs['ComputeF1B']['OUTPUT']
        }
        outputs['F1LayerStatistics'] = processing.run('native:rasterlayerstatistics', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # f3 layer statistics
        alg_params = {
            'BAND': 1,
            'INPUT': outputs['ComputeF3PartB']['OUTPUT']
        }
        outputs['F3LayerStatistics'] = processing.run('native:rasterlayerstatistics', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Invert BareAreas
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '',
            'FORMULA': '1-A',
            'INPUT_A': outputs['ComputeBareAreas']['CLASSIFIED_RASTER'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 0,  # Byte
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['InvertBareareas'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Normalize f1
        alg_params = {
            'BAND': 1,
            'FUZZYHIGHBOUND': outputs['F1LayerStatistics']['MAX'],
            'FUZZYLOWBOUND': outputs['F1LayerStatistics']['MIN'],
            'INPUT': outputs['ComputeF1B']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NormalizeF1'] = processing.run('native:fuzzifyrasterlinearmembership', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Normalize f3
        alg_params = {
            'BAND': 1,
            'FUZZYHIGHBOUND': outputs['F3LayerStatistics']['MAX'],
            'FUZZYLOWBOUND': outputs['F3LayerStatistics']['MIN'],
            'INPUT': outputs['ComputeF3PartB']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NormalizeF3'] = processing.run('native:fuzzifyrasterlinearmembership', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Compute f1 Threshold
        alg_params = {
            'INPUT': outputs['NormalizeF1']['OUTPUT']
        }
        outputs['ComputeF1Threshold'] = processing.run('script:computethresholdwithotsu', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Segment f1
        alg_params = {
            'Adaptive Method': 0,  # gaussian
            'Block Size': outputs['ComputeF1Threshold']['OUTPUT_THRESHOLD'],
            'Invert Image': False,
            'Modal Blurring': 0,
            'Percent': 0.05,
            'Raster': outputs['NormalizeF1']['OUTPUT'],
            'Thresholding Method': 0,  # otsu
            'Output Raster': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SegmentF1'] = processing.run('script:segmentationusingthresholding', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Compute f3 Threshold
        alg_params = {
            'INPUT': outputs['NormalizeF3']['OUTPUT'],
            'OUTPUT_HTML': None
        }
        outputs['ComputeF3Threshold'] = processing.run('script:computethresholdwithotsu', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Segment f3
        alg_params = {
            'Adaptive Method': 0,  # gaussian
            'Block Size': outputs['ComputeF3Threshold']['OUTPUT_THRESHOLD'],
            'Invert Image': False,
            'Modal Blurring': 0,
            'Percent': 0.05,
            'Raster': outputs['NormalizeF3']['OUTPUT'],
            'Thresholding Method': 0,  # otsu
            'Output Raster': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SegmentF3'] = processing.run('script:segmentationusingthresholding', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Compute Built Areas
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '',
            'FORMULA': 'logical_and(A==1,B==1)*0*A+logical_and(A==1,B==0)',
            'INPUT_A': outputs['SegmentF3']['Output Raster'],
            'INPUT_B': outputs['SegmentF1']['Output Raster'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 0,  # Byte
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ComputeBuiltAreas'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Built Up Soils Difference
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '',
            'FORMULA': 'A*B',
            'INPUT_A': outputs['ComputeBuiltAreas']['OUTPUT'],
            'INPUT_B': outputs['InvertBareareas']['OUTPUT'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 0,  # Byte
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BuiltUpSoilsDifference'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # IDP Camp Binary
        alg_params = {
            'backval': 0,
            'channel': 1,
            'filter': 'opening',
            'foreval': 1,
            'in': outputs['BuiltUpSoilsDifference']['OUTPUT'],
            'outputpixeltype': 5,  # float
            'structype': 'box',
            'xradius': 1,
            'yradius': 1,
            'out': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['IdpCampBinary'] = processing.run('otb:BinaryMorphologicalOperation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Polygonize Structures
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['IdpCampBinary']['out'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonizeStructures'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Extract by attribute
        alg_params = {
            'FIELD': 'DN',
            'INPUT': outputs['PolygonizeStructures']['OUTPUT'],
            'OPERATOR': 0,  # =
            'VALUE': '1',
            'OUTPUT': parameters['Structures']
        }
        outputs['ExtractByAttribute'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Structures'] = outputs['ExtractByAttribute']['OUTPUT']
        return results

    def name(self):
        return 'Tent Extraction'

    def displayName(self):
        return 'Tent Extraction'

    def group(self):
        return 'idpsitemapping'

    def groupId(self):
        return 'idpsitemapping'

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Algorithmn is implemented based on the procedure defined in the paper titled https://www.researchgate.net/publication/360952641_A_BUILDING_CHANGE_DETECTION_METHOD_BASED_ON_A_SINGLE_ALS_POINT_CLOUD_AND_A_HRS_IMAGE</p></body></html></p>
<h2>Input parameters</h2>
<h3>Satellite Image</h3>
<p>An RGB color channel Satellite Imagery to be used for classifiication. Due to the processing time,smaller tiles are preffered for efficient processing.</p>
<h3>Sample Bare Areas</h3>
<p>A point layer containing bare areas that have been sampled representatively across the image to be analayzed. Given the image variablity, bare areas with varying characterisitcs should be sampled. At least 80 points across an image. The image should not have any other attribute besides the id. Each image should have only the bare areas sampled on that specific image as there can be great variations between images and this will result to misleading information.</p>
<h2>Outputs</h2>
<h3>Structures</h3>
<p>This is apolygon layer that represents that tented areas and the structure. Some post processing should be undertaken to eliminate other structures. Use the rectanglify tool to clean the polygons and make them representative of the tents. One post processing is to compute a difference with then known IDP Camp areas. However care should be taken to only use this approach if/when the IDP camps have already been updated. If not, then a manual cleaning would be prefereable.</p>
<h2>Examples</h2>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Todo</p></body></html></p><br><p align="right">Algorithm author: Pascal Ogola</p><p align="right">Help author: Pascal Ogola</p><p align="right">Algorithm version: v1</p></body></html>"""

    def createInstance(self):
        return TentExtraction()
