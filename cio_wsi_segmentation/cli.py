import click
from cio_wsi_segmentation.inspect_image import perform_image_inspection
from cio_wsi_segmentation.binary_segmentation import perform_binary_segmentation
from cio_wsi_segmentation.cell_segmentation import perform_cell_segmentation

@click.group(context_settings={"help_option_names": ['-h', '--help']})
def main():
    """CLI tool for WSI segmentation"""
    pass

@main.command()
@click.argument('ome_tiff', type=click.Path(exists=True))
def inspect_image(ome_tiff):
    """Describe the OME TIFF and show its channel composition."""
    perform_image_inspection(ome_tiff)

@main.command()
@click.argument('ome_tiff', type=click.Path(exists=True))
@click.argument('image_mpp', type=float)
@click.argument('nuclear_channel', type=int)
@click.option('--membrane_channel', type=int, default=None, help='Optional channel index for membrane stain')
@click.option('--entropy_window_size_um', type=float, default=14, show_default=True, help='Size of window in which to calculate local entropy in um')
@click.option('--entropy_threshold', type=float, default=None, help='Optional entropy threshold, if not provided it will be automatically determined')
@click.option('--close_segmentation_um', type=float, default=20, show_default=True, help='Close segmentations with this window size in um')
@click.option('--erosion_expansion_um', type=float, default=5, show_default=True, help='Smooth the filled-gaps with erosion then expansion using this window size in um')
@click.option('--save_entropy_mask', is_flag=True, default=False, show_default=True, help='Optionally save the entropy mask as an output file')
@click.argument('output_mask', type=click.Path(), required=True)
def binary_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, entropy_window_size_um, entropy_threshold, close_segmentation_um, erosion_expansion_um, save_entropy_mask, output_mask):
    """Performs binary segmentation based on an entropy threshold."""
    perform_binary_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, entropy_window_size_um, entropy_threshold, close_segmentation_um, erosion_expansion_um, save_entropy_mask, output_mask)

@main.command()
@click.argument('ome_tiff', type=click.Path(exists=True))
@click.argument('image_mpp', type=float)
@click.argument('nuclear_channel', type=int)
@click.option('--membrane_channel', type=int, default=None, help='Channel index for membrane stain')
@click.argument('model_path', type=click.Path(exists=True))
@click.option('--binary_mask', type=click.Path(), default=None, help='Optional binary mask input')
@click.argument('output_segmentation_mask', type=click.Path(), required=True)
def cell_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, model_path, binary_mask, output_segmentation_mask):
    """Performs cell segmentation using a pre-trained model."""
    perform_cell_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, model_path, binary_mask, output_segmentation_mask)

if __name__ == "__main__":
    main()

