import subprocess
import execute_script
import streamlit as st
import base64
import json
import pickle
import uuid
import re

import pandas as pd

def clear_text():
    st.experimental_set_query_params(
    Namespace = "",
    Environment = "",
    #Image= "jupyter/docker:nopassword"
    CPU = 1,
    Memory = 1,
    GPU_40 = 0,
    GPU_20 = 0,
    Target = "",
    #output="",
    #flag=0,
    #return_code=0,
)


def read_values():
    urlparams = st.experimental_get_query_params()
    return {
        "Namespace": urlparams["Namespace"][0] if "Namespace" in urlparams else "",
        "Environment": urlparams["Environment"][0] if "Environment" in urlparams else "",
        #"Image": urlparams["Image"][0] if "Image" in urlparams else None,
        "CPU": int(urlparams["CPU"][0]) if "CPU" in urlparams else 1,
        "Memory": int(urlparams["Memory"][0]) if "Memory" in urlparams else 1,
        "GPU_40": int(urlparams["GPU_40"][0]) if "GPU_40" in urlparams else 0,
        "GPU_20": int(urlparams["GPU_20"][0]) if "GPU_20" in urlparams else 0,
        "Target": urlparams["Target"][0] if "Target" in urlparams else "",
        #"output": urlparams["output"][0] if "output" in urlparams else "",
        #"flag": urlparams["flag"][0] if "flag" in urlparams else 0,
        #"return_code": urlparams["return_code"][0] if "return_code" in urlparams else 0,
    }


def save_values():
    st.experimental_set_query_params(
        Namespace=str(st.session_state.Namespace),
        Environment=str(st.session_state.Environment),
        #Image=str(st.session_state.Image),
        CPU=int(st.session_state.CPU),
        Memory=str(int(st.session_state.Memory)),
        GPU_40=str(int(st.session_state.GPU_40)),
        GPU_20=str(int(st.session_state.GPU_20)),
        Target=str(st.session_state.Target),
        #output=str(output),
        #flag=int(flag),
        #return_code=int(return_code),
    )


def Validate(input,str):
    if input=="":
        res=False
        st.error(f"{str} can't be empty")
    else:
        res=True
    return res



def Validate_Entry(input,str):
    res=True
    if not input[0].isalpha():
        res=False
        st.error(f"{str} must be start with Alphabet and must contain only numbers(0-9), alphabet(a-z) and a special character (-)")
    else:
        for i in input:
            if not(i.isdigit() or i.isalpha() or i=='-'):
                res=False
                st.error(f"{str} must be start with Alphabet and must contain only numbers(0-9), alphabet(a-z) and a special character (-)")
                break
    return res

def Validate_Entry2(input,str):
    res=True
    if not input[0].isalpha() and input[0].islower():
        res=False
        st.error(f"{str} must be start with Alphabet (Only lowercase) and must contain only numbers(0-9), alphabet(Only lowercase) and a special character (-)")
    else:
        for i in input:
            if not(i.isdigit() or (i.isalpha() and i.islower()) or i=='-'):
                res=False
                st.error(f"{str} must be start with Alphabet (Only lowercase) and must contain only numbers(0-9), alphabet(Only lowercase) and a special character (-)")
                break
    return res


def Validate_range(input,str):
    res=True
    if input.isnumeric():
        if int(input)<=1024 or int(input)>=65535:
            res=False
            st.error(f"{str} must be between 1024 and 65535")
    else:
        res=False
        st.error(f"{str} must be a numeric value and in the range of (1024, 65535)")
    return res




st.set_page_config(page_title='Custom_DGX_Provisioning', layout = 'wide', initial_sidebar_state = 'auto')

st.markdown("""
    <h1 style='text-align: center;'>Custom_DGX_Provisioning</h1>
""", unsafe_allow_html=True)
values = read_values()

with st.container():
    Namespace=st.text_input('Namespace',key='Namespace',placeholder="Enter namespace",value=values["Namespace"],on_change=save_values)
    Environment=st.text_input('Environment name',key="Environment",placeholder="Enter environment name",value=values["Environment"],on_change=save_values)
    Image=st.selectbox('Image', ['nvcr.io/nvidia/pytorch:nopassword'],key="Image")
    CPU=st.number_input('CPU', 1, 64,key="CPU",value=values["CPU"],on_change=save_values)
    Memory=st.number_input('Memory', 1, 128,key="Memory",value=values["Memory"], on_change=save_values)
    GPU_40=st.number_input('40GB GPU', 0,8,key="GPU_40",value=values["GPU_40"], on_change=save_values)
    GPU_20=st.number_input('20GB GPU', 0, 1,key="GPU_20",value=values["GPU_20"], on_change=save_values)
    Target=st.text_input('Target Port',max_chars=5,placeholder="Enter target port",key="Target" ,value=values["Target"] or "",on_change=save_values)
    
        

#output=values["output"]
#flag=values["flag"]
#return_code=values["return_code"]




col1, col2 = st.columns([1,10])

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





if button1:
    res1=Validate(Namespace,"Namespace")
    if res1:
        res12=Validate_Entry(Namespace,"Namespace")
        if res12:
                res2=Validate(Environment,"Environment name")
                if res2:
                    res22=Validate_Entry2(Environment,"Environment name")
                    if res22:
                        res3=Validate(Target,"Target")
                        if res3:
                            res32=Validate_range(Target,"Target")
                            if res32:
                                return_code,stdout,stderr=execute_script.execute(Namespace,Environment,Image,str(CPU),str(Memory),str(GPU_40),str(GPU_20),Target)
                                if return_code==0:
                                    
                                    output=stdout.decode()
                                    st.success(output)
                                    col1, col2 = st.columns([1,8])

                                    with col1:
                                        Guide='Unsupervised-documentation.zip'
                                        with open(Guide, 'rb') as f:
                                            s = f.read()
                                        download_button_str = download_button(s, Guide, 'Download Guide')
                                        st.markdown(download_button_str, unsafe_allow_html=True)


                                    with col2:
                                        Script='DGX_tunnel_port_script.sh'
                                        with open(Script, 'rb') as f:
                                            s = f.read()
                                        download_button_str = download_button(s, Script, 'Download Script')
                                        st.markdown(download_button_str, unsafe_allow_html=True)
                                elif return_code==1:
                                    output=stderr.decode()
                                    st.error(output)
                                #save_values()
                                #flag=1
#flag=0
