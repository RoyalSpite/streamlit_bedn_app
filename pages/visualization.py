import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime as dt
from dateutil.relativedelta import relativedelta 
import pandas as pd
import altair as alt

@st.cache_resource
def init_connection():
    return MongoClient({st.secrets["mongo"]["url"]}, server_api=ServerApi('1'))

if "client" not in st.session_state:
    st.session_state.client = init_connection()
    st.session_state.client = st.session_state.client[st.secrets["mongo"]["col"]]

if "curr_date_index" not in st.session_state:
    st.session_state.curr_date_index = 0

if "curr_time_index" not in st.session_state:
    st.session_state.curr_time_index = 0

if "curr_page_index" not in st.session_state:
    st.session_state.curr_page_index = 0

if "date_filter" not in st.session_state:
    st.session_state.date_filter = []

grid_size = 5

@st.cache_data
def query_date(date):

    _from = dt.datetime.strptime(str(date[0]), '%Y-%m-%d')
    _to = dt.datetime.strptime(str(date[1]), '%Y-%m-%d')
    _to = _to.replace(hour=23,minute=59,second=59,microsecond=999)
        
    criteria = { "date": {"$gte": _from, "$lte": _to } }    
    
    return list(st.session_state.client[st.secrets["mongo"]["img"]].find(criteria))

@st.cache_data
def query_month(years,months=0):

    if type(years) == int:
        _from = dt.datetime(years, 1, 1)
        _to =  dt.datetime(years + 1, 1, 1)
    else:
        _from = dt.datetime(years[0], months[0], 1)
        _to =  dt.datetime(years[1], months[1], 1)
        
    criteria = { "date": {"$gte": _from, "$lt": _to } }    
    
    return list(st.session_state.client[st.secrets["mongo"]["img"]].find(criteria))

def getTimeInterval():
    
    def convert_time(time):
        return time.strftime("%H:%M")
    
    time_list = list()

    curr_time = dt.datetime.combine(dt.date.today(), dt.time(0, 0))
    next_time = dt.datetime.combine(dt.date.today(), dt.time(0, 0))
    i = 0

    while True:

        next_time += dt.timedelta(minutes=15)

        time_list.append({
            'index'  : i,
            'select' : '-'.join((convert_time(curr_time), convert_time(next_time.time())))
        })

        if next_time.time() == dt.time(0,0):
            break
        else:
            curr_time = next_time
            i += 1

    return time_list

def back_to_login():
    
    if "date_filter" in st.session_state:
        del st.session_state.date_filter
    
    if "time_filter" in st.session_state:
        del st.session_state.time_filter

    del st.session_state.curr_date_index
    del st.session_state.curr_time_index
    del st.session_state.curr_page_index
    
    if "login_email" in st.session_state:
        
        if st.session_state.login_email == "แอดมิน":
            del st.session_state.login_email
            st.switch_page('pages/admin.py')
        else:
            del st.session_state.login_email
            st.switch_page('streamlit_app.py')  
    else:
        st.switch_page('streamlit_app.py')

def getTimeFromSelection(selectTime, curr_date = dt.date.today()):
    
    _from, _to = [
        dt.datetime.combine(curr_date,dt.datetime.strptime(_time,"%H:%M").time()) 
            for _time in selectTime.split("-")
    ]
    
    if _to.time() == dt.time(0,0):
        _to = _to + dt.timedelta(days=1)
    
    return _from, _to

def getMonthsSelect():
    return {
        "มกราคม" : 1 ,"กุมภาพันธ์" : 2,"มีนาคม" : 3,
        "เมษายน" : 4, "พฤษภาคม" : 5, "มิถุนายน" : 6, 
        "กรกฎาคม" : 7, "สิงหาคม" : 8, "กันยายน" : 9,
        "ตุลาคม" : 10, "พฤศจิกายน" : 11, "ธันวาคม" : 12
    }
 
if st.session_state.get('d_back'):
    st.session_state.curr_page_index = 0
    st.session_state.curr_date_index -= 1
    
elif st.session_state.get('d_fort'):
    st.session_state.curr_page_index = 0
    st.session_state.curr_date_index += 1
    
elif st.session_state.get('t_back'):
    st.session_state.curr_page_index = 0
    st.session_state.curr_time_index -= 1

elif st.session_state.get('t_fort'):
    st.session_state.curr_page_index = 0
    st.session_state.curr_time_index += 1

elif st.session_state.get('p_back'):
    st.session_state.curr_page_index -= 1

elif st.session_state.get('p_fort'):
    to_img = (st.session_state.curr_page_index + 1) * (grid_size * grid_size)
    curr_len = len(st.session_state.date_filter[st.session_state.curr_date_index]["img"])

    if curr_len > 0:
        if curr_len >= to_img:
            st.session_state.curr_page_index += 1

