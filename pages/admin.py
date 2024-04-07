import streamlit as st

st.subheader("จัดการบัญชี", divider='gray')

def back_to_login():
    del st.session_state.user_set
    st.switch_page("streamlit_app.py")
    
if 'user_set' not in st.session_state:
    # query after delete
    st.session_state.user_set = list(
        st.session_state.client[st.secrets["mongo"]["user"]].find()
    )
else:
    for i in range(len(st.session_state.user_set)):
        if st.session_state.get(f"detete_user{i}"):
            user = st.session_state.user_set[i]
            print(f"อีเมลผู้ใช้งาน : {user['user_mail']}")
            
            st.session_state.client[st.secrets["mongo"]["user"]].delete_one(
                { "user_mail" : user['user_mail'] }
            )
            
            # query after delete
            st.session_state.user_set = list(
                st.session_state.client[st.secrets["mongo"]["user"]].find()
            )
            
            st.rerun()
            break



with st.container(border=True):
    if len(st.session_state.user_set) == 0:
        st.write("ไม่มีข้อมูลผู้ใช้")
    else:
        for i in range(len(st.session_state.user_set)):
            user = st.session_state.user_set[i]
            with st.container(border=True):
                col_name, col_button = st.columns([0.75, 0.25])
                with col_name:
                    st.write(f"อีเมลผู้ใช้งาน : {user['user_mail']}")
                with col_button:
                    with st.popover(label="ลบบัญชี", use_container_width=True):
                        st.write("แน่ใจ?")
                        st.button("ลบ",key=f"detete_user{i}",use_container_width=True)
                        
with st.sidebar:
    st.subheader("แอดมิน", divider="grey")
    
    to_vis = st.button("ดูผลการรุกล้ำ", use_container_width=True)
    if to_vis:
        st.session_state.login_email = "แอดมิน"
        st.switch("pages/visualization.py")    
    
    with st.popover(label="ออกจากระบบ", use_container_width=True):
        st.markdown("ยืนยันการออกจากระบบ?")
        logout = st.button("ใช่" , use_container_width=True)
        
        if logout:
            back_to_login()