import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from time import sleep
import bcrypt

@st.cache_resource
def init_connection():
    return MongoClient({st.secrets["mongo"]["uri"]}, server_api=ServerApi('1'))

if "client" not in st.session_state:
    st.session_state.client = init_connection()
    st.session_state.client = st.session_state.client[st.secrets["mongo"]["col"]]
     
st.header("ยินดีต้อนรับเข้าสู่ระบบตรวจจับและแจ้งเตือนการรุกล้ำของรถขุด", divider='gray')
st.caption("Backhoe's Encroachment Detection and Notification System")

def authentication():
    user_dict = list(st.session_state.client[st.secrets["mongo"]["user"]].find({
        'user_mail' : mail_input.lower()
    }))

    if len(user_dict) == 0:
        # ไม่มีอีเมล
        st.session_state.aut_complete = 1
    else:
        if bcrypt.checkpw(bytes(pswr,'utf-8'), user_dict[0]['password']) == False:
            # รหัสผ่านผิด
            st.session_state.aut_complete = 2
        else:
            if user_dict[0]['inUse'] == True:
                st.session_state.aut_complete = 3
            else:
                st.session_state.aut_complete = 0
    del user_dict

with st.container(border=True):
    
    mail_input = st.text_input("กรอกอีเมลล์")
    
    pswr = st.text_input("กรอกรหัสผ่าน", type="password")
    
    if 'aut_complete' in st.session_state:
        if len(mail_input) == 0 or len(pswr) == 0:
            st.error("⚠️ กรุณากรอกอีเมลล์ / รหัสผ่าน")
        else:
            if mail_input == st.secrets['admin']['usr'] and pswr == st.secrets['admin']['password']:
                st.warning("⚠️ เข้าสู่ระบบในฐานะแอดมิน")
                del st.session_state.aut_complete
                st.switch_page("pages/admin.py")
            elif st.session_state.aut_complete != 0:
                if st.session_state.aut_complete == 3:
                    st.error("❌ ไม่สามารถเข้าสู่ระบบได้ เนื่องจากผู้ใช้งานนี้กำลังเข้าสู่ระบบ")
                else : 
                    st.error("❌ อีเมลล์ / รหัสผ่านไม่ถูกต้อง")
            else:
                # st.session_state.login_usrname = usrname
                st.success("✔️ เข้าสู่ระบบสำเร็จ")
                # st.session_state.client[st.secrets["mongo"]["user"]].update_one(
                #     { "user_mail" : mail_input.lower() }, 
                #     { "$set" : { "inUse" : True } } 
                # )
                st.session_state.login_email = mail_input.lower()
                sleep(1)
                del st.session_state.aut_complete
                st.switch_page("pages/visualization.py")
    
    login_submit = st.button("เข้าสู่ระบบ", use_container_width=True, 
        type="primary", on_click=authentication
    )
    
signin_click = st.button("ลงทะเบียน", use_container_width=True)

recover_click = st.button("กู้คืนรหัสผ่าน", use_container_width=True)

if signin_click:
    if 'aut_complete' in st.session_state : del st.session_state.aut_complete
    st.switch_page("pages/signin.py")
    
if recover_click:
    if 'aut_complete' in st.session_state : del st.session_state.aut_complete
    st.switch_page("pages/pswd_recover.py")
    