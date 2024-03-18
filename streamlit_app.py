import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.timestamp import Timestamp
import datetime as dt
from dateutil.relativedelta import relativedelta 
import numpy as np

# st.write(f"username : {st.secrets['db_username']}")
# st.write(f"password : {st.secrets['db_pswd']}")

@st.cache_resource
def init_connection():
    global img_array
    return MongoClient({st.secrets["mongo"]["uri"]}, server_api=ServerApi('1'))

client = init_connection()

@st.cache_data
def query(date = dt.date.today()):
    
    database = client[st.secrets["mongo"]["col"]]
    collection = database[st.secrets["mongo"]["col"]]
    
    _from = dt.datetime.strptime(str(date), '%Y-%m-%d')
    _to = _from.replace(hour=23,minute=59,second=59,microsecond=999)
        
    criteria = { "date": {"$gte": _from, "$lte": _to } }

    return list(collection.find(criteria))

## ---------- Application --------------
st.header("Backhoe Encroachment Visualizer")

col1, col2 = st.columns([0.3,0.7])

with col1:
    with st.container(border=True):
            
        month_range = 3
                
        dateNow = dt.datetime.now()
        datePrev3 = dateNow - relativedelta(months = month_range)
        dateNext3 = dateNow
        
        date = st.date_input(
            "เลือกวันที่",
            value = dt.datetime.now(),
            min_value = datePrev3,
            max_value = dateNow,
            format = "DD.MM.YYYY",
        )
        
        AllDay = st.toggle('ดูตลอดทั้งวัน', value=False)
            
        time = st.slider("เลือกช่วงชั่วโมง",
            min_value=0,max_value=23,step=1, value=0, 
            disabled=AllDay
        )
        
        if not AllDay:
            st.write(f'เลือกในช่วง {time}:00 - {time}:59')
        
        
        # t = st.time_input('เลือกช่วงเวลา', dt.datetime.now())
            
with col2:
    
    img_array = query(date)
    filtered_array = list()
    
    if AllDay:
        filtered_array = img_array
    else:           
        _datetime_from = dt.datetime.strptime(str(date), '%Y-%m-%d').replace(hour=time)
        _datetime_to = _datetime_from.replace(minute=59,second=59, microsecond=999)
            
        filtered_array = list(filter(
            lambda elem: (elem['date'] >= _datetime_from) and (elem['date'] <= _datetime_to),
            img_array
        ))
            
    if len(filtered_array) == 0:
        st.container(border=True).write("ไม่มีข้อมูล")
    else:
        for img_data in filtered_array:            

            disp_date = img_data['date']
                
            disp_text = f'{disp_date.strftime("%d/%m")}/{disp_date.year + 543}'
            disp_time = f'เวลา {disp_date.strftime("%H:%M:%S")}'
                    
            with st.expander(f'{disp_text} {disp_time}'):
                st.image(img_data['img'])         
