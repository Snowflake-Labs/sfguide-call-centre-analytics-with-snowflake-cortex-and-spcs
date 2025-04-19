import streamlit as st
import glob
import os 
from snowflake.snowpark.session import Session


def appinfo(session:Session):

    with open("./src/readme.md", 'r') as f:
        readme_line = f.readlines()
        readme_buffer = []
        # resource_files

    for line in readme_line :
        readme_buffer.append(line) 
    st.markdown(''.join(readme_buffer[:-1])) 

    result = session.sql("select current_role();").collect()
    st.markdown(f"Current role: {result[0][0]}")
    

