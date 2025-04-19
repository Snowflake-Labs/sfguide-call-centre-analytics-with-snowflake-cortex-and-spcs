import streamlit as st
import pandas as pd
import numpy as np
import json
# import pydeck as pdk
import datetime
import math
import time
# import seaborn as sns
# import matplotlib.pyplot as plt
import plotly.express as px

# import pyecharts.options as opts
# from pyecharts.charts import Line, Bar, EffectScatter
# from pyecharts.globals import SymbolType
from snowflake.snowpark.session import Session
import snowflake.snowpark.functions as F

from src.functions import extract_audio_info,get_topic_info,get_call_intent,mode,get_dates

def analytics_main(session:Session):
    min_date,max_date= get_dates(session)

    @st.cache_data
    def load_data(query_of_interest):
        return session.sql(query_of_interest).to_pandas()

    st.markdown('-----')
    d_col1,_,d_col2=st.columns([4,1,4])
    with d_col1:
        min_date = datetime.datetime(2023,12,1)
        s_date = st.date_input("Start date", min_date, key='s_date')
        # s_date = st.date_input("Start date",  key='s_date')
    with d_col2:
        e_date = st.date_input("End date",  key='e_date')


    st.markdown('-----')

    col1,col2=st.columns(2)

    # Get all audio details
    all_audio_calls = load_data(extract_audio_info(s_date,e_date))
    st.markdown('-----')
    with st.container(border=True):
        with col1:
            st.metric(label="Total Calls", value=all_audio_calls["DATETIME"].count())
        with col2:
            st.metric(label="Total Call Duration in Minutes", value=all_audio_calls["DURATION"].sum())
         
    col11,col22=st.columns(2)

    with st.container(border=True):
        with col11:
            topic_df = load_data(get_topic_info(s_date,e_date))
            topic_types_df = topic_df["NAME"]
            topic_counts_df = topic_df["VALUE"]
            # st.markdown("<h3 style='text-align: left; color: black;'>Unique Summary Topics</h3>", unsafe_allow_html=True)

            # st.subheader("Unique Summary Topics")
            fig = px.pie(values=topic_counts_df, names=topic_types_df,title=" ")
            fig.update_layout(legend=dict(orientation="v",yanchor = "bottom",y= 0.1, xanchor="left", x=1),title_x=0.35)
            fig.update_layout(
    annotations=[
        dict(
            x=0.33,
            y=1.28 ,  # Adjust the y value to control the space
            xref="paper",
            yref="paper",
            text="<b>Unique Summary Topics</b>",
            showarrow=False,
            font=dict(size=18, color="black",family="sans-serif"),
            )
            ]
    )
            st.plotly_chart(fig)
        with col22:
            # st.markdown("<h3 style='text-align: left; color: black;'>Unique Call Intents</h3>", unsafe_allow_html=True)

            # st.subheader("Call Intent")
            topic_df = load_data(get_call_intent(s_date,e_date))
            topic_types_df = topic_df["NAME"]
            topic_counts_df = topic_df["VALUE"]
            fig = px.pie(values=topic_counts_df, names=topic_types_df,title=" ")
            fig.update_layout(legend=dict(orientation="v",yanchor = "bottom",y= 0.1, xanchor="left", x=1),title_x=0.4)
            fig.update_layout(
    annotations=[
        dict(
            x=0.33,
            y=1.28 ,  # Adjust the y value to control the space
            xref="paper",
            yref="paper",
            text="<b>Unique Call Intents</b>",
            showarrow=False,
            font=dict(size=18, color="black",family="sans-serif"),
            )
            ]
    )
            st.plotly_chart(fig)
  

    mou_col1,mou_col2=st.columns(2)
    with mou_col1:
        df_mou=load_data(extract_audio_info(s_date,e_date))
        res=df_mou.groupby(['UPDATE_MODE','YEAR_MONTH']).agg({'REPRESENTATIVE_NAME':'count'})
        res=res.reset_index()
        res['mode']=res.apply(mode, axis=1)
        fig = px.bar(res, x='YEAR_MONTH', y='REPRESENTATIVE_NAME', color='mode', barmode='group',
             labels={'REPRESENTATIVE_NAME': 'Total Count'})

        # Update layout for multiple y-axes
        fig.update_layout(yaxis=dict(title='Total Calls', side='left'),
                        yaxis2=dict(title='Total Calls', side='right', overlaying='y'))
        fig.update_layout(
        annotations=[
            dict(
                x=0.05,
                y=1.1 ,  
                xref="paper",
                yref="paper",
                text="<b>Total Calls By Update Mode</b>",
                showarrow=False,
                font=dict(size=18, color="black",family="sans-serif"),
                )
                ]
            )
        
        st.plotly_chart(fig)

    with mou_col2:
        df_mou=load_data(extract_audio_info(s_date,e_date))
        res=df_mou.groupby(['FIRST_CALL_RESOLUTION','YEAR_MONTH']).agg({'REPRESENTATIVE_NAME':'count'})
        res=res.reset_index()
        # res['mode']=res.apply(mode, axis=1)
        fig = px.bar(res, x='YEAR_MONTH', y='REPRESENTATIVE_NAME', color='FIRST_CALL_RESOLUTION', barmode='group',
             labels={'REPRESENTATIVE_NAME': 'Total Count'})

        # Update layout for multiple y-axes
        fig.update_layout(yaxis=dict(title='Total Calls', side='left'),
                        yaxis2=dict(title='Total Calls', side='right', overlaying='y'))
        fig.update_layout(
        annotations=[
            dict(
                x=0.05,
                y=1.1 ,  
                xref="paper",
                yref="paper",
                text="<b>First Call Resolution Stats</b>",
                showarrow=False,
                font=dict(size=18, color="black",family="sans-serif"),
                )
                ]
            )
        
        st.plotly_chart(fig)
    
    st.markdown('----')

    # # Get all audio files and path
    # all_audio_calls = load_data(extract_audio_info(s_date,e_date))

    audio_files_list = all_audio_calls.loc[:, 'FILENAME'].values.tolist()
    audio_files_list.sort()

    st.subheader("Audio File Details")
    # Select the audio file name
    select_audio_file = st.selectbox("Select Audio File",audio_files_list,key='audiofile')
    
    audio_file_path = all_audio_calls.loc[all_audio_calls['FILENAME']==select_audio_file, 'FILEPATH'].values[0]
    audio_summary = all_audio_calls.loc[all_audio_calls['FILENAME']==select_audio_file, 'CALL_SUMMARY'].values[0]

    policy_number = all_audio_calls.loc[all_audio_calls['FILENAME']==select_audio_file, 'POLICY_NUMBER'].values[0]
    claim_number = all_audio_calls.loc[all_audio_calls['FILENAME']==select_audio_file, 'CLAIM_NUMBER'].values[0]

    # DF with all required fields for the selected audio file
    audio_call_info = all_audio_calls.loc[all_audio_calls['FILENAME']==select_audio_file]

    
    #This will play the audio
    st.audio(audio_file_path)


    def reset_callback():
        if "claims_clicked"  in st.session_state:
            del st.session_state['claims_clicked']

    opt_col1,opt_col2,opt_col3=st.columns(3)
    with opt_col1:
        with st.form("Summarize",border=False):
            summarize_button = st.form_submit_button("Summarize Audio",on_click=reset_callback)
    
    with opt_col2:
        with st.form("AudioDetails",border=False):
            audio_info_button = st.form_submit_button("Get Audio Details",on_click=reset_callback)
        
    if summarize_button:
        with st.container(border=True):
            st.write(audio_summary)
            st.write("\n")

    if audio_info_button:
        with st.container(border=True):
            st.dataframe(audio_call_info)
            st.write("\n")
    
    def callback():
        st.session_state["claims_clicked"] = True
    
    with opt_col3:
        if "claims_clicked" not in st.session_state:
            st.session_state["claims_clicked"] = False

        if not st.session_state["claims_clicked"]:
            with st.form("Claim Info",border=False):
                claim_button = st.form_submit_button("Get Claim Info",on_click=callback)
    

    # Display Claim related info as DF
    if  st.session_state["claims_clicked"] :
    #and (claim_number!='NONE' or claim_number!='CL_NotAvailable' ):
        with st.container(border=True):
            st.subheader("Claim Details")
            cl_df=session.table("AutoClaims").filter(F.col('ClaimID')==claim_number)
            st.dataframe(cl_df)
                        
            with st.form("Get Policy",border=False):
                st.markdown('##')
                policy_button1 = st.form_submit_button("Get Policy Info")
                if policy_button1:
                    with st.spinner("Getting Policy Info.."):
                        cl_df=session.table("AutoClaims").filter(F.col('ClaimID')==claim_number)
                        pol_df=session.table("PolicyDetails")
                        pol_number=cl_df.join(pol_df,pol_df.POLICYID==cl_df.POLICYID).select(pol_df.POLICYNUMBER).collect()[0]['POLICYNUMBER']
                        st.subheader("Policy Details")
                        st.dataframe(pol_df.filter(F.col('POLICYNUMBER')==pol_number))
                        reset_callback()


    st.markdown('##')    
    