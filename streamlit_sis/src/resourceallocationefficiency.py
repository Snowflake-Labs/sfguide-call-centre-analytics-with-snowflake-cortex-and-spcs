import streamlit as st
from snowflake.snowpark.session import Session
import json
import datetime
from snowflake.snowpark.session import Session
import snowflake.snowpark.functions as F

from streamlit_echarts import st_echarts

from decimal import *

from snowflake.snowpark.types import DecimalType

import plotly.graph_objects as go

from src.functions import get_agent_call_duration,get_sentiment_ratio
import pandas as pd



# connection_parameters = json.load(open('connection.json'))

    # session = 
# if "snowpark_session" not in st.session_state:
#     session = Session.builder.configs(connection_parameters).create()
# else:
#     session = st.session_state.snowpark_session



def main(session:Session):
    @st.cache_data
    def load_data(query_of_interest):
        return session.sql(query_of_interest).to_pandas()

    d_col1,_,d_col2=st.columns([4,1,4])
    with d_col1:
        min_date = datetime.datetime(2023,11,1)
        # s_date = st.date_input("Start date", min_value=min_date, max_value=max_date,key='s_date')
        s_date = st.date_input("Start date", value=datetime.date(2023, 10, 1), key='s_date')
    with d_col2:
        e_date = st.date_input("End date", key='e_date')
    # st.markdown('----')
    st.markdown('-----')


    col1,col2=st.columns(2)
    # st.title("Cortex Call Centre Insurance Assistant")
    with col1:
        df = load_data(get_agent_call_duration(s_date,e_date))
        
        # Create a title using st.subheader
        st.subheader("Average Handle Time (AHT)")
        
        # Create a bar chart using native Streamlit component
        chart_df = pd.DataFrame({
            'Agent': df['AGENT'],
            'Duration (mins)': df['TOTAL_DURATION_MINS']
        }).set_index('Agent')
        
        st.bar_chart(chart_df, height=500)
        """
        df= load_data(get_agent_call_duration(s_date,e_date))

        options = {
        "title": {"text":"Average Handle Time (AHT)",
                "textAlign":"left",
                "padding":[1,10,1,300],
                "textStyle":{"fontFamily": "sans-serif"}
                },
        "xAxis": {
            "type": "category",
            "data": df['AGENT'].to_list(),
            "name":"Agent Name",
            "nameLocation":"middle",
            "nameGap": 35,
            "nameTextStyle": {"fontWeight":"bold"}
        },
        "yAxis": {"type": "value","name":"Duration in Mins",
                "nameLocation":"middle",
                "nameGap": 35,
                "nameTextStyle": {"fontWeight":"bold"}
                },
        "series": [{"data": df['TOTAL_DURATION_MINS'].to_list(), "type": "bar"}],
        }
        st_echarts(options=options, height="500px")

        # st.bar_chart(df)
        """

    with col2:
        df_ratio = load_data(get_sentiment_ratio(s_date, e_date))
        
        # Create a title using st.subheader for consistency
        st.subheader("Sentiment Analysis by Month")
        
        # Create an improved plotly figure
        fig = go.Figure()
        
        # Add traces with better colors and styling
        fig.add_trace(go.Bar(
            x=df_ratio['YEARMONTH'], 
            y=df_ratio['POSITIVE_SENTIMENT_COUNT'],
            name='Positive',
            marker_color='#4CAF50',  # Green for positive
            hovertemplate='<b>%{x}</b><br>Positive: %{y}<extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=df_ratio['YEARMONTH'], 
            y=df_ratio['NEGATIVE_SENTIMENT_COUNT'],
            name='Negative',
            marker_color='#FF5252',  # Red for negative
            hovertemplate='<b>%{x}</b><br>Negative: %{y}<extra></extra>'
        ))
        
        # Clean up the layout with better proportions
        fig.update_layout(
            barmode='group',
            height=500,
            margin=dict(l=40, r=40, t=10, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            xaxis_title="Month",
            yaxis_title="Number of Calls",
            hovermode="x",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Add a helpful annotation or tooltip if data is limited
        if len(df_ratio) <= 1:
            fig.add_annotation(
                text="Limited data available for selected date range",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                font=dict(size=14)
            )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Optionally add insights beneath the chart
        if not df_ratio.empty:
            total_positive = df_ratio['POSITIVE_SENTIMENT_COUNT'].sum()
            total_negative = df_ratio['NEGATIVE_SENTIMENT_COUNT'].sum()
            total_calls = total_positive + total_negative
            
            if total_calls > 0:
                positive_pct = (total_positive / total_calls) * 100
                
                st.caption(f"**Overview:** {int(total_calls)} total calls analyzed, "
                        f"{positive_pct:.1f}% positive sentiment")
        """
        df_ratio= load_data(get_sentiment_ratio(s_date,e_date))

        fig = go.Figure(data=[
            go.Bar(name='POSITIVE SENTIMENT COUNT', x=df_ratio['YEARMONTH'], y=df_ratio['POSITIVE_SENTIMENT_COUNT']),
            go.Bar(name='NEGATIVE SENTIMENT COUNT', x=df_ratio['YEARMONTH'], y=df_ratio['NEGATIVE_SENTIMENT_COUNT'])
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_xaxes(tickfont=dict(size=12))  # Adjust the font size as needed
        fig.update_yaxes(tickfont=dict(size=12))
        fig.update_layout(width=800, height=500)  # Adjust width and height as needed
        space_above_graph = - 0.5
        fig.update_layout(
        annotations=[
            dict(
                x=0.5,
                y=1.28 ,  # Adjust the y value to control the space
                xref="paper",
                yref="paper",
                text="<b>Sentiment Count</b>",
                showarrow=False,
                font=dict(size=18, color="black",family="sans-serif"),
                )
                ]
        )
        fig.update_layout(
        xaxis_title="<b>Year-Month</b>",
        yaxis_title="<b>Count of Sentiments</b>",
        xaxis=dict(
            title_font=dict(size=12, family="Arial")
        ),
        yaxis=dict(
            title_font=dict(size=12, family="Arial")
        )
    )      

        st.plotly_chart(fig)
        """


    st.markdown('-----')



