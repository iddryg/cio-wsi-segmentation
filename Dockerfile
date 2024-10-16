# Use the TensorFlow GPU base image
FROM tensorflow/tensorflow:2.8.0-gpu

LABEL custom.license="Modified Apache License 2.0"
LABEL custom.license.url="https://github.com/jason-weirather/cio-wsi-segmentation/LICENSE"

# System maintenance
RUN rm /etc/apt/sources.list.d/cuda.list && \
    rm /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    make \
    libpython3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    graphviz \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Create a writable directory for Matplotlib and Fontconfig cache
RUN mkdir -p /tmp/matplotlib && \
    mkdir -p /tmp/fontconfig && \
    chmod -R 777 /tmp/matplotlib /tmp/fontconfig

# Set environment variables for Matplotlib and Fontconfig
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV XDG_CACHE_HOME=/tmp/fontconfig

# Ensure pip installs globally for all users
RUN pip install --upgrade pip

# Clone and install the deepcell-toolbox and deepcell-tf requirements
WORKDIR /opt

RUN git clone --branch v0.12.1z https://github.com/jason-weirather/deepcell-toolbox.git /opt/deepcell-toolbox && \
    git clone --branch v0.12.6z https://github.com/jason-weirather/deepcell-tf.git /opt/deepcell-tf && \
    cd /opt/deepcell-toolbox && pip install --no-cache-dir --prefix=/usr/local . && \
    cd /opt/deepcell-tf && pip install --no-cache-dir --prefix=/usr/local .

# Clone and install seg-flow
RUN git clone https://github.com/jason-weirather/seg-flow.git /opt/seg-flow && \
    cd /opt/seg-flow && pip install --no-cache-dir --prefix=/usr/local .

# Copy your project files
ADD . /opt/cio-wsi-segmentation

# Install the cio-wsi-segmentation package globally
RUN cd /opt/cio-wsi-segmentation && pip install --no-cache-dir --prefix=/usr/local .

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

# Ensure that all installed Python programs are available to all users
ENV PATH="/usr/local/bin:${PATH}"


ENTRYPOINT ["cio-wsi-segmentation"]
