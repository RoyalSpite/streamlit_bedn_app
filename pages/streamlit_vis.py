import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.timestamp import Timestamp
import datetime as dt
from dateutil.relativedelta import relativedelta 
import numpy as np

# st.write(f"username : {st.secrets['db_username']}")
# st.write(f"password : {st.secrets['db_pswd']}")

@st.cache_data
def query(date):
    
    database = st.session_state.client[st.secrets["mongo"]["col"]]
    collection = database[st.secrets["mongo"]["col"]]
    
    _from = dt.datetime.strptime(str(date[0]), '%Y-%m-%d')
    _to = dt.datetime.strptime(str(date[1]), '%Y-%m-%d')
    _to = _to.replace(hour=23,minute=59,second=59,microsecond=999)
        
    criteria = { "date": {"$gte": _from, "$lte": _to } }    
    
    return list(collection.find(criteria))

## ---------- Application --------------
st.header("Backhoe Encroachment Visualizer")

col1, col2 = st.columns([0.31,0.69])

with col1:
    with st.form(key="query_select",border=True):
            
        st.form_submit_button("ค้นหา", use_container_width=True)
            
        month_range = 3
                
        dateNow = dt.datetime.now()
        datePrev3 = dateNow - relativedelta(months = month_range)
        dateNext3 = dateNow
        
        date = st.date_input(
            "เลือกวันที่",
            value = (dateNow, dateNow),
            min_value = datePrev3,
            max_value = dateNow,
            format = "DD.MM.YYYY",
        )

        min_time = dt.time(0,0)
        max_time = dt.time(23,59)
        time = st.slider("เลือกช่วงชั่วโมง",
            value=(min_time,max_time), step = dt.timedelta(minutes=5)
        )
            
with col2:
    
    filtered_array = list()
    if len(date) == 1 :
        st.error("กรุณาเลือกช่วงเวลาให้ถูกต้อง")
    else:
 
        img_array = query(date)                    
        filtered_array = list()
        
        _time_from = time[0].replace(microsecond=0)
        _time_to = time[1].replace(microsecond=999999)
        
        filtered_array = list(filter(
            lambda elem: (elem['date'].time() >= _time_from) and (elem['date'].time() <= _time_to),
            img_array
        ))
    
        if len(filtered_array) == 0:
            st.container(border=True).write("ไม่มีข้อมูล")
        else:
            st.write("กดเพื่อดูรูปภาพการรุกล้ำ")
            for img_data in filtered_array:            

                disp_date = img_data['date']
                    
                disp_text = f'{disp_date.strftime("%d/%m")}/{disp_date.year}'
                disp_time = f'เวลา {disp_date.strftime("%H:%M:%S")}'
                        
                with st.expander(f'{disp_text} {disp_time}'):
                    st.image(img_data['img'])
                    
with st.sidebar:
    st.subheader(st.session_state.login_usrname)
    logout_button = st.button(label="ออกจากระบบ", use_container_width=True)
    
    if logout_button:
        del st.session_state.login_usrname
        st.switch_page('streamlit_app.py')
