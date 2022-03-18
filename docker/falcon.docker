FROM python:3.8.12-slim-bullseye
WORKDIR /app

# Installing the necessary libraries
RUN apt-get update && apt-get install -y \
  sudo \
  unzip \
  build-essential \
  curl \
  cmake \
  git \
  libexpat1-dev \
  libhdf5-dev \
  libjpeg-dev \
  libpython3-dev \
  libtiff5-dev \
  ninja-build \
  wget \
  vim \
  pigz \
  zlib1g-dev

RUN pip install --upgrade pip
RUN pip install scikit-build
RUN pip install cmake

WORKDIR /
RUN git clone https://github.com/LalithShiyam/FALCON.git
WORKDIR /FALCON
RUN . ./falcon_installer.sh
RUN . /root/.bashrc
