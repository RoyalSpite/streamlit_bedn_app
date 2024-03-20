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
    user_dict = list(filter(lambda user: user["username"] == usrname, st.session_state.user_set))
    if len(user_dict) == 0:
        st.session_state.aut_complete = False
    else:
        st.session_state.aut_complete = bcrypt.checkpw(bytes(pswr,'utf-8'), user_dict[0]['password'])

with st.form(key="Login",border=True):
    
    usrname = st.text_input("กรอกชื่อผู้ใช้")
    
    pswr = st.text_input("กรอกรหัสผ่าน", type="password")
    
    if 'aut_complete' in st.session_state:

        if len(usrname) == 0 or len(pswr) == 0:
            st.error("⚠️ กรุณากรอกชื่อ / รหัสผ่าน")
        else:
            authentication()
            if st.session_state.aut_complete == False:
                st.error("❌ ชื่อผู้ใช้ / รหัสผ่านไม่ถูกต้อง")
            else:
                st.session_state.login_usrname = usrname
                del st.session_state.user_set
                del st.session_state.aut_complete
                st.success("✔️ เข้าสู่ระบบสำเร็จ")
                sleep(1)
                st.switch_page("pages/streamlit_vis.py")
    else:
        st.session_state.aut_complete = False
    
    login_submit = st.form_submit_button("เข้าสู่ระบบ", use_container_width=True, 
        type="primary",disabled=st.session_state.aut_complete
    )
    
signin_click = st.button(
    "ลงทะเบียน", use_container_width=True, disabled=st.session_state.aut_complete
)

if signin_click:
    del st.session_state.aut_complete
    st.switch_page("pages/streamlit_signin.py")