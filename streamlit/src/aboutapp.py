import streamlit as st
import glob
import os 

def appinfo():

    with open("./src/readme.md", 'r') as f:
        readme_line = f.readlines()
        readme_buffer = []
        # resource_files

    for line in readme_line :
        readme_buffer.append(line) 
    st.markdown(''.join(readme_buffer[:-1])) 
    

