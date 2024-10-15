from segflow import OMETiffHelper

def perform_image_inspection(ome_tiff):
    """
    Inspect an OME tiff and show its channels.
    
    Parameters:
        ome_tiff (str): Path to the input OME-TIFF file.
    """
    with OMETiffHelper(ome_tiff) as ome:
        print(ome)
