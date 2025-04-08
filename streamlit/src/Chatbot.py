import streamlit as st
from snowflake.snowpark.session import Session
import json
import re

def chatbot(session:Session):

    st.subheader("Call Centre Insurance Assistant - RAG based approach")

    with st.expander("ℹ️ Instructions",expanded=True):
        st.markdown(
            """
            Enter your prompt and the app will retrieve the relevant data from the database and use it as augmented context for the LLM.
            
            **Examples that you can use:**

            1. give me the call details for the agent Quinn where the sentiment is negative in the month december 2023.

            2. Will you rate the conversation on the policy number POL345678 happened on 2023-12-09 as a first call resolution ?

            3. why is the call sentiment negative for the conversation on the policy number POL345678 happened on 2023-12-09

            4. what can be done to improve the call sentiment for the conversation on the policy number POL345678 happened on 2023-12-09

            """
        )
    

    # with open('creds.json') as f:
    #     connection_parameters = json.load(f)

    # session = Session.builder.configs(connection_parameters).create()

    def build_prompt(message):
        prompt = " "
        context = " "
        content = " "
        num_tokens = 512
        question = st.session_state.messages[-1]["content"]
        content = get_context(question)
        if model == "llama2-70b-chat":
            num_tokens = 4096 
        else:
            num_tokens = 512
        prompt += f"\"<question>\n{question}\n</question>\n" 
        prompt += f"\"<content>\n{content}\n</content>\n"
        prompt += f'''\n You are an assistant on vehicle insurance team in the Insurance Industry. 
        Do not mention anything about the chat history, nor the content provided as input in your response. 
        You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
        provide the best answer to the question embedded between the <question> and </question> tag
        and give the best answer basing your response on the content provided in between the <content> and </content> tag. Limit your answer to a maximum of {num_tokens} tokens.\"'''
        
        prompt = re.sub("'", "''", prompt)
        return prompt

    model = st.selectbox("Hello, I'm the Snowflake Cortex Vehicle Insurance AI Assistant based on Llama v2. Please choose the model you'd like to use:", options = ['llama2-70b-chat','llama2-7b-chat'])

    def get_context(question):
        sql_stmt = f''' with top_response as ( select AUDIO_DATA, vector_cosine_similarity(ct_embedding ,SNOWFLAKE.CORTEX.embed_text_768('e5-base-v2',
        '{question}')) as similarity from Audio_Call_Embedding 
        order by similarity desc limit 1) select AUDIO_DATA 
        from top_response;'''
        df = session.sql(sql_stmt).to_pandas()
        print(df['AUDIO_DATA'][0])
        return df['AUDIO_DATA'][0]

    def get_df(question):
        sql_stmt = f''' with top_response as ( select AUDIO_DATA, vector_cosine_similarity(ct_embedding ,SNOWFLAKE.CORTEX.embed_text_768('e5-base-v2',
        '{question}')) as similarity from Audio_Call_Embedding 
        order by similarity desc limit 3) 
        select AUDIO_DATA:AUDIOFILENAME::string as AudioFileName,AUDIO_DATA:CALLDATE::date as CallDate,AUDIO_DATA:CALLSENTIMENT::string  as Sentiment
        from top_response;'''
        df = session.sql(sql_stmt).to_pandas()
        return df

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


    # Initialize the chat messages history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I assist you today?"}
        ]

    # Prompt for user input and save
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

    # display the existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is not from assistant, we need to generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        # Call LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                prompt = build_prompt(st.session_state.messages)
                sql_stmt = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{prompt}') as answer"
                df = session.sql(sql_stmt).to_pandas()
                st.write(df['ANSWER'][0])
                # st.dataframe(get_df(st.session_state.messages[-1]["content"]))
                message = {"role": "assistant", "content": df['ANSWER'][0]}
                st.session_state.messages.append(message)  
