# QGIS-Resources
A collection of Resources to be used within QGIS. 
Resources are designed to work with QGIS 3.0 or Higher.
- To install these resources, navigate to plugins and install the QGIS Resource Sharing Plugin. Within the Qgis Resource Sharing Window, navigate to the Settings and # Add repository https://github.com/passies95/QGIS-Resources.git

# Limitations
- As the image size increases, the disk space required for processing significantly increase since intermediate results are written on computer memory and are only released once the Qgis window has been closed or terminated. However, since each run produces different temporary outputs it is not possible to know the output name at the onset hence restoring previous steps is not been provided for at this time.
For instance a Worldview image of 100000 * 100000 would have a size of approximately 50 gb on memory. Consequently this might require a storage space of approximately 600 gb to use this model. This will however be released once the processing has finalized.
- The model performs relatively poorly on sandy beaches where the soil brighteness closely resembles the brightness of built up structures. This may lead to aggregations in some other instances. However this can be fixed during post processing.

# Recommendation
- Processing should be done for image tile of approximately 20000 * 20000 or less. Besides the advantage of requiring less storage space, it also improves the model results. 
