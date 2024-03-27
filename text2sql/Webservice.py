import logging
import sys
from fastapi import FastAPI, Request, Query
from snowflake.snowpark.session import Session
import requests
import subprocess
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch

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

logger = get_logger('text to sql')


app = FastAPI()

tokenizer = AutoTokenizer.from_pretrained("/notebooks/llm-workspace/nsql-llama-2-7B/")
peft_model_base = AutoModelForCausalLM.from_pretrained("/notebooks/llm-workspace/nsql-llama-2-7B/", load_in_8bit=True, torch_dtype=torch.bfloat16, device_map='auto')
peft_model_path="/notebooks/llm-workspace/peft-nsql_llama2_7B-checkpoint/"

model = PeftModel.from_pretrained(peft_model_base, 
                                       peft_model_path, 
                                       torch_dtype=torch.bfloat16,
                                       is_trainable=False)


@app.post("/text2sql", tags=["Endpoints"])
async def text_2_sql(request: Request):
  
   request_body = await request.json()
    
   request_body = request_body['data']
   print(request_body)
   
   return_data = []
   for index, text in request_body:
        print(text)

        logger.info(text)
    
        prompt = f"""CREATE TABLE STREAMLITAPPTABLE (
            DATETIME DATE,
            AUDIO_FILE_NAME VARCHAR(100),
            DURATION FLOAT,
            CALLTOACTION VARCHAR(16777216),
            CLAIMNUMBER VARCHAR(16777216),
            CUSTOMER VARCHAR(16777216),
            INTENT VARCHAR(16777216),
            ISSUE VARCHAR(16777216),
            POLICYNUMBER VARCHAR(16777216),
            PURPOSEOFCALL VARCHAR(16777216),
            REPRESENTATIVE VARCHAR(16777216),
            RESOLUTION VARCHAR(16777216),
            RESPONSEMODE VARCHAR(16777216),
            MODEOFUPDATE VARCHAR(16777216),
            NEXTSTEPS VARCHAR(16777216),
            CALLSENTIMENT VARCHAR(8),
            FIRSTCALLRESOLUTION VARCHAR(3)
        )

        -- Using valid SQLite, answer the following questions for the tables provided above.

        -- {text}

        SELECT"""

        model_input = tokenizer(prompt, return_tensors="pt").to("cuda")

        generated_ids = model.generate(**model_input, max_new_tokens=500)
        query=query=tokenizer.decode(generated_ids[0][len(model_input[0])-1:], skip_special_tokens=True).replace('"', "'").strip()

        return_data.append([index, query])
        
   return {"data": return_data}
