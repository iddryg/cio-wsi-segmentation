import numpy as np
import tifffile

from segflow import OMETiffHelper, SegFlow
from segflow.image_processing_methods import EntropyImageProcessingMethod

def perform_binary_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, entropy_threshold, output_mask):
    """
    Performs binary segmentation using entropy thresholding.
    
    Parameters:
        ome_tiff (str): Path to the input OME-TIFF file.
        image_mpp (float): Image micron per pixels measurement.
        nuclear_channel (int): Index of the channel containing the nuclear stain.
        membrane_channel (int): Index of the channel containing the membrane stain (optional).
        entropy_threshold (float): Optional entropy threshold value.
        output_mask (str): Path to save the binary mask and entropy mask as a TIFF file.
    """
    segmenter = SegFlow(tile_size=512, stride=256)

    # Load the OME-TIFF
    with OMETiffHelper(ome_tiff) as ome:
        if membrane_channel is not None:
            segmenter.load_numpy_arrays(nuclear=ome.get_channel_data_by_index(0),membrane=ome.get_channel_data_by_index(0))
        else:
            segmenter.load_numpy_arrays(nuclear=ome.get_channel_data_by_index(0))

    segmenter.normalize_image()

    tiled_image = segmenter.extract_raw_tiles()
    print(tiled_image.shape)

    entropy_window_size = int(round(14/image_mpp))
    print(f"Entropy Window Size: {entropy_window_size}")    

    eipm = EntropyImageProcessingMethod(image_mpp, entropy_window_size_px=int(round(14/image_mpp)), downscale_factor=1)
    entropy_tiles = eipm.run_image_processing(tiled_image)
    entropy_image = entropy_tiles.combine_tiles(crop=True,method="average")

    if entropy_threshold is None:
         entropy_threshold = entropy_image.determine_threshold()
    print(f"Threshold: {entropy_threshold}")

    # erosion/expansion
    erosion_expansion_px = int(round(11.2/image_mpp))
    print(f"Dilate/Erode: {erosion_expansion_px}")
    binary_mask = entropy_image.apply_threshold(entropy_threshold).\
        dilate_segmentation(erosion_expansion_px).\
        erode_segmentation(erosion_expansion_px)

    # Save both masks to a TIFF file with custom descriptions
    with tifffile.TiffWriter(output_mask) as tif:
        # Save binary mask as uint8 with LZW compression and description including threshold
        binary_description = f"processed_image_mask (Threshold: {entropy_threshold})"
        tif.write(binary_mask, photometric='minisblack', compression='lzw', description=binary_description)

        # Save entropy image as float32 with LZW compression and description
        tif.write(entropy_image.astype(np.float32), photometric='minisblack', compression='lzw', description='entropy_mask')

    print(f"Binary and entropy masks saved to {output_mask}")
