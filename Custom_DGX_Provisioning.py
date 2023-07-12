import streamlit as st
import base64
import json
import pickle
import uuid
import re

import pandas as pd

def clear_text():
    st.session_state["Namespace"] = ""
    st.session_state["Environment"] = ""
    st.session_state["Image"] = "None"
    st.session_state["CPU"] = 1
    st.session_state["Memory"] = 1
    st.session_state["GPU_40"] = 0
    st.session_state["GPU_20"] = 0
    st.session_state["Target"] = ""



st.set_page_config(page_title='Custom_DGX_Provisioning', layout = 'wide', initial_sidebar_state = 'auto')

st.markdown("""
    <h1 style='text-align: center;'>Custom_DGX_Provisioning</h1>
""", unsafe_allow_html=True)

with st.container():
    Namespace=st.text_input('Namespace',key='Namespace',placeholder="Enter namespace")
    Environment=st.text_input('Environment name',key="Environment",placeholder="Enter environment name")
    Image=st.selectbox('Pick one', ['None', 'XYZ','PQR'],key="Image")
    CPU=st.number_input('CPU', 1, 64,key="CPU")
    Memory=st.number_input('Memory', 1, 128,key="Memory")
    GPU_40=st.number_input('40GB GPU', 0,8,key="GPU_40")
    GPU_20=st.number_input('20GB GPU', 0, 1,key="GPU_20")
    Target=st.text_input('Target Port',max_chars=5,placeholder="Enter target port",key="Target" )



def Validate(input,str):
    if input=="":
        res=False
        st.error(f"{str} can't be empty")
    else:
        res=True
        if input==Target:
            if not Target.isnumeric():
                res=False
                st.error(f"{str} must be numeric")
    return res
    
        



col1, col2 = st.columns([1,17])

with col1:
    button1 = st.button("Submit")

with col2:
    button2 = st.button("Reset",on_click=clear_text)


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


def Validate_Entry(input,str):
    res=True
    if not input[0].isalpha():
        res=False
        st.error(f"{str} must be start with Alphabet and must contain only numbers(0-9), alphabet(a-z) and a special character '-'")
    else:
        for i in input:
            if not(i.isdigit() or i.isalpha() or i=='-'):
                res=False
                st.error(f"{str} must be start with Alphabet and must contain only numbers(0-9), alphabet(a-z) and a special character '-'")
                break
    return res


def Validate_range(input,str):
    res=True
    if int(input)<=1024 or int(input)>=65535:
        res=False
        st.error(f"{str} must be between 1024 and 65535")
    return res

#file_url = "/Data/Exp1.odt"


if button1:
    res1=Validate(Namespace,"Namespace")
    res12=Validate_Entry(Namespace,"Namespace")
    if res1 and res12:
        res2=Validate(Environment,"Environment name")
        res22=Validate_Entry(Environment,"Environment name")
        if res2 and res22:
            res3=Validate(Target,"Target")
            res32=Validate_range(Target,"Target")
            if res3 and res32:
                st.success("Successfully Completed")
                output=r'''THE DETAILS ARE 
1. DGX PORT FOR SSH ACCESS:31441
2. DGX PORT FOR APPLICATION ACCESS:31345
3. DGX PORT FOR JUPYTER ACCESS: 31532
4. SERVER PORT TO DEPLOY APPLICATION:6709
 
Local IP Address Of Server 192.168.12.1'''
                st.success(output)
                col1, col2 = st.columns([1,10])

                with col1:
                    Guide='Data/Exp1.pdf'
                    with open(Guide, 'rb') as f:
                        s = f.read()
                    download_button_str = download_button(s, Guide, 'Download Guide')
                    st.markdown(download_button_str, unsafe_allow_html=True)


                with col2:
                    Script='Data/Exp1.pdf'
                    with open(Script, 'rb') as f:
                        s = f.read()
                    download_button_str = download_button(s, Script, 'Download Script')
                    st.markdown(download_button_str, unsafe_allow_html=True)

