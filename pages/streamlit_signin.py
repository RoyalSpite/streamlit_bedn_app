import streamlit as st
from time import sleep
import random
import string
import bcrypt
import re
from utils.send_email import send_email

def sigin_verify_message():
    return """
    <html>
        <body>
            <p>ท่านได้ลงทะเบียนเข้าสู่ระบบตรวจจับ และแจ้งเตือนการรุกล้ำของรถขุดสำเร็จ</p>
            <p>อีเมลล์นี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
        </body>
    </html>
    """

def set_auth_state(key : str, val : bool):
    st.session_state[key] = val
    
def backToLogin_callback():
    del st.session_state.email_valid
    del st.session_state.pswd_valid
    st.switch_page("streamlit_app.py")
    
def checkEmail(mail):
    return re.fullmatch(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        mail
    )
    

st.header("ลงทะเบียน")

with st.form("signin", border=True):
    
    new_mail = st.text_input(label="เพิ่มเมลล์")
    
    if "email_valid" not in st.session_state:
        st.session_state.email_valid = False
    else:
        if (len(new_mail) == 0):
            st.error("❌ กรุณากรอกเมลล์")
            set_auth_state("email_valid", False)
        else:
            if " " in new_mail:
                st.error("❌ เมลล์ต้องไม่มีช่องว่าง")
                set_auth_state("email_valid", False)
                
            elif checkEmail(new_mail) is None:
                st.error("❌ รูปแบบเมลล์ไม่ถูกต้อง")
                set_auth_state("email_valid", False)
                
            elif(len(list(filter(lambda user: user["user_mail"] == new_mail.lower(), st.session_state.user_set)))) > 0:
                st.error("❌ เมลล์นี้มีคนใช้แล้ว")
                set_auth_state("email_valid", False)
                
            else:
                st.success("👌 เมลล์นี้ สามารถใช้งานได้")
                set_auth_state("email_valid", True)
        
    new_pswd = st.text_input("กรอกรหัสผ่าน",type="password", 
                help="รหัสผ่านควรยาวมากกว่า 6 ตัวอักษร")
    
    con_pswd = st.text_input("ยืนยันรหัสผ่าน",type="password")
    
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
    
    if 'verify_fail' in st.session_state:
        if st.session_state.verify_fail:
            st.error("❌ ลงทะเบียนไม่สำเร็จ โปรดลองอีกครั้งในภายหลัง")
            
    st.form_submit_button("ยืนยัน", use_container_width=True, type="primary",
        disabled = (st.session_state.email_valid and st.session_state.pswd_valid)
    )

backToLogin = st.button("กลับสู่หน้า login", use_container_width=True,
    disabled = (st.session_state.email_valid and st.session_state.pswd_valid)                    
)

if backToLogin:
    backToLogin_callback()
    
if 'email_valid' in st.session_state and 'pswd_valid' in st.session_state:
    if st.session_state.email_valid == st.session_state.pswd_valid == True:
        # sign success
        if 'verify_fail' in st.session_state:
            del st.session_state.verify_fail

        recipient = new_mail.lower()
        mail_content = {
            'subject': "ลงทะเบียนเข้าสู่ระบบ BEDN สำเร็จ",
            'body' : sigin_verify_message()
        }
                
        if send_email(recipient, mail_content) == "success":
           
            database = st.session_state.client[st.secrets["mongo"]["col"]]
            collection = database[st.secrets["mongo"]["user"]]
            
            salt = bcrypt.gensalt()
            byte_pswd = bytes(new_pswd, 'utf-8')
            hash_password = bcrypt.hashpw(byte_pswd, salt)
            
            payload = {
                "user_mail" : recipient,
                "password" : hash_password,
                "salt" : salt
            }
            
            collection.insert_one(payload)
            st.session_state.user_set = list(collection.find())
            
            st.toast("✔️ ลงทะเบียนสำเร็จ")
            sleep(1)
            backToLogin_callback()
        
        else:
            del st.session_state.email_valid
            del st.session_state.pswd_valid
            
            st.session_state.verify_fail = True
        