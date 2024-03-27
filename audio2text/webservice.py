import logging
import sys
import numpy as np
import ffmpeg
from fastapi import FastAPI, Request, Query
from whisper import tokenizer
from openai_whisper.core import transcribe, language_detection
from snowflake.snowpark.session import Session
import requests
import subprocess
import json


# Logging
def get_logger(logger_name):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG)
   handler = logging.StreamHandler(sys.stdout)
   handler.setLevel(logging.DEBUG)
   handler.setFormatter(
      logging.Formatter(
      '%(name)s [%(asctime)s] [%(levelname)s] %(message)s'))
   logger.addHandler(handler)
   return logger
logger = get_logger('whisper-fast-api')

LANGUAGE_CODES=sorted(list(tokenizer.LANGUAGES.keys()))

app = FastAPI()

@app.post("/audio-duration", tags=["Endpoints"])
async def audio_duration(request: Request):
   request_body = await request.json()
   request_body = request_body['data']
   return_data = []
   for index, audio_file in request_body:
      input_filename = audio_file
      out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", input_filename])
      ffprobe_data = json.loads(out)
      duration_seconds = float(ffprobe_data["format"]["duration"])
      return_data.append([index, { "call_duration_seconds": duration_seconds }])
   return {"data": return_data}

@app.post("/asr", tags=["Endpoints"])
async def asr(request: Request):
   request_body = await request.json()
   logger.info(f"Value of the json -> {request_body}")
   request_body = request_body['data']
   return_data = []
   for index, task, language, audio_file, encode in request_body:
      transcription = transcribe(load_audio(audio_file, encode), task, language)
      return_data.append([index, transcription])
   return {"data": return_data}


@app.post("/detect-language", tags=["Endpoints"])
async def detect_language(request: Request):
   request_body = await request.json()
   request_body = request_body['data']
   return_data = []
   for index, audio_file, encode in request_body:
      detected_lang_code = language_detection(load_audio(audio_file, encode))
      return_data.append([index, { "detected_language": tokenizer.LANGUAGES[detected_lang_code], "language_code" : detected_lang_code }])
   return {"data": return_data}



def load_audio(file: str, encode=True, sr: int = 16000):
   """
   Ref - https://github.com/openai/whisper/blob/main/whisper/audio.py#L140
   Open an audio file object and read as mono waveform, resampling as necessary.
   Parameters
   ----------
   file: str
      PRESIGNED_URL as described here https://docs.snowflake.com/en/sql-reference/functions/get_presigned_url
   encode: Boolean
      If true, encode audio stream to WAV before sending to whisper
   sr: int
      The sample rate to resample the audio if necessary
   Returns
   -------
   A NumPy array containing the audio waveform, in float32 dtype.
   """
   # Creating Snowpark Session
   if encode:
      try:
         # This launches a subprocess to decode audio while down-mixing and resampling as necessary.
         # Requires the ffmpeg CLI and `ffmpeg-python` package to be installed.
         out, _ = (
            ffmpeg.input("pipe:", threads=0)
            .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
            .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=requests.get(file).content)
         )
         #requests.get(file).content
      except ffmpeg.Error as e:
         raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e
   else:
      out = requests.get(file).content

   return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0