## ---------- Application --------------
st.header("แสดงผลการรุกล้ำ", divider="gray")

daily_tab , months_tab = st.tabs(["ดูข้อมูลรายวัน", "ดูข้อมูลรายเดือน/ปี"])

with daily_tab:

    with st.form(key="query_select",border=True):

        month_range = 3
                    
        dateNow = dt.datetime.now()

        button_col , date_col, time_col = st.columns([0.2, 0.4, 0.4])
        
        with button_col:
            query_submit = st.form_submit_button("ค้นหา", use_container_width=True, type="primary")
            if query_submit:
                st.session_state.curr_date_index = 0
                st.session_state.curr_time_index = 0
                st.session_state.curr_page_index = 0       
            
        with date_col:        
            date = st.date_input(
                "เลือกวันที่",
                value = (dateNow, dateNow),
                min_value = dt.date(2024, 1, 1),
                max_value = dateNow,
                format = "DD.MM.YYYY",
            )
        
        with time_col:
            
            time = st.multiselect(label="เลือกช่วงเวลา",
                placeholder="เลือกช่วงเวลา",options=[ d['select'] for d in getTimeInterval() ],
                help="เลือกช่วงเวลา ถ้าไม่ได้เลือก คือดูทั้งวัน"
            )

    if len(date) == 1:
        with st.container(border=True):
            st.error("กรุณาเลือกช่วงเวลาให้ถูกต้อง")
    else:
        img_array = query_date(date)
        st.session_state.date_filter = list()
        st.session_state.time_filter = list( 
            filter(lambda d: d['select'] in time ,getTimeInterval()) 
        )
        st.session_state.time_filter = [ d['select'] for d in list(
            sorted(st.session_state.time_filter ,key = lambda d: d['index'])
        )]
                
        curr_date = date[0]
        while True:
            if curr_date > date[1]:
                break
            else:
                c1 = curr_date
                c2 = curr_date + dt.timedelta(days=1)
                disp_date = f'{curr_date.strftime("%d/%m")}/{curr_date.year}'
                filtered_img = list(
                    filter(
                        lambda d : (d["date"].date() >= c1 and d["date"].date() < c2)
                        ,img_array
                    )
                )
                                
                # filter time
                if len(st.session_state.time_filter) > 0:
                    
                    from_time, to_time = getTimeFromSelection(
                        st.session_state.time_filter[
                            st.session_state.curr_time_index
                    ], curr_date)
                                
                    filtered_img = list(
                        filter(
                            lambda d : (
                                d["date"].time() >= from_time.time() 
                                and d["date"].time() < to_time.time()
                            )
                            ,img_array
                        )
                    )
                            
                st.session_state.date_filter.append({
                    "date" : curr_date,
                    "img" : filtered_img
                })
                        
                curr_date += dt.timedelta(days=1)

    if len(date) < 2:
        st.write("ไม่มีข้อมูล")
    else:
        # visualize
        # date control
        with st.container(border=True):
            date_grid, time_col = st.columns(2)
                    
            with date_grid:
                with st.container(border=True):
                    st.write("เลือกวัน")
                    b_col, d_col, f_col = st.columns(3)
                    with b_col: st.button(key="d_back",label="⬅️", 
                        disabled=(
                            date[0] == date[1] or st.session_state.curr_date_index == 0
                        ),
                        use_container_width=True
                    )
                    
                    with d_col: 
                        st.write(
                            st.session_state.date_filter[
                                st.session_state.curr_date_index
                            ]["date"].strftime("%d-%m-%Y")
                        )
                        
                    with f_col: st.button(key="d_fort",label="➡️",
                        disabled=(date[0] == date[1] 
                            or st.session_state.curr_date_index == len(
                                st.session_state.date_filter) - 1
                            )
                        ,use_container_width=True
                    )
                    
            with time_col:
                with st.container(border=True):
                    st.write("เลือกช่วงเวลาที่จะดู")
                    b_col, t_col, f_col = st.columns(3)
                    with b_col: st.button(key="t_back",label="⬅️",
                        disabled=(
                            len(st.session_state.time_filter) == 0 or
                            st.session_state.curr_time_index == 0
                        ),
                        use_container_width=True
                    )
                    with t_col: 
                        if len(st.session_state.time_filter) == 0: st.write("ไม่มี")
                        else: 
                            st.write(
                                st.session_state.time_filter[
                                    st.session_state.curr_time_index
                                ]
                            )
                    with f_col: st.button(key="t_fort",label="➡️", 
                        disabled=(
                            len(st.session_state.time_filter) == 0 or 
                            st.session_state.curr_time_index == (
                                len(st.session_state.time_filter) - 1)
                        ),
                        use_container_width=True
                    )    
                                                
        data = st.session_state.date_filter[st.session_state.curr_date_index]

        time_title, download_col = st.columns([0.8,0.2])

        with time_title:
            st.subheader(data["date"].strftime("%d-%m-%Y"),divider="rainbow")
            
        if len(data['img']) > 0:
            df = pd.DataFrame({
                "encroach_time" : [ d["date"] for d in data['img'] ],
                "backhoe_index" : [ d["backhoe_id"] for d in data['img'] ],
                "conf" : [ d["conf"] for d in data['img'] ]
            })
        else:
            df = pd.DataFrame({
                "encroach_time" : []
            })
            
        with download_col:
            df = df.to_csv(index=False).encode('utf-8')
            file_name = f'{data["date"]}'    
            if len(st.session_state.time_filter) > 0:
                from_time, to_time = getTimeFromSelection(
                    st.session_state.time_filter[
                        st.session_state.curr_time_index
                    ], curr_date
                )
                file_name += f'_{from_time.strftime("%H-%M")}'
            
            file_name += "_encroach_record.csv"
                
            st.download_button("ดาวน์โหลดประวัติการรุกล้ำ", 
                data=df, file_name=file_name, mime='text/csv', 
                disabled=(len(data['img']) == 0)
            )
        
        # show image gallery
        
        gallery_tab, graph_tab = st.tabs(["รูปภาพ", "แผนภูมิ"])
        
        with gallery_tab:
            
            if len(data["img"]) > 0:
                _, __, _page = st.columns(3)
                
                with _page:
                    with st.container():
                        st.caption("เลือกหน้า")
                        b_col, p_col, f_col = st.columns(3)
                        curr_img_len = len(
                            st.session_state.date_filter[
                                st.session_state.curr_date_index
                            ]['img'])
                        
                        with b_col: 
                            st.button(key="p_back",label="⬅️",
                                disabled=(st.session_state.curr_page_index == 0)
                            )
                            
                        with p_col: 
                            st.write(
                                (st.session_state.curr_page_index + 1)+"/"
                                +((curr_img_len // (grid_size * grid_size)) + 1)
                            )
                                
                        with f_col: 
                            st.button(key="p_fort",label="➡️",
                                disabled=(
                                (
                                    (st.session_state.curr_page_index + 1) 
                                    * (grid_size * grid_size)
                                 ) > 
                                    len(st.session_state.date_filter[
                                        st.session_state.curr_date_index]["img"]
                                    )
                                )
                            )
                
                for i in range(grid_size):                    
                    grid = st.columns(grid_size)
                    with st.container(border=True):
                        for j in range(grid_size):
                            page_ind = (
                                st.session_state.curr_page_index * (grid_size * grid_size)
                            )
                            index = (page_ind + (i * grid_size) + j)
                            if (index < len(data["img"])):
                                with grid[j]:
                                    st.image(
                                        data["img"][index]["img"],
                                        caption=str(data["img"][index]["date"].time())[:12]
                                    )
                            else:
                                break
                
        with graph_tab:
            
            arr_time_lab = list()
            arr_time_count = list()
            
            graph_header_text = ""
            
            if len(data["img"]) > 0:
                if len(st.session_state.time_filter) > 0:
                    
                    from_time, to_time = getTimeFromSelection(st.session_state.time_filter[
                        st.session_state.curr_time_index
                    ])
                    
                    graph_header_text = ("แสดงจำนวนการรุกล้ำ ตั้งแต่เวลา" +
                        from_time.strftime('%H:%M') + " ถึง " + to_time.strftime('%H:%M')
                    )
                    
                    c_time = from_time
                    while True:
                        if c_time == to_time:
                            break
                        else:
                            arr_time_lab.append(
                                c_time.strftime('%H:%M:%S')
                            )                    
                            
                            arr_time_count.append(                        
                                len(
                                    list(
                                        filter(
                                            lambda d : (d['date'].time() >= c_time.time()
                                                and d['date'].time() < (
                                                    c_time + dt.timedelta(seconds=10)).time()
                                            )
                                            ,data["img"]
                                        )
                                    )
                                )
                            )
                            
                            c_time += dt.timedelta(seconds=10)
                                        
                else:
                    graph_header_text = f"แสดงจำนวนการรุกล้ำของวันที่ {data['date']}"
                    
                    c_date =  dt.datetime.combine(data["date"], dt.datetime.min.time())
                    while True:
                        if c_date == dt.datetime.combine(
                                data["date"], dt.datetime.min.time()) + dt.timedelta(days=1):
                            break
                        else:
                            arr_time_lab.append(c_date.strftime('%H:%M'))                    
                            arr_time_count.append(                        
                                len(
                                    list(
                                        filter(
                                            lambda d : (d['date'] >= c_date
                                                and d['date'] < (
                                                    c_date + dt.timedelta(minutes=15)
                                                )
                                            )
                                            ,data["img"]
                                        )
                                    )
                                )
                            )
                            
                            c_date += dt.timedelta(minutes=15)
                
                st.write(graph_header_text)
                
                chart = alt.Chart(pd.DataFrame({
                    "time" : arr_time_lab,
                    "count" : arr_time_count
                })).mark_bar().encode(
                    x="time", y="count"
                )
                    
                st.altair_chart(chart, use_container_width=True)
                    
            else:
                st.write("ไม่มีข้อมูล")

with months_tab:
    
    with st.form(key="months_select"):
        
        button_col , months_col, years_col = st.columns([0.2, 0.4, 0.4])
        
        with button_col:
            st.form_submit_button("ค้นหา", type="primary", use_container_width=True)
        
        with months_col:
            options = ["ตลอดทั้งปี"]
            month_step = 3
            for i in range(0,12,month_step):
                options.append(f'{list(getMonthsSelect().keys())[i]} - {list(getMonthsSelect().keys())[i+month_step-1]}')
            month_select = st.selectbox("เลือกเดือน", options=options)
            
        with years_col:
            year_select = st.selectbox("เลือกปี", options=[2024])
        
    month_data = []
    y_count = []
    x_col = []
    if month_select == "ตลอดทั้งปี":
        month_data = query_month(years=year_select)
        
        for i in range(1,13,1):
            curr_month = list(getMonthsSelect().keys())[i-1]
            
            cm1 = dt.datetime(year_select, i, 1)
            cm2 = cm1 + relativedelta(months=1)
            
            x_col.append(curr_month)
            y_count.append(
                len(
                    list(
                        filter(
                            lambda d : (d["date"] >= cm1 and d["date"] < cm2)
                            ,month_data
                        )
                    )
                )
            )
    else:
        first_key, last_key =  [ m.strip() for m in month_select.split('-') ]
        
        month_array = [getMonthsSelect()[first_key]]
        
        _years = [ year_select, year_select ]
        if getMonthsSelect()[last_key] == 12:            
            
            month_array = month_array + [ _ for _ in range(
                getMonthsSelect()[first_key] + 1, getMonthsSelect()[last_key] + 1
            ) ]
            
            last_key = list(getMonthsSelect().keys())[0]
            _years[1] += 1
            
            month_array.append(1)
        
        else:
            last_key = getMonthsSelect()[last_key]
            last_key = list(getMonthsSelect().keys())[last_key]
            
            month_array = month_array + [ _ for _ in range(
                getMonthsSelect()[first_key] + 1, getMonthsSelect()[last_key] + 1
            ) ]

        month_data = query_month(
            years = _years,
            months=[getMonthsSelect()[first_key], getMonthsSelect()[last_key]]    
        )
        
        print(month_array)
        
        # group months
        for i in range(len(month_array) - 1):
            
            curr_month = list(getMonthsSelect().keys())[month_array[i] - 1]
            
            if (month_array[i + 1]) == 1:
                next_month = list(getMonthsSelect().keys())[0]
            else:
                next_month = list(getMonthsSelect().keys())[month_array[i]]
            
            cm1 = dt.datetime(year_select,month_array[i], 1)
            cm2 = cm1 + relativedelta(months=1)
            
            x_col.append(curr_month)
            y_count.append(
                len(
                    list(
                        filter(
                            lambda d : (d["date"] >= cm1 and d["date"] < cm2)
                            ,month_data
                        )
                    )
                )
            )
        
    graph_data = pd.DataFrame({
        "month" : x_col,
        "count" : y_count
    })
    
    chart = alt.Chart(graph_data).mark_bar().encode(
        x= alt.X(field="month", type="ordinal", sort= list(getMonthsSelect().keys()) ), 
        y="count"
    )
    
    st.altair_chart(chart, use_container_width=True)
    
with st.sidebar:
    
    logout_text = ""
    if "login_email" in st.session_state:
        st.subheader(st.session_state.login_email,divider="grey")
        if st.session_state.login_email == "แอดมิน":
            logout_text = "กลับหน้าแอดมิน"
        else:
            logout_text = "ออกจากระบบ"
    else:
        st.subheader("user",divider="grey")
        logout_text = "ออกจากระบบ"
    
    with st.popover(label=logout_text, use_container_width=True):
        if "login_email" in st.session_state:
            if st.session_state.login_email == "แอดมิน":
                st.markdown("กลับหน้าแอดมิน?")
            else:
                st.markdown("ยืนยันการออกจากระบบ?")
        else:
            st.markdown("ยืนยันการออกจากระบบ?")
            
        logout = st.button("ใช่" , use_container_width=True)
        
        
        if logout:
            back_to_login()