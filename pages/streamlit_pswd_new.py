import streamlit as st
import datetime as dt
import bcrypt
from time import sleep
from utils.send_email import send_email

def recover_complete_message():
    recover_time = dt.datetime.now()
    return f"""
    <html>
        <body>
            <p>ท่านได้กู้รหัสผ่านสำเร็จ</p>
            <p>เมื่อวันที่ {recover_time.strftime("%d/%m/%y")}</p>
            <p>เวลา {recover_time.strftime("%H:%M:%S")}</p>
            <p>อีเมลล์นี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
        </body>
    </html>
    """

def to_login():
    if 'pswd_valid' in st.session_state:
        del st.session_state.pswd_valid
    
    if 'query_email' in st.session_state:
        del st.session_state.query_email
    
    st.switch_page('streamlit_app.py')

def recover():
    
    mail_payload = {
        'subject' : "กู้รหัสผ่านสำเร็จ",
        'body' : recover_complete_message()
    }
    
    if send_email(st.session_state.query_email, mail_payload) == "success":
        
            database = st.session_state.client[st.secrets["mongo"]["col"]]
            collection = database[st.secrets["mongo"]["user"]]
            
            salt = bcrypt.gensalt()
            byte_pswd = bytes(new_pswd, 'utf-8')
            hash_password = bcrypt.hashpw(byte_pswd, salt)
            
            new_pswd_payload = {
                "password" : hash_password,
                "salt" : salt
            }
            
            collection.update_one(
                { "user_mail" : st.session_state.query_email }, 
                { "$set" : new_pswd_payload } 
            )
            
            st.session_state.user_set = list(collection.find())
            
            st.toast("✔️ กู้รหัสผ่านสำเร็จ")
            sleep(1)
            to_login()
            
if ('query_email' not in st.session_state):
    to_login()

with st.form("new password",border=True):
    
    new_pswd = st.text_input("กรอกรหัสผ่าน",type="password", 
                help="รหัสผ่านควรยาวมากกว่า 6 ตัวอักษร")
    
    con_pswd = st.text_input("ยืนยันรหัสผ่าน",type="password")
    
    if "pswd_valid" not in st.session_state:
        st.session_state.pswd_valid = False
    else:
        if (len(new_pswd) == 0):
            st.error("❌ กรุณากรอกรหัสผ่าน")
        else:
            if " " in new_pswd:
                st.error("❌ รหัสผ่านใหม่ต้องไม่มีช่องว่าง")
            elif (len(new_pswd) < 5):
                st.error("❌ รหัสผ่านควรมีความยาวมากกว่า 5 ตัวอักษร") 
            elif (len(con_pswd) == 0):
                st.error("❌ กรุณายืนยันรหัสผ่าน")
            elif (new_pswd != con_pswd):
                st.error("❌ รหัสผ่านไม่ตรงกัน")
            else:
                st.success("👌 รหัสผ่านนี้สามารถใช้งานได้")
                recover()
                
    st.form_submit_button("ยืนยันการแก้ไขรหัสผ่าน", use_container_width=True, type="primary")
    
with st.popover("ยกเลิกการเปลี่ยนรหัสผ่าน", use_container_width=True):
    st.markdown("ต้องการยกเลิกการกรอก OTP? ถ้าต้องการกู้รหัสผ่าน จะต้องขอรหัส OTP ใหม่")
    back_to_login = st.button("ย้อนกลับ", use_container_width=True)
    
    if back_to_login:
        back_to_login()