import logging
import sys, os
import os
from typing import Union
from threading import Lock
import torch
import whisper


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
logger = get_logger('whisper-core')

model_name= os.getenv("ASR_MODEL", "base")
if torch.cuda.is_available():
    logger.debug(f"Running on GPU")
    model = whisper.load_model(model_name).cuda()
else:
    logger.debug(f"Running on CPU")
    model = whisper.load_model(model_name)
model_lock = Lock()

# ref : https://github.com/ahmetoner/whisper-asr-webservice/blob/main/app/openai_whisper/core.py#L20

# def duration_audio(audio):
#     input_filename = audio
#     out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", input_filename])
#     ffprobe_data = json.loads(out)
#     duration_seconds = float(ffprobe_data["format"]["duration"])
#     return duration_seconds
#     # Load the audio file
#     audio = AudioSegment.from_file(audio)

#     # Extract the duration in milliseconds
#     total_duration = len(audio)
#     # print(f"total duration of the call = {round(total_duration/1000/60,2)} seconds")

#     # return duration in mins
#     return round(total_duration/1000/60,2)

def transcribe(
    audio,
    task: Union[str, None],
    language: Union[str, None],
):
    options_dict = {"task" : task}
    if language:
        options_dict["language"] = language
    with model_lock:
        result = model.transcribe(audio, **options_dict)
    return result

def language_detection(audio):
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    with model_lock:
        _, probs = model.detect_language(mel)
    detected_lang_code = max(probs, key=probs.get)

    return detected_lang_code


