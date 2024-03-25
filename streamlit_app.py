import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from time import sleep
import bcrypt

@st.cache_resource
def init_connection():
    global img_array
    return MongoClient({st.secrets["mongo"]["uri"]}, server_api=ServerApi('1'))

if "client" not in st.session_state:
    st.session_state.client = init_connection()
    
if "user_set" not in st.session_state:
    database = st.session_state.client[st.secrets["mongo"]["col"]]
    collection = database[st.secrets["mongo"]["user"]]
    st.session_state.user_set = list(collection.find())
     
st.header("ยินดีต้อนรับเข้าสู่ระบบแจ้งเตือนและตรวจจับการรุกล้ำของรถขุด", divider='gray')
st.caption("Backhoe's Encroachment Detection and Notification System")

def authentication():
    user_dict = list(filter(lambda user: user["user_mail"] == mail_input.lower(), st.session_state.user_set))
    if len(user_dict) == 0:
        st.session_state.aut_complete = False
    else:
        st.session_state.aut_complete = bcrypt.checkpw(bytes(pswr,'utf-8'), user_dict[0]['password'])

with st.form(key="Login",border=True):
    
    mail_input = st.text_input("กรอกอีเมลล์ที่ใช้ลงทะเบียน")
    
    pswr = st.text_input("กรอกรหัสผ่าน", type="password")
    
    if 'aut_complete' not in st.session_state:
        st.session_state.aut_complete = False
    else:

        if len(mail_input) == 0 or len(pswr) == 0:
            st.error("⚠️ กรุณากรอกอีเมลล์ / รหัสผ่าน")
        else:
            authentication()
            if st.session_state.aut_complete == False:
                st.error("❌ อีเมลล์ / รหัสผ่านไม่ถูกต้อง")
            else:
                # st.session_state.login_usrname = usrname
                del st.session_state.user_set
                del st.session_state.aut_complete
                st.success("✔️ เข้าสู่ระบบสำเร็จ")
                st.session_state.login_email = str(mail_input.lower())
                sleep(1)
                st.switch_page("pages/streamlit_vis.py")
    
    login_submit = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True, 
        type="primary",disabled=st.session_state.aut_complete
    )
    
signin_click = st.button(
    "ลงทะเบียน", use_container_width=True, disabled=st.session_state.aut_complete
)

recover_click = st.button(
    "กู้คืนรหัสผ่าน", use_container_width=True, disabled=st.session_state.aut_complete
)

if signin_click:
    del st.session_state.aut_complete
    st.switch_page("pages/streamlit_signin.py")
    
if recover_click:
    del st.session_state.aut_complete
    st.switch_page("pages/streamlit_pswd_recover.py")
    