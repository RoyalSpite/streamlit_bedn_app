import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.timestamp import Timestamp
import datetime as dt
from dateutil.relativedelta import relativedelta 
import numpy as np

# mongodb+srv://siriwutthesorcerer:vkd5D8LtnyWw7JCl@image-test.kv0abp0.mongodb.net/

st.write(f"username : {st.secrets['db_username']}")
st.write(f"password : {st.secrets['db_pswd']}")

# @st.cache_resource
# def init_connection():
#     uri = f'mongodb+srv://{st.secrets["db_username"]}:{st.secrets["db_pswd"]}@image-test.kv0abp0.mongodb.net/?retryWrites=true&w=majority&appName=image-test'
#     return MongoClient(uri, server_api=ServerApi('1'))

# client = init_connection()

# @st.cache_data(ttl=600)
# def query(date = dt.date.today(), hour = 0, allday = False):
    
#     database = client['img']
#     collection = database['img']
    
#     _from = dt.datetime.strptime(str(date), '%Y-%m-%d')
#     if not allday:
#         _from = _from.replace(hour = hour)
#         _to = _from.replace(minute=59,second=59)
#     else:
#         _to = _from.replace(hour=23,minute=59,second=59)
        
#     criteria = { "date": {"$gte": _from, "$lte": _to } }

#     return list(collection.find(criteria))

# ## ---------- Application --------------
# st.header("Backhoe Encroachment Visualizer")

# col1, col2 = st.columns([0.3,0.7])

# with col1:
#     with st.container(border=True):
            
#         month_range = 3
                
#         dateNow = dt.datetime.now()
#         datePrev3 = dateNow - relativedelta(months = month_range)
#         dateNext3 = dateNow
        
#         date = st.date_input(
#             "เลือกวันที่",
#             value = dt.datetime.now(),
#             min_value = datePrev3,
#             max_value = dateNow,
#             format = "DD.MM.YYYY",
#         )
        
#         AllDay = st.toggle('ดูตลอดทั้งวัน')
            
#         time = st.slider("เลือกช่วงชั่วโมง",
#             min_value=0,max_value=23,step=1, value=0, 
#             disabled=AllDay
#         )
        
#         if not AllDay:
#             st.write(f'เลือกในช่วง {time}:00 - {time}:59')
        
        
#         # t = st.time_input('เลือกช่วงเวลา', dt.datetime.now())
            
# with col2:
#     img_set = st.container(border=True)
    
#     img_array = query(date, time, AllDay)
    
#     if len(img_array) == 0:
#         img_set.text("ไม่พบข้อมูล")
#     else:
#         for img_data in img_array:            
#             disp_date = img_data['date']
#             disp_text = f'{disp_date.day}/{disp_date.month}/{disp_date.year + 543}'
#             disp_time = f'เวลา {disp_date.hour}:{disp_date.minute}:{disp_date.second}'
                
#             with st.expander(f'{disp_text} {disp_time}'):
#                 st.image(img_data['img'])         
