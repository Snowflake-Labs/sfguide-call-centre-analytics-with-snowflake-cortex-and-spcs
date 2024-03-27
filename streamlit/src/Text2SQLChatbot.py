import streamlit as st
from snowflake.snowpark.session import Session
import json
import re

def chatbot(session:Session):

    st.subheader("Call Centre Insurance Assistant - Text2SQL")

    with st.expander("ℹ️ Instructions",expanded=True):
        st.markdown(
            """
            You can input your question as natural language text and the chatbot will return you the output as a table ! 
            Shows you on how to use your own co-pilot from the app.
            
            **Examples that you can use:**

            1. Give me count of records for every resolution
            2. Give me rows with the claim number CLM456789
            3. Give me all rows where purpose of call like policy inquiry in the month december 2023
            4. Give the sum of callduration for every representative where the response mode is Resolved
            5. list the unique issues handled by the representatives name starting with emma in November and end of December 2023
            6. what is the sum of call duration for every representative and for every resolution

            """
        )

    def clear_chat_history():
        st.session_state.messages = [{"role": "assistant", "content": "Ask your question?"}]

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
                prompt = st.session_state.messages[-1]["content"]
                your_system_message=''' You are a sql expert and you know the schema of the table well and it is as below. Answer the SQL queries based on the below schema.
                  CREATE TABLE STREAMLITAPPTABLE (
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
                    )  '''
                #build_prompt(st.session_state.messages)
                # sql_stmt = f"SELECT SNOWFLAKE.ML.COMPLETE('{model}', '{prompt}') as answer"
                sql_stmt=f'''select text2sql('{prompt}')::string '''
                sql_stmt_qry= session.sql(sql_stmt).collect()[0][0]
                sql_stmt_qry=sql_stmt_qry.replace("'","''")
                updated_qry=f'''select SNOWFLAKE.CORTEX.COMPLETE('llama2-70b-chat',concat('<s>[INST]Replace the sql like to ilike if found in the SQL query between the tage <query> </query> and ensure the SQL query is a valid Snowflake query. 
                                                Only ouput the SQL Query and do not include the user prompt. Do not include details about the replacement .Do not provide any explaination about the modified query and output the modified query only without any detail .
                                                Do not output like The query is syntactically valid Snowflake SQL statement
                                                Some of the date based queries and prompts are as below:
                                                [/INST]
                                                For the prompt: Give me count of total calls in the month november 2023. 
                                                SQL Query: SELECT count(*) FROM STREAMLITAPPTABLE WHERE DATETIME = 2023-11-01 between 2023-11-30

                                                For the prompt : list the unique issues handled by the representative name starts with emma in the month November 2023
                                                SQL Query: select distinct issues from STREAMLITAPPTABLE where represetative ilike emma% and datetime between 2023-11-01 and 2023-11-30;

                                                For the prompt : list the unique issues handled by the representative name starts with emma in the month November and December 2023
                                                SQL Query: select distinct issues from STREAMLITAPPTABLE where represetative ilike emma% and datetime between 2023-11-01 and 2023-12-31;
                                                
                                                For the prompt : give me call details for the representative name like Ryan where the call sentiment is negative in the month November 2023
                                                SQL Query: select distinct issues from STREAMLITAPPTABLE where represetative ilike Ryan% and AND CALLSENTIMENT = ''Negative'' and datetime between 2023-11-01 and 2023-11-30;
                                               
                                                [INST] Do not provide any explaination about the modified query and output the modified query only without any detail for the query found between <query> </query> tag. If you a. If you are unable to change the SQL ouput it as Select 1; . Do not include th query tags in output. Do not include the explanation about the ilike operator or the query output', '<query>','{sql_stmt_qry}','</query>  [/INST] Answer: Sure, I would be happy to help!')) as qry'''

                df_updated=session.sql(updated_qry).to_pandas()
                # print(f"updated qry -> {updated_qry}")
                # print(f"sql_stmt_qry  -> {sql_stmt_qry}")
                
                try:
                    
                    if 1==0:
                        pass
                    # ':' in df_updated['QRY'][0]:
                    #     print(f"df_updated['QRY'][0] -> {df_updated['QRY'][0]}")
                    #     run_qry=df_updated['QRY'][0].split(':')[1].strip()
                    #     print(f'run query in : -> {run_qry}')
                    #     if ';' in run_qry:
                    #         print(run_qry)
                    #         final_qry = run_qry.split(';')[0].strip()
                    #     else: final_qry=run_qry
                    else:
                        run_qry=df_updated['QRY'][0].split('\n')[0]
                        # print(f'run query in else -> {run_qry}')
                        if ';' in run_qry:
                            print(run_qry)
                            final_qry = run_qry.split(';')[0].strip()
                        else: final_qry=run_qry
                    
                    # print('-------------final full qyery------')
                    # print(final_qry)
                    # print('------------------------- markdown query split list')
                    # print(final_qry.split('```'))
                    # print('------------------------')
                    # st.write(final_qry)
                    for idx,qy in enumerate(final_qry.split('```')):
                        if 'SELECT' in qy:
                            # print("inside loop...")
                            # print(qy)
                            # print(f'The query which is getting executed is ->  {qy}')
                            pd_df=session.sql(qy).to_pandas()
                            
                            # print(qy)
                            break

                    # pd_df=session.sql(final_qry.split('```')[0]).to_pandas()
                    
                    st.dataframe(pd_df)

                    if '```' in final_qry:
                        st.code(final_qry.split('```')[0])
                    else: 
                        st.code(final_qry)
                    # with st.form("Execute Query",border=False):
                    #     input= st.chat_input("Update your query ",key='EQ')
                    #     summarize_button = st.form_submit_button("Run")

                    # st.dataframe(get_df(st.session_state.messages[-1]["content"]))
                    message = {"role": "assistant", "content": pd_df}
                    st.session_state.messages.append(message)  
                except Exception as e:
                    st.write(f"Sorry invalid query to execute. Please change the prompt. Below is the query generated for your prompt.")
                    if '```' in final_qry:
                        st.code(final_qry.split('```'))
                    else: 
                        st.code(final_qry)