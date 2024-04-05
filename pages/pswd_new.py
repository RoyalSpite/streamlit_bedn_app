import streamlit as st
import datetime as dt
import bcrypt
from time import sleep
from utils.utils import send_email

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
    
    del st.session_state.recover_mail
    
    st.switch_page('streamlit_app.py')

def pswd_recover_confirm():
    
    if (len(new_pswd) == 0):
        st.session_state.pswd_valid = 1
    elif " " in new_pswd:
        st.session_state.pswd_valid = 2
    elif (len(new_pswd) < 5):
        st.session_state.pswd_valid = 3
    elif (len(con_pswd) == 0):
        st.session_state.pswd_valid = 4
    elif (new_pswd != con_pswd):
        st.session_state.pswd_valid = 5
    else:
        mail_payload = {
            'subject' : "noreply : กู้รหัสผ่านสำเร็จ",
            'body' : recover_complete_message()
        }
        
        if send_email(st.session_state.recover_mail, mail_payload) == "success":
        
            salt = bcrypt.gensalt()
            byte_pswd = bytes(new_pswd, 'utf-8')
            hash_password = bcrypt.hashpw(byte_pswd, salt)
            
            new_pswd_payload = {
                "password" : hash_password,
                "salt" : salt
            }
            
            st.session_state.client[st.secrets["mongo"]["user"]].update_one(
                { "user_mail" : st.session_state.recover_mail }, 
                { "$set" : new_pswd_payload } 
            )
            
            st.session_state.user_set = list(
                st.session_state.client[st.secrets["mongo"]["user"]].find()
            )
            
            st.session_state.pswd_valid = 0
        else:
            st.session_state.pswd_valid = 6

st.subheader("กรอกรหัสผ่านใหม่", divider="grey")
        
with st.container(border=True):
    
    new_pswd = st.text_input("กรอกรหัสผ่าน",type="password", 
                help="รหัสผ่านควรยาวมากกว่า 6 ตัวอักษร")
    
    con_pswd = st.text_input("ยืนยันรหัสผ่าน",type="password")
    
    if "pswd_valid" in st.session_state:
        if st.session_state.pswd_valid == 1:
            st.error("❌ กรุณากรอกรหัสผ่าน")
        elif st.session_state.pswd_valid == 2:
            st.error("❌ รหัสผ่านใหม่ต้องไม่มีช่องว่าง")
        elif st.session_state.pswd_valid == 3:
            st.error("❌ รหัสผ่านควรมีความยาวมากกว่า 5 ตัวอักษร") 
        elif st.session_state.pswd_valid == 4:
            st.error("❌ กรุณายืนยันรหัสผ่าน")
        elif st.session_state.pswd_valid == 5:
            st.error("❌ รหัสผ่านไม่ตรงกัน")
        elif st.session_state.pswd_valid == 6:
            st.error("❌ ยืนยันไม่สำเร็จ กรุณาลองใหม่")
        elif st.session_state.pswd_valid == 0:
            st.success("✔️ กู้รหัสผ่านสำเร็จ")
            sleep(1)
            to_login()
                
    st.button("ยืนยันการแก้ไขรหัสผ่าน", use_container_width=True, type="primary",
        on_click=pswd_recover_confirm          
    )
    
with st.popover("ยกเลิกการเปลี่ยนรหัสผ่าน", use_container_width=True):
    st.markdown("ต้องการยกเลิกการกรอก OTP? ถ้าต้องการกู้รหัสผ่าน จะต้องขอรหัส OTP ใหม่")
    back_to_login = st.button("ย้อนกลับ", use_container_width=True)
    
    if back_to_login:
        to_login()