import streamlit as st
import pandas as pd
import numpy as np
import json
# import pydeck as pdk
import datetime
import math
import time
# import seaborn as sns
# import plotly.express as px

from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
import snowflake.connector


# from streamlit_echarts import st_echarts
# from streamlit_echarts import st_pyecharts
from decimal import *
from streamlit_option_menu import option_menu
# from geopy.geocoders import Nominatim
from snowflake.connector.pandas_tools import write_pandas
from snowflake.snowpark.types import DecimalType


#

import datetime

from functions import mode,extract_audio_info,get_agent_call_duration,get_call_aggregation,get_agent_call_stats,get_call_intent,get_ratio,get_sentiment_ratio,get_topic_info
from resourceallocationefficiency import main as res_main
from audiofile_analytics import analytics_main
from Chatbot import chatbot
from Text2SQLChatbot import chatbot as text_cb
from aboutapp import appinfo

import os

# from session_connectivity import create_session_object

# Environment variables below will be automatically populated by Snowflake.
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_HOST = os.getenv("SNOWFLAKE_HOST")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

# Custom environment variables
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ROLE = os.getenv("SNOWFLAKE_ROLE")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE","XS_WH")

def get_login_token():
  """
  Read the login token supplied automatically by Snowflake. These tokens
  are short lived and should always be read right before creating any new connection.
  """
  with open("/snowflake/session/token", "r") as f:
    return f.read()

def get_connection_params():

  """
  Construct Snowflake connection params from environment variables. 
  There is an issue using cortex LLM fuctions with oauth token within streamlit. Hence changed connection mode to reading from json
  """
  return json.load(open('./src/connection.json'))
  # if os.path.isfile("/snowflake/session/token"):
  #       creds = {
  #           'host': os.getenv('SNOWFLAKE_HOST'),
  #           'port': os.getenv('SNOWFLAKE_PORT'),
  #           'protocol': "https",
  #           'account': os.getenv('SNOWFLAKE_ACCOUNT'),
  #           'authenticator': "oauth",
  #           'token': open('/snowflake/session/token', 'r').read(),
  #           'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
  #           'database': os.getenv('SNOWFLAKE_DATABASE'),
  #           'schema': os.getenv('SNOWFLAKE_SCHEMA'),
  #           'client_session_keep_alive': True
  #       }
  # else:
  #       creds = {
  #           'account': os.getenv('SNOWFLAKE_ACCOUNT'),
  #           'user': os.getenv('SNOWFLAKE_USER'),
  #           'password': os.getenv('SNOWFLAKE_PASSWORD'),
  #           'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
  #           'database': os.getenv('SNOWFLAKE_DATABASE'),
  #           'schema': os.getenv('SNOWFLAKE_SCHEMA'),
  #           'client_session_keep_alive': True
  #       }
    
    
  # connection = snowflake.connector.connect(**creds)
  # return connection
    

# connection_parameters = json.load(open('./src/connection.json'))

    # session = 
if "snowpark_session" not in st.session_state:
    # session = Session.builder.configs({"connection": get_connection_params()}).create()
    session = Session.builder.configs(get_connection_params()).create()

    # session = Session.builder.configs(connection_parameters).create()
else:
    session = st.session_state.snowpark_session
session.query_tag = 'cortext_app' 

st.set_page_config(page_title="My App",layout='wide')
st.title("Customer Insight Analyzer ❄️")
 

def get_dates():
    # Getting unique dates 
    date_list=[data[0] for data in session.table('Audio_Claims_Extracted_info').select('DATETIME').sort(F.col("DATETIME"), ascending=True).distinct().collect()]
    date_list.sort()
    st_dt,ed_dt=date_list[0],date_list[-1]
    
    return (st_dt,ed_dt)

      
with st.sidebar:
    #signup = st.button("Login")
    choose_side_opt = option_menu("Supervisor Dashboard", ["About App", "Audio Analytics","Resource Allocation Efficiency" ,"Chatbot","Text2SQLBot" ],
                         icons=['browser-safari',  'card-checklist','card-checklist','card-checklist'],
                         menu_icon="snow3", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "white","font-color": "#249dda"},
        "icon": {"color": "#31c0e7", "font-size": "25px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "white"},
        "nav-link-selected": {"background-color": "7734f9"},
    }
    )

# Load & cache data
@st.cache_data
def load_data(query_of_interest):
    return session.sql(query_of_interest).to_pandas()

if choose_side_opt == "About App":
  appinfo()

if choose_side_opt == "Audio Analytics":
    
    # snowflake_environment = session.sql('SELECT current_user(), current_version()').collect()
    # Current Environment Details
    # st.write(f"Databse Name - {session.get_current_database()}")
    # st.write(f"WH Name - {session.get_current_warehouse()}")
    analytics_main(session=session)


if choose_side_opt == "Resource Allocation Efficiency":
    res_main(session=session)

if choose_side_opt == "Chatbot":
    # st.session_state.messages=[]
    # st.session_state.messages = [{"role": "assistant", "content": "Ask your question?"}]
    chatbot(session=session)

if choose_side_opt == "Text2SQLBot":
    # st.session_state.messages=[]
    # st.session_state.messages = [{"role": "assistant", "content": "Ask your question?"}]
    text_cb(session=session)