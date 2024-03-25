import streamlit as st
import math, random, string
from utils.send_email import send_email
import datetime as dt

def otp_request_message(otp_payload):
    return f"""
    <html>
        <body>
            <p>ท่านได้ขอรหัสผ่านใหม่</p>
            <p>รหัส OTP  : {otp_payload['otp_code']}</p>
            <p>รหัสอ้างอิง : {otp_payload['ref_code']}</p>
            <p><h3>** รหัส OTP นี้มีอายุ 3 นาที **</h3></p>
            <p><h3>** กรุณาอย่าแชร์รหัส OTP นี้ให้ผู้อื่นเด็ดขาด **</h3></p>
            <p>อีเมลล์นี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
        </body>
    </html>
    """

def back_to_login():
    
    if 'otp_code' in st.session_state:
        del st.session_state.otp_code
    
    if 'ref_code' in st.session_state:
        del st.session_state.ref_code
    
    if 'otp_time' in st.session_state:
        del st.session_state.otp_time
    
    if 'query_email' in st.session_state:
        del st.session_state.query_email
    
    if 'recover' in st.session_state:
        del st.session_state.recover

    st.switch_page('streamlit_app.py')

def getOTP_Elem() :
    digits = "0123456789"
    otp_payload = {}
    otp_payload['otp_code'] = ''.join([digits[math.floor(random.random() * 10)] for _ in range(6) ])
    otp_payload['ref_code'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return otp_payload

st.subheader("กู้คืนรหัสผ่าน")

with st.container(border=True):
    
    search_mail = st.text_input("ค้นหาอีเมลล์")
    
    if 'recover' in st.session_state:
        if (len(list(filter(lambda user: user["user_mail"] == search_mail.lower(), st.session_state.user_set)))) > 0:
            # find email, set otp and ref code
            otp_set = getOTP_Elem()
            mail_payload = {
                'subject' : "ขอรหัส OTP ใหม่",
                'body' : otp_request_message(otp_set)
            }
            if send_email(search_mail.lower(), mail_payload) == "success":
                # email send success, go to otp verification
                st.session_state.otp_code = otp_set['otp_code']
                st.session_state.ref_code = otp_set['ref_code']
                st.session_state.otp_time = dt.datetime.now()
                st.session_state.query_email = search_mail.lower()
                st.success("✔️ ส่ง OTP สำเร็จ")
                            
                if 'recover' in st.session_state:
                    del st.session_state.recover
                
                st.switch_page('pages/streamlit_otp.py')
            else:
                st.error("❌ ส่งรหัส OTP ไม่สำเร็จ กรุณาลองใหม่อีกครั้ง")
        else:
            st.error("❌ ไม่พบอีเมลล์")
    else:
        st.session_state.recover = ""

    recovery_submit = st.button("ค้นหาอีเมลล์", use_container_width=True, 
        type="primary"
    )
    
login_button = st.button("ย้อนกลับ", use_container_width=True)

if login_button:
    back_to_login()