import streamlit as st
from common.hello import say_hello
from src.aboutapp import appinfo

session = st.connection('snowflake').session()


#st.set_page_config(page_title="My App",layout='wide')
st.title("❄️ Customer Insight Analyzer ❄️ ")

appinfo(session=session)

