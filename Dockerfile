FROM mambaorg/micromamba:1-jammy-cuda-11.8.0

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

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    libpython3-dev

# Add your _activate_current_env.sh to the global profile.d directory
RUN cp /usr/local/bin/_activate_current_env.sh /etc/profile.d/activate_mamba.sh && \
    chmod +x /etc/profile.d/activate_mamba.sh

# Ensure it is sourced for all users by adding it to profile.d (global for bash users)
RUN echo "source /etc/profile.d/activate_mamba.sh" >> /etc/bash.bashrc

# Create a writable directory for Matplotlib and Fontconfig cache
RUN mkdir -p /tmp/matplotlib && \
    mkdir -p /tmp/fontconfig && \
    chmod -R 777 /tmp/matplotlib /tmp/fontconfig

# Set environment variables for Matplotlib and Fontconfig
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV XDG_CACHE_HOME=/tmp/fontconfig

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
    cd /opt/deepcell-toolbox && micromamba run -n base pip install . && \
    cd /opt/deepcell-tf && micromamba run -n base pip install .

RUN micromamba install -y -n base -c conda-forge opencv=4.10.0 py-opencv

RUN micromamba run -n base git clone https://github.com/jason-weirather/seg-flow.git /opt/seg-flow && \
    cd /opt/seg-flow && micromamba run -n base pip install .

USER root

# Copy the entire repository into the container
ADD . /opt/cio-wsi-segmentation

# Create Models directories and extract the models into their respective folders
RUN mkdir -p /Models/7 /Models/8 /Models/9 && \
    tar -xzf /opt/cio-wsi-segmentation/Models/MultiplexSegmentation-7.tar.gz -C /Models/7 && \
    rm /opt/cio-wsi-segmentation/Models/MultiplexSegmentation-7.tar.gz && \
    tar -xzf /opt/cio-wsi-segmentation/Models/MultiplexSegmentation-8.tar.gz -C /Models/8 && \
    rm /opt/cio-wsi-segmentation/Models/MultiplexSegmentation-8.tar.gz && \
    tar -xzf /opt/cio-wsi-segmentation/Models/MultiplexSegmentation-9.tar.gz -C /Models/9 && \
    rm /opt/cio-wsi-segmentation/Models/MultiplexSegmentation-9.tar.gz && \
    chmod -R 755 /Models

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
