#!/bin/bash

# This will launch the FAST API endpoint which will allow us to access the NumbersStation/nsql-llama-2-7B model as an API

uvicorn Webservice:app --host 0.0.0.0 --port 9000