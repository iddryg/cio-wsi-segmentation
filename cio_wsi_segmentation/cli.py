import click
from cio_wsi_segmentation.inspect_image import perform_image_inspection
from cio_wsi_segmentation.binary_segmentation import perform_binary_segmentation
from cio_wsi_segmentation.cell_segmentation import perform_cell_segmentation

@click.group()
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
@click.option('--membrane_channel', type=int, default=None, help='Channel index for membrane stain')
@click.option('--entropy_threshold', type=float, default=None, help='Optional entropy threshold, if not provided it will be automatically determined')
@click.argument('output_mask', type=click.Path(), required=True)
def binary_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, entropy_threshold, output_mask):
    """Performs binary segmentation based on an entropy threshold."""
    perform_binary_segmentation(ome_tiff, image_mpp, nuclear_channel, membrane_channel, entropy_threshold, output_mask)

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

