import streamlit as st
from src.audiofile_analytics import analytics_main
from src.functions import mode,extract_audio_info,get_agent_call_duration,get_call_aggregation,get_agent_call_stats,get_call_intent,get_ratio,get_sentiment_ratio,get_topic_info

session = st.connection('snowflake').session()


st.title("Audio Analytics")
analytics_main(session=session)