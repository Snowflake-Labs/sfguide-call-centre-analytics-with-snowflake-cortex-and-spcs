FROM nvcr.io/nvidia/pytorch:23.06-py3

# Install FFMPEG
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get -qq update \
    && apt-get -qq install --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install fastapi gunicorn uvicorn[standard] ffmpeg-python ffprobe openai-whisper snowflake-snowpark-python[pandas] 

WORKDIR /app
COPY ./ /app
CMD ["uvicorn", "webservice:app", "--host", "0.0.0.0", "--port", "9000"]
# CMD ["jupyter","lab" ,"--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root","--NotebookApp.token=''", "--NotebookApp.password=''"]

