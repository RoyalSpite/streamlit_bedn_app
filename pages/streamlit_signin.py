import streamlit as st
from time import sleep
import random
import string
import bcrypt

# @st.cache_resource
# def get_user_query():
#     client = MongoClient({st.secrets["mongo"]["uri"]}, server_api=ServerApi('1'))
#     database = client[st.secrets["mongo"]["user"]]
#     collection = database[st.secrets["mongo"]["user"]]
    
#     return list(collection.find())

def set_auth_state(key : str, val : bool):
    st.session_state[key] = val
    
def backToLogin_callback():
    del st.session_state.usrname_valid
    del st.session_state.pswd_valid
    st.switch_page("streamlit_app.py")

st.header("ลงทะเบียน")

with st.form("signin", border=True):
    
    new_name = st.text_input(label="เพิ่มชื่อผู้ใช้", max_chars=7)
    
    if "usrname_valid" not in st.session_state:
        st.session_state.usrname_valid = False
    else:
        if (len(new_name) == 0):
            st.error("❌ กรุณากรอกชื่อผู้ใช้")
            set_auth_state("usrname_valid", False)
        else:
            if " " in new_name:
                st.error("❌ ชื่อผู้ใช้ใหม่ต้องไม่มีช่องว่าง")
                set_auth_state("usrname_valid", False)
            elif(len(list(filter(lambda user: user["username"] == new_name, st.session_state.user_set)))) > 0:
                st.error("❌ ชื่อผู้ใช้นี้มีคนใช้แล้ว")
                set_auth_state("usrname_valid", False)
            else:
                st.success("👌 ชื่อผู้ใช้นี้ สามารถใช้งานได้")
                set_auth_state("usrname_valid", True)
        
    new_pswd = st.text_input("กรอกรหัสผ่าน",type="password", max_chars=15)
    con_pswd = st.text_input("ยืนยันรหัสผ่าน",type="password", max_chars=15)
    
    if "pswd_valid" not in st.session_state:
        st.session_state.pswd_valid = False
    else:
        if (len(new_pswd) == 0):
            st.error("❌ กรุณากรอกรหัสผ่าน")
            set_auth_state("pswd_valid", False)
        else:
            if " " in new_pswd:
                st.error("❌ รหัสผ่านใหม่ต้องไม่มีช่องว่าง")
                set_auth_state("pswd_valid", False)
            elif (len(new_pswd) < 5):
                st.error("❌ รหัสผ่านควรมีความยาวมากกว่า 5 ตัวอักษร")  
                set_auth_state("pswd_valid", False)
            elif (len(con_pswd) == 0):
                st.error("❌ กรุณายืนยันรหัสผ่าน")
                set_auth_state("pswd_valid", False)    
            elif (new_pswd != con_pswd):
                st.error("❌ รหัสผ่านไม่ตรงกัน")
                set_auth_state("pswd_valid", False)
            else:
                st.success("👌 รหัสผ่านนี้สามารถใช้งานได้")
                set_auth_state("pswd_valid", True)
                
    st.form_submit_button("ยืนยัน", use_container_width=True, type="primary",
        disabled = (st.session_state.usrname_valid == st.session_state.pswd_valid == True)
    )

backToLogin = st.button("กลับสู่หน้า login", use_container_width=True,
    disabled = (st.session_state.usrname_valid == st.session_state.pswd_valid == True)                    
)

if backToLogin:
    backToLogin_callback()
    
if 'usrname_valid' in st.session_state and 'pswd_valid' in st.session_state:
    if st.session_state.usrname_valid == st.session_state.pswd_valid == True:
        # sign success
        database = st.session_state.client[st.secrets["mongo"]["col"]]
        collection = database[st.secrets["mongo"]["user"]]
        salt = bcrypt.gensalt()
        
        byte_pswd = bytes(new_pswd, 'utf-8')
        hash_password = bcrypt.hashpw(byte_pswd, salt)
        
        payload = {
            "username" : new_name,
            "password" : hash_password,
            "salt" : salt
        }
        
        collection.insert_one(payload)
        
        st.session_state.user_set = list(collection.find())
        
        st.toast("✔️ ลงทะเบียนสำเร็จ")
        sleep(1)
        backToLogin_callback()
        