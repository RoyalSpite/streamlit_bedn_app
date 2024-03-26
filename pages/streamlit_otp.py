import streamlit as st
import datetime as dt
    
def back_to_login():

    if 'otp_code' in st.session_state:
        del st.session_state.otp_code
    
    if 'ref_code' in st.session_state:
        del st.session_state.ref_code
        
    if 'otp_time' in st.session_state:
        del st.session_state.otp_time
    
    if 'query_email' in st.session_state:
        del st.session_state.query_email
    
    if 'otp_check' in st.session_state:
        del st.session_state.otp_check
    
    st.switch_page('streamlit_app.py')
    
# if (('otp_code' not in st.session_state) 
#     or ('ref_code' not in st.session_state) 
#     or ('otp_time' not in st.session_state)
#     or ('query_email' not in st.session_state)
#     ):
#     back_to_login()

st.subheader("กรุณากรอกรหัส OTP ที่ได้รับ")

with st.form('otp',border=True):
    
    st.info(f'ℹ️ รหัสอ้างอิง : {st.session_state.ref_code}')   
    otp = st.text_input("กรุณากรอกรหัส OTP", max_chars=6, type="password")
    
    if 'otp_check' in st.session_state:
        if len(otp) == 0:
            st.error("❌ กรุณากรอกรหัส OTP")
        elif otp == st.session_state.otp_code:
            if dt.datetime.today() <= (st.session_state.otp_time + dt.timedelta(minutes=3)):
                del st.session_state.otp_code
                del st.session_state.ref_code
                del st.session_state.otp_time
                del st.session_state.otp_check
                st.success("✔️ รหัส OTP ถูกต้อง")
                st.switch_page('pages/streamlit_pswd_new.py')
            else:
                st.error("❌ รหัส OTP หมดอายุ กรุณาขอรหัสใหม่")
        else:
            st.error("❌ รหัส OTP ไม่ถูกต้อง")
    else:
        st.session_state.otp_check = ""

    submit_otp = st.form_submit_button("ยืนยัน", use_container_width=True, 
        type="primary"
    )

with st.popover("ยกเลิก", use_container_width=True):
    st.markdown("ต้องการยกเลิกการกรอก OTP? ถ้าต้องการกู้รหัสผ่าน จะต้องขอรหัส OTP ใหม่")
    login_button = st.button("กลับไปหน้าเข้าสู่ระบบ", use_container_width=True)
    
    if login_button:
        back_to_login()