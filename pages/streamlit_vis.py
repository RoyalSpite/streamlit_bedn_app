import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.timestamp import Timestamp
import datetime as dt
from dateutil.relativedelta import relativedelta 
import numpy as np

@st.cache_resource
def init_connection():
    global img_array
    return MongoClient({st.secrets["mongo"]["uri"]}, server_api=ServerApi('1'))

if "client" not in st.session_state:
    st.session_state.client = init_connection()

@st.cache_data
def query(date):
    database = st.session_state.client[st.secrets["mongo"]["col"]]
    collection = database[st.secrets["mongo"]["col"]]
    
    _from = dt.datetime.strptime(str(date[0]), '%Y-%m-%d')
    _to = dt.datetime.strptime(str(date[1]), '%Y-%m-%d')
    _to = _to.replace(hour=23,minute=59,second=59,microsecond=999)
        
    criteria = { "date": {"$gte": _from, "$lte": _to } }    
    
    return list(collection.find(criteria))

def getTimeInterval():
    
    def convert_time(time):
        return time.strftime("%H:%M")
    
    time_list = list()

    curr_time = dt.datetime.combine(dt.date.today(), dt.time(0, 0))
    next_time = dt.datetime.combine(dt.date.today(), dt.time(0, 0))

    while True:

        next_time += dt.timedelta(minutes=15)

        time_list.append('-'.join((convert_time(curr_time), convert_time(next_time.time()))))

        if next_time.time() == dt.time(0,0):
            break
        else:
            curr_time = next_time

    return time_list

def back_to_login():
    del st.session_state.login_email
    st.switch_page('streamlit_app.py')

## ---------- Application --------------
st.header("Backhoe Encroachment Visualizer")

with st.form(key="query_select",border=True):

    month_range = 3
                
    dateNow = dt.datetime.now()
    datePrev3 = dateNow - relativedelta(months = month_range)
    dateNext3 = dateNow
    
    button_col , date_col, time_col = st.columns([0.2, 0.4, 0.4])
    
    with button_col:
        st.form_submit_button("ค้นหา", use_container_width=True, type="primary")
        
    with date_col:        
        date = st.date_input(
            "เลือกวันที่",
            value = (dateNow, dateNow),
            min_value = datePrev3,
            max_value = dateNow,
            format = "DD.MM.YYYY",
        )
    
    with time_col:
        time = st.multiselect(label="เลือกช่วงเวลา",
            placeholder="เลือกช่วงเวลา",options=getTimeInterval())
                                        
with st.container(border=True):
    
    if len(date) == 1 :
        st.error("กรุณาเลือกช่วงเวลาให้ถูกต้อง")
    else:
 
        img_array = query(date)                    
        date_tab_arr = list()
        
        curr_date = date[0]
        while True:
            if curr_date > date[1]:
                break
            else:
                c1 = curr_date
                c2 = curr_date + dt.timedelta(days=1)
                disp_date = f'{curr_date.strftime("%d/%m")}/{curr_date.year}'
                filtered_img = list(filter(lambda d: (d['date'].date() >= c1 and d['date'].date() < c2), img_array ))
                
                date_tab_arr.append(curr_date)
                
                curr_date += dt.timedelta(days=1)

        for _tab in date_tab_arr:
            with st.expander(_tab.strftime("%d/%m/%Y")):
                
                curr_date_exp = list(filter(lambda d:(d['date'].date() >= _tab and d['date'].date() < _tab + dt.timedelta(days=1)), img_array ))
                
                if len(time) == 0:
                    if len(curr_date_exp) == 0:
                        st.write("ไม่มีข้อมูล")
                    else:
                        for exp in curr_date_exp:
                            
                            with st.container(border=True):
                                st.write(exp['date'].strftime("%H:%M:%S"))
                                st.image(exp['img'])
                            
                else:
                    time_list = [time_int.split("-")  for time_int in time]
                    filter_time = list()            
                    
                    for time_int in time_list:
                        t1_h, t1_m = time_int[0].split(":")
                        t1 = dt.time(int(t1_h), int(t1_m))
                        
                        t2_h, t2_m = time_int[1].split(":")
                        if (t2_m=="00"):
                            if (t2_h=="00"):
                                t2 = dt.time(hour=23)
                            else:
                                t2 = dt.time(hour=int(t2_h) - 1)
                            t2 = t2.replace(minute=59)
                        else:
                            t2 = dt.time(hour=int(t2_h), minute=(int(t2_m) - 1))
                            
                        t2 = t2.replace(second=59,microsecond=999999)
                        
                        filter_time.append((t1, t2))
                        
                    filter_time = list(sorted(filter_time,key=lambda t:t[0]))
               
                    for _time in filter_time:
                        current_time_exp = list(filter(
                            lambda d:(d['date'].time() >= _time[0] and d['date'].time() <= _time[1])
                            , img_array ))
                        next_time = dt.datetime.combine(dt.date.today(), _time[1]) + dt.timedelta(microseconds=1)
                        st.write(f'{_time[0].strftime("%H:%M")} - {(next_time).strftime("%H:%M")}')
                        if len(current_time_exp) == 0:
                            st.write("ไม่มีข้อมูล")
                        else:
                            for c_exp in current_time_exp:
                                with st.container(border=True):
                                    st.write(c_exp['date'].strftime("%H:%M:%S"))
                                    st.image(c_exp['img'])
                
        # if len(time) == 0:
        #     filtered_array = img_array
        # else:
        #     time_list = [time_int.split("-")  for time_int in time]
        #     filter_time = list()            
            
        #     for time_int in time_list:
        #         t1_h, t1_m = time_int[0].split(":")
        #         t1 = dt.time(int(t1_h), int(t1_m))
                
        #         t2_h, t2_m = time_int[1].split(":")
        #         if (t2_m=="00"):
        #             if (t2_h=="00"):
        #                 t2 = dt.time(hour=23)
        #             else:
        #                 t2 = dt.time(hour=int(t2_h) - 1)
        #             t2 = t2.replace(minute=59)
        #         else:
        #             t2 = dt.time(hour=int(t2_h), minute=(int(t2_m) - 1))
                    
        #         t2 = t2.replace(second=59,microsecond=999999)
                
        #         filter_time.append((t1, t2))
                
        #     filter_time = list(sorted(filter_time,key=lambda t:t[0]))
            
        #     st.write(filter_time)
            
            
            
        #     for _img in img_array:
        #         for _time in filter_time:
        #             if (_img['date'].time() >= _time[0]) and (_img['date'].time() <= _time[1]):
        #                 filtered_array.append(_img)
        #                 break

        # if len(filtered_array) == 0:
        #     st.container(border=True).write("ไม่มีข้อมูล")
        # else:
        #     st.write("กดเพื่อดูรูปภาพการรุกล้ำ")
        #     for img_data in filtered_array:            

        #         disp_date = img_data['date']
                    
        #         disp_text = f'{disp_date.strftime("%d/%m")}/{disp_date.year}'
        #         disp_time = f'เวลา {disp_date.strftime("%H:%M:%S")}'
                        
        #         with st.expander(f'{disp_text} {disp_time}'):
        #             st.image(img_data['img'])
                    
with st.sidebar:
    st.subheader(st.session_state.login_email)
    
    with st.popover(label="ออกจากระบบ", use_container_width=True):
        st.markdown("ยืนยันการออกจากระบบ?")
        logout = st.button("ใช่" , use_container_width=True, on_click=back_to_login)
