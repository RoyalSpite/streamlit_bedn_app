import streamlit as st
import datetime as dt
from time import sleep
from utils.utils import send_email

def sigin_complete_message():
    sigin_time = dt.datetime.now()
    return f"""
    <html>
        <body>
            <p>ท่านได้กู้รหัสผ่านสำเร็จ</p>
            <p>เมื่อวันที่ {sigin_time.strftime("%d/%m/%y")}</p>
            <p>เวลา {sigin_time.strftime("%H:%M:%S")}</p>
            <p>อีเมลล์นี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
        </body>
    </html>
    """    

def back_to_login():

    if st.session_state.new_page == 'signin':
        del st.session_state.signin_payload
    elif st.session_state.new_page == 'pswd_recover':
        del st.session_state.recover_mail

    del st.session_state.new_page

    del st.session_state.otp_code
    del st.session_state.ref_code
    del st.session_state.otp_time
    
    if 'otp_check' in st.session_state :
        del st.session_state.otp_check
    
    st.switch_page('streamlit_app.py')

def checkOTP():
    if len(otp) == 0:
        st.session_state.otp_check = 1
    else:
        if otp == st.session_state.otp_code:
            if dt.datetime.today() <= (st.session_state.otp_time + dt.timedelta(minutes=3)):                
                if st.session_state.new_page == 'signin':   
                    mail_payload = {
                        'subject' : "noreply : กู้รหัสผ่านสำเร็จ",
                        'body' : recover_complete_message()
                    }
                    if send_email(st.session_state.signin_payload["user_mail"], mail_payload) == "success":
                        # success
                        st.session_state.otp_check = 0
                    else:
                        st.session_state.otp_check = 4
                else:
                    # success
                    st.session_state.otp_check = 0
        
            else:
                st.session_state.otp_check = 3
        else:
            st.session_state.otp_check = 2

st.subheader("กรุณากรอกรหัส OTP ที่ได้รับ")

with st.container(border=True):
    
    st.info(f'ℹ️ รหัสอ้างอิง : {st.session_state.ref_code}')   
    otp = st.text_input("กรุณากรอกรหัส OTP", max_chars=6, type="password")
    
    if 'otp_check' in st.session_state:
        if st.session_state.otp_check == 1 :
            st.error("❌ กรุณากรอกรหัส OTP")
        elif st.session_state.otp_check == 2:
            st.error("❌ รหัส OTP ไม่ถูกต้อง")
        elif st.session_state.otp_check == 3:
            st.error("❌ รหัส OTP หมดอายุ กรุณาขอรหัสใหม่")
        elif st.session_state.otp_check == 4:
            st.error("❌ ยืนยันรหัสไม่สำเร็จ กรุณาลองใหม่อีกครั้ง")
        elif st.session_state.otp_check == 0:
            # success    
            del st.session_state.otp_code
            del st.session_state.ref_code
            del st.session_state.otp_time
            del st.session_state.otp_check
                
            st.success("✔️ รหัส OTP ถูกต้อง")
            if st.session_state.new_page == 'signin':
                st.session_state.client[st.secrets["mongo"]["user"]].insert_one(
                    st.session_state.signin_payload
                )
                del st.session_state.signin_payload
                
                st.toast("✔️ ลงทะเบียนสำเร็จ")
                sleep(1)
                st.switch_page('streamlit_app.py')
            elif st.session_state.new_page == 'pswd_recover':
                st.switch_page('pages/pswd_new.py')

    submit_otp = st.button("ยืนยัน", use_container_width=True, 
        type="primary", on_click=checkOTP
    )

with st.popover("ยกเลิก", use_container_width=True):
    # st.markdown("ต้องการยกเลิกการกรอก OTP? ถ้าต้องการกู้รหัสผ่าน จะต้องขอรหัส OTP ใหม่")
    login_button = st.button("กลับไปหน้าเข้าสู่ระบบ", use_container_width=True)
    
    if login_button:
        back_to_login()
        
# with st.popover("ขอรหัส OTP ใหม่", use_container_width=True):
#     st.markdown("ต้องการขอรหัส OTP ใหม่?")
#     resent_otp = st.button("กลับไปหน้าเข้าสู่ระบบ", use_container_width=True)
    
#     if resent_otp:
#         back_to_login()