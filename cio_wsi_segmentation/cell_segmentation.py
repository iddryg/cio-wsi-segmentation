import numpy as np
import tifffile
from tqdm import tqdm

from segflow import OMETiffHelper, SegFlow, SegmentationImage, SegmentationPatchTiledImage
from segflow.image_processing_methods import EntropyImageProcessingMethod

from tensorflow.keras.models import load_model

def perform_cell_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, model_path, binary_mask, output_segmentation_mask):
    """
    Performs binary segmentation using entropy thresholding.
    
    Parameters:
        ome_tiff (str): Path to the input OME-TIFF file.
        image_mpp (float): Image micron per pixels measurement.
        nuclear_channel (int): Index of the channel containing the nuclear stain.
        membrane_channel (int): Index of the channel containing the membrane stain (optional).
        model_path (str): Path to the model.
        binary_mask (str): Optional path to the binary mask.
        output_segmentation_mask (str): Path to save the segmentation mask as a TIFF file.
    """
    #segmenter = SegFlow(tile_size=512, stride=256)
    segmenter = SegFlow(tile_size=(512,512), stride=(256,256))

    # Load the OME-TIFF
    with OMETiffHelper(ome_tiff) as ome:
        if membrane_channel is not None:
            segmenter.load_numpy_arrays(nuclear=ome.get_channel_data_by_index(0),membrane=ome.get_channel_data_by_index(0))
        else:
            segmenter.load_numpy_arrays(nuclear=ome.get_channel_data_by_index(0))

    segmenter.normalize_image()

    tiled_image = segmenter.extract_raw_tiles()
    print(tiled_image.shape)


    # Execute deepcell
    batch_size = 128   # Number of tiles to process in each batch; adjust based on system memory

    from deepcell.applications import Mesmer

    from segflow.segmentation_methods import GenericSegmentationMethod
    class MesmerSegmentationMethod(GenericSegmentationMethod):
        def __init__(self,image_mpp):
            super().__init__(image_mpp)
            self.app = Mesmer(model=load_model(model_path))
        def _run_segmentation(self,tiles, batch_size = batch_size):
            segmentation_tiles = []
            for i in tqdm(range(0, len(tiles), batch_size),desc=f"Batches of ({batch_size})",total = (len(tiles) - 1) // batch_size + 1):
                batch_tiles = tiles[i:i+batch_size]
                preds = self.app.predict(batch_tiles, image_mpp=self.image_mpp)
                segmentation_tiles.extend(preds)
                #print(f"     Processed batch {i // batch_size + 1}/{(len(tiles) - 1) // batch_size + 1}\r")
            segmentation_tiles = np.array(segmentation_tiles)
            return segmentation_tiles

    mesmethod = MesmerSegmentationMethod(image_mpp)
    segmentation_tiles = mesmethod.run_segmentation(tiled_image)
    print(segmentation_tiles.shape)

    segmented_image = segmentation_tiles.\
        high_confidence_tile_filter(64).\
        combine_tiles(iou_threshold=0.9,crop=True).\
        randomize_segmentation()

    if binary_mask is not None:
        with tifffile.TiffFile(binary_mask) as tif:
            # Extract the description and image of the first series (first page)
            first_description = tif.pages[0].description
            print(f"Applying mask: {first_description}")
            binary_image = SegmentationImage(tif.pages[0].asarray())
            segmented_image = segmented_image.apply_binary_mask(binary_image,method="centroid_overlap")

    spti = SegmentationPatchTiledImage.from_image(segmented_image, bbox_size = (128,128))
    print(spti.shape)
    spti = spti.isolate_center_labels()
    print(spti.shape)
    cleaned = spti.remove_disjointed_pixels()
    print(cleaned.shape)


    #filter size
    filter_size = int(round(14/image_mpp))
    print(f"Filter size: {filter_size}")
    small_labels = cleaned.find_patches_with_small_labels(filter_size)
    cleaned = cleaned.drop_labels(small_labels)
    print(cleaned.shape)

    missing_labels = cleaned.find_patches_with_missing_labels()
    cleaned = cleaned.drop_labels(missing_labels).isolate_center_labels()
    print(cleaned.shape)

    segmented_image = cleaned.combine_tiles(method='all_labels')

    # Save both masks to a TIFF file with custom descriptions
    with tifffile.TiffWriter(output_segmentation_mask) as tif:
        
        # If binary_mask is None, create a mask of ones with the same shape as the segmentation image
        if binary_mask is None:
            binary_image = SegmentationImage(np.ones_like(segmented_image, dtype=np.uint8))
        
        # Save binary mask as uint8 with LZW compression and description "binary_image"
        binary_description = "processed_image_mask"
        tif.write(binary_image.astype(np.uint8), photometric='minisblack', compression='lzw', description=binary_description)

        # Save segmentation mask as uint32 with LZW compression and description "segmented_image"
        segmentation_description = "segmented_image_mask"
        tif.write(segmented_image.astype(np.uint32), photometric='minisblack', compression='lzw', description=segmentation_description)

    print(f"Binary and segmentation masks saved to {output_segmentation_mask}")
