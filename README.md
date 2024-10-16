# cio-wsi-segmentation

`cio-wsi-segmentation` is a command-line tool for performing whole slide image (WSI) segmentation. This tool is built to process OME-TIFF files and enables both binary segmentation (based on entropy thresholding) and cell segmentation using pre-trained models. It supports optional inputs for nuclear and membrane stains and allows for saving segmentation masks in TIFF format.

## License

This repository uses a [Modified Apache License, Version 2.0](./LICENSE). It is derived from the original work by DeepCell, which follows the terms of the same license. For any commercial use, contact [vanvalenlab@gmail.com](mailto:vanvalenlab@gmail.com).

### Citation Requirements

- **Cell Segmentation**: If you use this tool for cell segmentation, please cite the original work by Noah Greenwald:
  
  > Greenwald, N.F., Miller, G., Moen, E. et al. Whole-cell segmentation of tissue images with human-level performance using large-scale data annotation and deep learning. Nat Biotechnol 40, 555–565 (2022). https://doi.org/10.1038/s41587-021-01094-0
  
  Additionally, for the primary implementation of this tool for cell segmentation, it is recommended to use the official release of Mesmer: [https://github.com/vanvalenlab/deepcell-tf](https://github.com/vanvalenlab/deepcell-tf).
  
- **Entropy-Based Binary Segmentation**: The entropy-based binary segmentation functionality is implemented using modules from the [seg-flow repository](https://github.com/jason-weirather/seg-flow).

## Features

- **Binary Segmentation**: Perform segmentation based on local entropy thresholds, allowing for fine-grained control of window sizes and thresholds.
- **Cell Segmentation**: Use pre-trained models to segment cells in whole slide images, with options to input binary masks and specify stain channels.
- **Support for OME-TIFF**: Input images are expected to be in OME-TIFF format, which is widely used for microscopy data.
- **Dockerized Execution**: The tool can be run inside a Docker container with models pre-installed, making it easier to set up and use.

## Installation

To use `cio-wsi-segmentation`, you can run it either in a Python environment or within a Docker container.

### Running with Docker

The easiest way to get started is by using Docker. To pull and run the Docker image:

```bash
docker pull vacation/cio-wsi-segmentation:0.1.0
```

Run the container interactively or execute commands directly, passing in your files and options.

### Building the Docker Image

To build the Docker image from the source:

```bash
docker build -t cio-wsi-segmentation:latest .
```

Once built, the tool can be run using the following:

```bash
docker run --rm \
  -v /path/to/data:/data \
  -u $(id -u):$(id -g) \
  cio-wsi-segmentation:latest <command>
```

Replace `<command>` with any of the available commands listed below.

### Python Installation

To install the package in a Python environment, you can use:

```bash
pip install .
```

## Usage

`cio-wsi-segmentation` provides a set of commands for image segmentation. All commands are executed from the CLI.

### Commands

#### 1. `inspect-image`

Displays information about the channels in the input OME-TIFF file.

**Usage**:

```bash
cio-wsi-segmentation inspect-image <ome_tiff>
```

**Example**:

```bash
cio-wsi-segmentation inspect-image /path/to/sample.ome.tiff
```

#### 2. `binary-segmentation`

Performs binary segmentation based on local entropy thresholds. The entropy threshold can be determined automatically or provided as an input.

**Usage**:

```bash
cio-wsi-segmentation binary-segmentation <ome_tiff> <image_mpp> <nuclear_channel> [OPTIONS] <output_mask>
```

**Required Arguments**:
- `<ome_tiff>`: Path to the OME-TIFF file.
- `<image_mpp>`: Image micron-per-pixel resolution (float).
- `<nuclear_channel>`: Channel index for nuclear stain (integer).
- `<output_mask>`: Path to save the binary mask (TIFF file).

**Options**:
- `--membrane_channel`: Optional index for membrane stain.
- `--entropy_window_size_um`: Window size for calculating local entropy (default: 14 µm).
- `--entropy_threshold`: Custom entropy threshold (if not provided, it will be automatically determined).
- `--close_segmentation_um`: Close segmentations with this window size (default: 20 µm).
- `--erosion_expansion_um`: Smooth gaps with erosion and expansion (default: 5 µm).
- `--save_entropy_mask`: Optionally save the entropy mask (default: False).

**Example**:

```bash
cio-wsi-segmentation binary-segmentation /path/to/image.ome.tiff 0.28 0 --membrane_channel 1 --save_entropy_mask /path/to/output_mask.tiff
```

#### 3. `cell-segmentation`

Performs cell segmentation using a pre-trained model.

**Usage**:

```bash
cio-wsi-segmentation cell-segmentation <ome_tiff> <image_mpp> <nuclear_channel> <model_path> [OPTIONS] <output_segmentation_mask>
```

**Required Arguments**:
- `<ome_tiff>`: Path to the OME-TIFF file.
- `<image_mpp>`: Image micron-per-pixel resolution (float).
- `<nuclear_channel>`: Channel index for nuclear stain (integer).
- `<model_path>`: Path to the pre-trained segmentation model.
- `<output_segmentation_mask>`: Path to save the segmentation mask (TIFF file).

**Options**:
- `--membrane_channel`: Optional index for membrane stain.
- `--binary_mask`: Optional binary mask input.

**Example**:

```bash
cio-wsi-segmentation cell-segmentation /path/to/image.ome.tiff 0.28 0 /Models/7/MultiplexSegmentation --binary_mask /path/to/binary_mask.tiff /path/to/output_segmentation_mask.tiff
```

## Running with Models

The Docker image includes pre-installed models stored in the following directories:
- `/Models/7/MultiplexSegmentation`
- `/Models/8/MultiplexSegmentation`
- `/Models/9/MultiplexSegmentation`

You can specify the model to use by passing the corresponding path to the `--model_path` argument when running the `cell-segmentation` command.

## Example Workflows

### Binary Segmentation Example

1. To perform binary segmentation on an OME-TIFF image:
   ```bash
   cio-wsi-segmentation binary-segmentation /data/image.ome.tiff 0.28 0 --save_entropy_mask /data/output_binary_mask.tiff
   ```

### Cell Segmentation Example

2. To perform cell segmentation using a pre-trained model:
   ```bash
   cio-wsi-segmentation cell-segmentation /data/image.ome.tiff 0.28 0 /Models/7/MultiplexSegmentation --binary_mask /data/binary_mask.tiff /data/output_segmentation.tiff
   ```

Each model is designed for specific types of cell segmentation, and you can choose the appropriate model based on your dataset.

## Contact

For any questions, contact [Jason L Weirather](mailto:jason.weirather@gmail.com).
