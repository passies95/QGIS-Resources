import cv2
import numpy as np

# Load segmented layers A and B
f3_path = 'C:\\Users\\pogola\\AppData\\Local\\Temp\\processing_rakDYJ\\826b4515f8b745358af3aa5f0bfac6a8\\Output Raster.tif'
f1_path = 'C:\\Users\\pogola\\AppData\\Local\\Temp\\processing_rakDYJ\\49c49a44854847d2ae1d91d913d41b70\\Output Raster.tif'
layer_A = cv2.imread(f3_path, cv2.IMREAD_GRAYSCALE)
layer_B = cv2.imread(f1_path, cv2.IMREAD_GRAYSCALE)

# Retrieve build-up areas by subtracting vegetation areas
build_up_areas = np.where((layer_A == 1) & (layer_B == 0), 1, 0).astype(np.uint8)

# Save the result
cv2.imwrite('build_up_areas.tif', build_up_areas)
