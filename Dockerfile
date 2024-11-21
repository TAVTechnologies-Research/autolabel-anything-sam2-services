# For more information, please refer to https://aka.ms/vscode-docker-python
FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel
LABEL authors="ismailalpaydemir"

ARG TORCH_CUDA_ARCH_LIST="Ada"

WORKDIR /app
COPY . /app

#COPY ./meta-segment-anything-2/ ${SAM2_PATH}

# ---- Python Related ENV Variables ---- #
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV CUDA_HOME=/usr/local/cuda

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim\
    ninja-build\
    wget\
    ffmpeg \
    libavutil-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    pkg-config \
    build-essential \
    libffi-dev

# Install pip requirements
#COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN SAM2_BUILD_ALLOW_ERRORS=0 TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}  pip install -v -e  segment-anything-2/

# run model download script
RUN bash ./segment-anything-2/checkpoints/download_ckpts.sh

CMD ["python", "main.py", "--test", "0"]
#ENTRYPOINT ["/bin/bash"]


