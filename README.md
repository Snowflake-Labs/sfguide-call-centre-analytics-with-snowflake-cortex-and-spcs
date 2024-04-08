# sfguide-call-centre-analytics-with-snowflake-cortex-and-spcs

## Overview

In this guide we will build a Call Centre Analytics solution built for analyzing insurance call center audio files. Leveraging Snowflake features like cortex, large language model running in Snowpark containers, we transcribes text and duration from audiofile,extracts essential information such as Customer details, Agent interactions, Sentiment analysis, Summary, Resolution from each audio call to name a few. Here are key highlights and features of the solution :

* Whisper running in Snowpark Containers to Extract Text and Duration of the call from the audio files.

* Using Cortex LLM functions for diarization to identify customer and representative.

* Snowpark and Cortext LLM function to summarize and extract various information from call conversation.

* Using Cortex Vector Search and Embedding to store embedding in Vector Type.

* LLM model fine tuned for SQL queries running in SPCS for converting natural language to SQL query.

* Streamlit APP which has a dashboard for audio analytics, chatbot on your data using RAG based approach. Also a Text2SQL chatbot for generating SQL queries and executing them from natural language input text.

## Step-By-Step Guide

For prerequisites, environment setup, step-by-step guide and instructions, please refer to the [QuickStart Guide](https://quickstarts.snowflake.com/guide/call_centre_analytics_with_snowflake_cortex_and_spcs/index.html).
