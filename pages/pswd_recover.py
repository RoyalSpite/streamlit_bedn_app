import streamlit as st
import math, random, string
from utils.utils import send_email, getOTP
import datetime as dt
from time import sleep

def otp_request_message(otp_payload):
    return f"""
    <html>
        <body>
            <p>ท่านได้ขอรหัสผ่านใหม่</p>
            <p>รหัส OTP  : {otp_payload['otp_code']}</p>
            <p>รหัสอ้างอิง : {otp_payload['ref_code']}</p>
            <p><h3>** รหัส OTP นี้มีอายุ 3 นาที **</h3></p>
            <p><h3>** กรุณาอย่าแชร์รหัส OTP นี้ให้ผู้อื่นเด็ดขาด **</h3></p>
            <p>อีเมลนี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
        </body>
    </html>
    """

def back_to_login():
    if 'recover' in st.session_state: del st.session_state.recover
    st.switch_page('streamlit_app.py')
    
def checkEmailInput():
    
    if len(search_mail) == 0:
        st.session_state.recover = 1
    else:
        user_dict = list(st.session_state.client[st.secrets["mongo"]["user"]].find({
            'user_mail' : search_mail.lower()
        }))

        if len(user_dict) > 0:
            if user_dict[0]['inUse'] == True:
                st.session_state.recover = 3
            else:
                            
                otp = getOTP()
                email_payload = {
                    'subject' : "noreply : แก้ไขรหัสผ่าน",
                    'body' : otp_request_message(otp)
                }
                
                if send_email(search_mail.lower(), email_payload) == "success":
                    # success  
                    st.session_state.otp_code = otp['otp_code']
                    st.session_state.ref_code = otp['ref_code']
                    st.session_state.otp_time = dt.datetime.today()
                    st.session_state.new_page = 'pswd_recover'
                    st.session_state.recover_mail = search_mail.lower()
        
                    st.session_state.recover = 0
                else:
                    st.session_state.recover = 4
        else:
            st.session_state.recover = 2

st.subheader("กู้คืนรหัสผ่าน")

with st.container(border=True):
    
    search_mail = st.text_input("ค้นหาอีเมล")
    
    if 'recover' in st.session_state:
        if st.session_state.recover == 0:
            st.success("✔️ ส่ง OTP สำเร็จ")
            del st.session_state.recover
            sleep(1)
            st.switch_page('pages/otp.py')
        elif st.session_state.recover == 1:
            st.error("❌ กรุณากรอกอีเมล")
        elif st.session_state.recover == 2:
            st.error("❌ ไม่พบอีเมล")
        elif st.session_state.recover == 3:
            st.error("❌ ไม่สามารถกู้คืนรหัสผ่านได้ เนื่องจากผู้ใช้นี้กำลังใช้งานระบบ")
        elif st.session_state.recover == 4:
            st.error("❌ ไม่สามารถส่งรหัส OTP ได้ กรุณาลองใหม่อีกครั้ง")

    recovery = st.button("ค้นหาอีเมล", use_container_width=True, 
        type="primary", on_click=checkEmailInput
    )
    
login_ = st.button("ย้อนกลับ", use_container_width=True)

if login_:
    back_to_login()