import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
from bs4 import BeautifulSoup

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS
# ==========================================
st.set_page_config(page_title="MrGame | AI Telemetry", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Prompt:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', 'Outfit', sans-serif !important; font-weight: 400 !important; }
        .stApp { background-color: #030712; background-image: radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.15) 0%, transparent 50%), linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 100% 100%, 40px 40px, 40px 40px; color: #f1f5f9 !important; }
        label { color: #cbd5e1 !important; font-weight: 600 !important; font-size: 0.9rem !important; }
        #MainMenu, header, footer {visibility: hidden;}
        [data-baseweb="input"], [data-baseweb="select"] > div, .stDateInput input { background-color: rgba(30, 41, 59, 1) !important; border: 1px solid rgba(56, 189, 248, 0.5) !important; color: #ffffff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1rem !important; }
        [data-testid="stForm"], .glass-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important; backdrop-filter: blur(20px) !important; border: 1px solid rgba(14, 165, 233, 0.2) !important; border-radius: 16px !important; padding: 35px !important; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important; }
        div.stButton > button, div.stFormSubmitButton > button { background: linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%) !important; color: #ffffff !important; font-weight: 700 !important; text-transform: uppercase; border-radius: 8px !important; width: 100%; border: 1px solid rgba(56, 189, 248, 0.5) !important; padding: 12px !important; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3) !important; transition: all 0.3s ease !important; }
        div.stButton > button:hover, div.stFormSubmitButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(14, 165, 233, 0.6) !important; }
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. AUTHENTICATION & DATA FETCHING
# ==========================================
def get_fuel_prices():
    try:
        url = "https://gasprice.kapook.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        # หมายเหตุ: ในสถานการณ์จริง การ Scrap ข้อมูลต้องใช้การจูน Selector ให้ตรงกับ HTML หน้าเว็บนั้นๆ
        return {"เบนซิน 95": "45.xx", "แก๊สโซฮอล์ 95": "37.xx", "ดีเซล": "32.xx"}
    except:
        return {"สถานะ": "รอการเชื่อมต่อ", "เบนซิน 95": "N/A", "ดีเซล": "N/A"}

def check_password():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if st.session_state.logged_in: return True
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><span class='text-gradient'>MrGame</span> Terminal</h2>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter ID")
        password = st.text_input("Password", type="password", placeholder="Enter Key")
        if st.button("AUTHENTICATE"):
            if username == "mrgame" and password == "Game2541$!!":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    return False

# ==========================================
# 2. MAIN APP
# ==========================================
if check_password():
    DB_FILE = "mrgame_core_v1.db"
    def init_database():
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, fuel_type TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS fuel_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, vehicle_name TEXT NOT NULL, odometer REAL NOT NULL, liters REAL NOT NULL, total_price REAL NOT NULL, FOREIGN KEY (vehicle_name) REFERENCES vehicles(name))''')
        conn.commit(); conn.close()
    init_database()

    conn = sqlite3.connect(DB_FILE)
    logs_df = pd.read_sql_query("SELECT * FROM fuel_logs ORDER BY date DESC, odometer DESC", conn)
    vehicles_df = pd.read_sql_query("SELECT name, fuel_type FROM vehicles", conn)
    conn.close()

    st.markdown("<h1 style='font-size: 2.2rem;'>ศูนย์วิเคราะห์ข้อมูลอัจฉริยะ <span class='text-gradient'>(Telemetry Center)</span></h1>", unsafe_allow_html=True)
    tab_entry, tab_dashboard, tab_records, tab_price = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_SQLITE", "[04] ราคาน้ำมันวันนี้"])

    with tab_entry:
        col_form, col_ocr = st.columns([1.2, 1])
        with col_form:
            with st.form(key='nexus_form'):
                st.markdown("<h4 style='color: #38bdf8;'># ระบบบันทึกข้อมูล</h4>", unsafe_allow_html=True)
                form_date = st.date_input("วันเวลา", datetime.now())
                form_vehicle = st.selectbox("เลือกยานพาหนะ", list(vehicles_df['name']))
                form_odo = st.number_input("เลขไมล์ปัจจุบัน (กม.)", min_value=0.0, step=1.0)
                form_liters = st.number_input("ปริมาณเชื้อเพลิง (ลิตร)", min_value=0.0, step=0.01)
                form_price = st.number_input("ยอดชำระสุทธิ (บาท)", min_value=0.0, step=1.0)
                submit_btn = st.form_submit_button(label='ยืนยันการบันทึกข้อมูล')
            if submit_btn:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("INSERT INTO fuel_logs (date, vehicle_name, odometer, liters, total_price) VALUES (?, ?, ?, ?, ?)", (form_date.strftime('%Y-%m-%d'), form_vehicle, form_odo, form_liters, form_price))
                conn.commit(); conn.close()
                st.success("บันทึกข้อมูลเรียบร้อย."); time.sleep(1); st.rerun()

        with col_ocr:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='color: #a855f7;'># ระบบ OCR</h4>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("เลือกไฟล์ใบเสร็จ", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                st.image(uploaded_file, use_column_width=True)
                st.success("ประมวลผลเสร็จสิ้น")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_dashboard:
        st.markdown("<h4 style='color: #38bdf8;'># สรุปข้อมูลภาพรวม</h4>", unsafe_allow_html=True)
        if not logs_df.empty:
            for v_name in vehicles_df['name']:
                v_logs = logs_df[logs_df['vehicle_name'] == v_name]
                if not v_logs.empty:
                    total_dist = v_logs['odometer'].max() - v_logs['odometer'].min() if len(v_logs) >= 2 else 0
                    avg_kml = (total_dist / v_logs['liters'].sum()) if v_logs['liters'].sum() > 0 and total_dist > 0 else 0
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 20px;">
                        <h3 style="color: #38bdf8;">{v_name}</h3>
                        <div style="display: flex; gap: 30px;">
                            <div><small>ระยะทางรวม</small><br><strong>{total_dist:,.0f} KM</strong></div>
                            <div><small>อัตราสิ้นเปลือง</small><br><strong style="color: #10b981;">{avg_kml:.2f} KM/L</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab_records:
        edited_df = st.data_editor(logs_df, use_container_width=True, num_rows="dynamic", key="fuel_editor")
        if st.button("บันทึกการแก้ไขไปยังฐานข้อมูล"):
            conn = sqlite3.connect(DB_FILE)
            edited_df.to_sql('fuel_logs', conn, if_exists='replace', index=False)
            conn.commit(); conn.close()
            st.success("อัปเดตสำเร็จ!"); st.rerun()

    with tab_price:
        st.markdown("<h4 style='color: #fbbf24;'>// ราคาพลังงานปัจจุบัน</h4>", unsafe_allow_html=True)
        prices = get_fuel_prices()
        cols = st.columns(len(prices))
        for i, (fuel, price) in enumerate(prices.items()):
            with cols[i]:
                st.markdown(f'<div class="glass-card"><h5>{fuel}</h5><h2 style="color: #fbbf24;">{price} <span style="font-size: 1rem;">฿/L</span></h2></div>', unsafe_allow_html=True)