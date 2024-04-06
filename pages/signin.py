import streamlit as st
import bcrypt
import datetime as dt
from utils.utils import send_email, getOTP
from email_validator import validate_email, EmailNotValidError
from time import sleep

def sigin_verify_message(otp):
    return f"""
    <html>
        <body>
            <p>ท่านได้ลงทะเบียนเข้าสู่ระบบตรวจจับ และแจ้งเตือนการรุกล้ำของรถขุด</p>
            <p>กรุณากรอกรหัส OTP เพื่อยืนยัน</p>
            <p>รหัส OTP  : {otp['otp_code']}</p>
            <p>รหัสอ้างอิง : {otp['ref_code']}</p>
            <p><h3>** รหัส OTP นี้มีอายุ 3 นาที **</h3></p>
            <p><h3>** กรุณาอย่าแชร์รหัส OTP นี้ให้ผู้อื่นเด็ดขาด **</h3></p>
            <p>อีเมลนี้เป็นการตอบกลับอัตโนมัติ อย่าตอบกลับ</p>
        </body>
    </html>
    """

def back_to_login():
    if 'email_valid' in st.session_state:
        del st.session_state.email_valid
    
    if 'pswd_valid' in st.session_state:
        del st.session_state.pswd_valid
        
    st.switch_page("streamlit_app.py")
    
def checkEmail(mail):
    
    user_dict = list(st.session_state.client[st.secrets["mongo"]["user"]].find({
        'user_mail' : mail
    }))
    
    if len(mail) == 0:
        # ไม่ได้กรอกอีเมล
        return 1
    elif " " in mail:
        # อีเมลมีช่องว่าง
        return 2
    elif(len(user_dict)) > 0:
        # อีเมลที่กรอกมีคนใช้แล้ว
        return 3
    else:
        try:                
            validate_email(mail, check_deliverability=True)
        except EmailNotValidError as e:
            # อีเมลไม่มี @
            return 4   
        else:
            return 0

def checkPassword(pswd1, pswd2):
    if (len(pswd1) == 0):
        # ไม่ได้กรอกรหัสผ่าน
        return 1
    elif " " in pswd1:
        # รหัสผ่านมีช่องว่าง
        return 2
    elif not (len(pswd1) >= 6):
        # รหัสผ่านสั้นกว่า 6 ตัว
        return 3
    elif (len(pswd2) == 0):
        # ไม่ได้กรอกยืนยันรหัสผ่าน
        return 4
    elif pswd1 != pswd2:
        # รหัสผ่านไม่ตรงกัน
        return 5
    else:
        return 0

def signin_confirm():
    
    st.session_state.email_valid = checkEmail(new_mail.lower())
    st.session_state.pswd_valid = checkPassword(new_pswd, con_pswd)
    
    if st.session_state.email_valid == 0 and st.session_state.pswd_valid == 0:

        recipient = new_mail.lower()

        salt = bcrypt.gensalt()
        byte_pswd = bytes(new_pswd, 'utf-8')
        hash_password = bcrypt.hashpw(byte_pswd, salt)
            
        otp = getOTP()

        email_payload = {
            'subject' : "noreply : ยืนยันการสมัครเข้าสู่ระบบ",
            'body' : sigin_verify_message(otp)
        }

        if send_email(recipient, email_payload) == "success":
            
            st.session_state.otp_code = otp['otp_code']
            st.session_state.ref_code = otp['ref_code']
            st.session_state.otp_time = dt.datetime.today()
            st.session_state.new_page = 'signin'
            
            st.session_state.signin_payload = {
                "user_mail" : recipient,
                "password" : hash_password,
                "salt" : salt,
                "inUse" : False
            }
            
        else:
            st.session_state.email_valid = 6
            st.session_state.pswd_valid = 6

st.header("ลงทะเบียน")

with st.container(border=True):
    
    new_mail = st.text_input(label="เพิ่มอีเมล")
    
    if "email_valid" in st.session_state:
        if st.session_state.email_valid == 1 : 
            st.error("❌ กรุณากรอกอีเมล")
        elif st.session_state.email_valid == 2:
            st.error("❌ อีเมลต้องไม่มีช่องว่าง")
        elif st.session_state.email_valid == 3:
            st.error("❌ อีเมลนี้มีคนใช้แล้ว")
        elif st.session_state.email_valid == 4:
            st.error("❌ อีเมลนี้ไม่ถูกต้อง")
        elif st.session_state.email_valid == 0:
            st.success("✔️ อีเมลนี้ สามารถใช้งานได้")
        
    new_pswd = st.text_input("กรอกรหัสผ่าน",type="password", 
                help="รหัสผ่านต้องยาวไม่ต่ำกว่า 6 ตัวอักษร")
    
    con_pswd = st.text_input("ยืนยันรหัสผ่าน",type="password")
    
    if "pswd_valid" in st.session_state:
        if st.session_state.pswd_valid == 1:
            st.error("❌ กรุณากรอกรหัสผ่าน")
        elif st.session_state.pswd_valid == 2:
            st.error("❌ รหัสผ่านใหม่ต้องไม่มีช่องว่าง")
        elif st.session_state.pswd_valid == 3:
            st.error("❌ รหัสผ่านต้องยาวไม่ต่ำกว่า 6 ตัวอักษร") 
        elif st.session_state.pswd_valid == 4:
            st.error("❌ กรุณายืนยันรหัสผ่าน")
        elif st.session_state.pswd_valid == 5:
            st.error("❌ รหัสผ่านไม่ตรงกัน")
        elif st.session_state.pswd_valid == 0:
            st.success("✔️ รหัสผ่านนี้สามารถใช้งานได้")
    
    if "pswd_valid" in st.session_state and "email_valid" in st.session_state:
        if st.session_state.email_valid == 0 and st.session_state.pswd_valid == 0:
            del st.session_state.email_valid
            del st.session_state.pswd_valid        
            sleep(1)
            st.switch_page('pages/otp.py')
        elif st.session_state.email_valid == 6 and st.session_state.pswd_valid == 6:
            st.error("❌ ไม่สามารถส่งรหัส OTP ได้ กรุณาลองใหม่อีกครั้ง")            
                
    confirm = st.button("ยืนยัน", use_container_width=True, type="primary",
            on_click=signin_confirm
    )

backToLogin = st.button("กลับสู่หน้า login", use_container_width=True)

if backToLogin:
    back_to_login()