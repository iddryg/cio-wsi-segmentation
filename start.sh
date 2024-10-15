#!/bin/bash

# Source the micromamba activation script
source /etc/profile.d/activate_mamba.sh

# Run cio-wsi-segmentation with the provided arguments
exec cio-wsi-segmentation "$@"
