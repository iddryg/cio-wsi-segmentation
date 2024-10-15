FROM mambaorg/micromamba:1-jammy-cuda-12.6.0

# Set environment variables for NVIDIA
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

LABEL custom.license="Modified Apache License 2.0"
LABEL custom.license.url="https://github.com/jason-weirather/cio-wsi-segmentation/LICENSE"

# Copy the license file into the image
COPY LICENSE /app/LICENSE

# Install Python 3.8 in the base environment globally for all users
RUN micromamba install -n base python=3.8 git nano -c conda-forge && \
    micromamba clean --all --yes

USER root

# Add your _activate_current_env.sh to the global profile.d directory
RUN cp /usr/local/bin/_activate_current_env.sh /etc/profile.d/activate_mamba.sh && \
    chmod +x /etc/profile.d/activate_mamba.sh

# Ensure it is sourced for all users by adding it to profile.d (global for bash users)
RUN echo "source /etc/profile.d/activate_mamba.sh" >> /etc/bash.bashrc

#USER mambauser
#
## Install PyTorch with CUDA using micromamba run (so we don’t need to activate the base environment manually)
#RUN micromamba run -n base pip install \
#    torch \
#    torchvision \
#    torchaudio --extra-index-url https://download.pytorch.org/whl/cu124

# Switch to root to perform privileged operations
USER root

# Create deepcell directories and open permissions
RUN mkdir -p /opt/deepcell-toolbox && \
    chmod -R 777 /opt/deepcell-toolbox && \
    mkdir -p /opt/deepcell-tf && \
    chmod -R 777 /opt/deepcell-tf

# Create seg-flow directory and give permissions
RUN mkdir -p /opt/seg-flow && \
    chmod -R 777 /opt/seg-flow

# Switch back to the default user for micromamba
USER mambauser

# Clone and install the deepcell requirements
RUN micromamba run -n base git clone --branch v0.12.1z https://github.com/jason-weirather/deepcell-toolbox.git /opt/deepcell-toolbox && \
    micromamba run -n base git clone --branch v0.12.6z https://github.com/jason-weirather/deepcell-tf.git /opt/deepcell-tf && \
    micromamba run -n base pip install -r /opt/deepcell-toolbox && \
    micromamba run -n base pip install -r /opt/deepcell-tf

RUN micromamba run -n base git close https://github.com/jason-weirather/seg-flow.git /opt/seg-flow && \
    micromamba run -n base pip install -r /opt/seg-flow

USER root

# Copy the entire repository into the container
ADD . /opt/cio-wsi-segmentation

# Set permissions for the copied files
RUN chmod -R 777 /opt/cio-wsi-segmentation

# Set perms so mamba will run for all users
RUN mkdir -p /.cache/mamba/proc && \
    chmod -R 777 /.cache/mamba

USER mambauser
RUN cd /opt/cio-wsi-segmentation && micromamba run -n base pip install -e .

RUN mkdir -p /home/mambauser && \
    chmod -R 777 /home/mambauser

# Use the wrapper script as the entrypoint
ENTRYPOINT ["/opt/cio-wsi-segmentation/start.sh"]
