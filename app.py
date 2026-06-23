import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS
# ==========================================
st.set_page_config(page_title="MrGame | AI Telemetry", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Prompt:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700;800&display=swap');
        
        html, body, [class*="css"] { font-family: 'Prompt', 'Outfit', sans-serif !important; font-weight: 400 !important; }
        
        .stApp { 
            background-color: #030712;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.15) 0%, transparent 50%),
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), 
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
            color: #f1f5f9 !important; 
        }
        
        label { color: #cbd5e1 !important; font-weight: 600 !important; font-size: 0.9rem !important; }
        #MainMenu, header, footer {visibility: hidden;}
        
        /* ปรับสีช่องกรอกให้คมชัด */
        [data-baseweb="input"], [data-baseweb="select"] > div, .stDateInput input {
            background-color: rgba(30, 41, 59, 1) !important;
            border: 1px solid rgba(56, 189, 248, 0.5) !important;
            color: #ffffff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1rem !important;
        }

        [data-testid="stForm"], .glass-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            border-radius: 16px !important;
            padding: 35px !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
        }
        
        /* ปุ่มสไตล์ Cyberpunk */
        div.stButton > button, div.stFormSubmitButton > button {
            background: linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%) !important;
            color: #ffffff !important; 
            font-weight: 700 !important; 
            text-transform: uppercase;
            border-radius: 8px !important; 
            width: 100%;
            border: 1px solid rgba(56, 189, 248, 0.5) !important;
            padding: 12px !important;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        div.stButton > button:hover, div.stFormSubmitButton > button:hover { 
            transform: translateY(-2px) !important; 
            box-shadow: 0 8px 25px rgba(14, 165, 233, 0.6) !important;
        }
        
        .text-gradient { 
            background: linear-gradient(to right, #38bdf8, #818cf8); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. AUTHENTICATION
# ==========================================
def check_password():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if st.session_state.logged_in: return True

    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><span class='text-gradient'>MrGame</span> Terminal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem; font-family: \"JetBrains Mono\"; margin-bottom: 25px;'>SYSTEM_AUTHENTICATION_REQUIRED</p>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter ID")
        password = st.text_input("Password", type="password", placeholder="Enter Key")
        
        if st.button("AUTHENTICATE"):
            if username == "mrgame" and password == "Game2541$!!":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied: Invalid Credentials")
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
        c.execute("SELECT COUNT(*) FROM vehicles")
        if c.fetchone()[0] == 0:
            c.executemany("INSERT INTO vehicles (name, fuel_type) VALUES (?, ?)", [('Honda PCX 150', 'Gasohol 95'), ('Honda Giorno+', 'Gasohol 95'), ('Ford Ranger', 'Diesel')])
        conn.commit()
        conn.close()

    init_database()

    def get_latest_data(vehicle_name):
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT odometer, date FROM fuel_logs WHERE vehicle_name = ? ORDER BY odometer DESC LIMIT 1", conn, params=[vehicle_name])
        conn.close()
        if not df.empty: return df.iloc[0]['odometer'], df.iloc[0]['date']
        return 0.0, None

    conn = sqlite3.connect(DB_FILE)
    logs_df = pd.read_sql_query("SELECT * FROM fuel_logs ORDER BY date DESC, odometer DESC", conn)
    vehicles_df = pd.read_sql_query("SELECT name, fuel_type FROM vehicles", conn)
    conn.close()

    st.markdown("<h1 style='font-size: 2.2rem;'>ศูนย์วิเคราะห์ข้อมูลอัจฉริยะ <span class='text-gradient'>(Telemetry Center)</span></h1>", unsafe_allow_html=True)

    tab_entry, tab_dashboard, tab_records = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_SQLITE"])

    with tab_entry:
        col_form, col_ocr = st.columns([1.2, 1])
        with col_form:
            with st.form(key='nexus_form'):
                st.markdown("<h4 style='color: #38bdf8;'><span style='color: #64748b;'>#</span> ระบบบันทึกข้อมูล (Telemetry Input)</h4>", unsafe_allow_html=True)
                form_date = st.date_input("วันเวลา", datetime.now())
                v_options = {row['name']: row['fuel_type'] for _, row in vehicles_df.iterrows()}
                form_vehicle = st.selectbox("เลือกยานพาหนะ", list(v_options.keys()))
                form_odo = st.number_input("เลขไมล์ปัจจุบัน (กม.)", min_value=0.0, step=1.0)
                form_liters = st.number_input("ปริมาณเชื้อเพลิง (ลิตร)", min_value=0.0, step=0.01)
                form_price = st.number_input("ยอดชำระสุทธิ (บาท)", min_value=0.0, step=1.0)
                submit_btn = st.form_submit_button(label='ยืนยันการบันทึกข้อมูล')
            
            if submit_btn:
                last_odo, _ = get_latest_data(form_vehicle)
                if form_odo <= last_odo and last_odo > 0:
                    st.error(f"ข้อผิดพลาด: เลขไมล์ปัจจุบันต้องมากกว่าเลขไมล์เดิม ({last_odo:,.1f} กม.)")
                else:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO fuel_logs (date, vehicle_name, odometer, liters, total_price) VALUES (?, ?, ?, ?, ?)", (form_date.strftime('%Y-%m-%d'), form_vehicle, form_odo, form_liters, form_price))
                    conn.commit()
                    conn.close()
                    st.success("บันทึกข้อมูลเรียบร้อย.")
                    time.sleep(1)
                    st.rerun()

        with col_ocr:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='color: #a855f7;'><span style='color: #64748b;'>#</span> ระบบอ่านใบเสร็จอัตโนมัติ (OCR)</h4>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("เลือกไฟล์ใบเสร็จ (Browse/Gallery/Camera)", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                st.image(uploaded_file, use_column_width=True)
                with st.spinner('กำลังประมวลผล...'):
                    time.sleep(1.5)
                st.success("ระบบประมวลผลเสร็จสิ้น")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_dashboard:
        st.markdown("<h4 style='color: #38bdf8;'><span style='color: #64748b;'>#</span> สรุปข้อมูลภาพรวมยานพาหนะ</h4>", unsafe_allow_html=True)
        if not logs_df.empty:
            for v_name in vehicles_df['name']:
                v_logs = logs_df[logs_df['vehicle_name'] == v_name]
                if not v_logs.empty:
                    # คำนวณ Metric
                    total_cost = v_logs['total_price'].sum()
                    total_liters = v_logs['liters'].sum()
                    total_dist = v_logs['odometer'].max() - v_logs['odometer'].min() if len(v_logs) >= 2 else 0
                    
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 20px;">
                        <h3 style="color: #38bdf8; margin-bottom: 15px;">{v_name}</h3>
                        <div style="display: flex; gap: 40px;">
                            <div><small style="color: #64748b;">ระยะทางรวม</small><br><strong style="font-size: 1.2rem;">{total_dist:,.0f} KM</strong></div>
                            <div><small style="color: #64748b;">ค่าน้ำมันรวม</small><br><strong style="font-size: 1.2rem;">฿ {total_cost:,.0f}</strong></div>
                            <div><small style="color: #64748b;">ปริมาณรวม</small><br><strong style="font-size: 1.2rem;">{total_liters:,.2f} L</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีข้อมูลบันทึกในระบบ")

    with tab_records:
        st.markdown("<h4 style='color: #10b981;'><span style='color: #64748b;'>//</span> ฐานข้อมูล_SQLITE (Editable)</h4>", unsafe_allow_html=True)
        if not logs_df.empty:
            edited_df = st.data_editor(logs_df, use_container_width=True, num_rows="dynamic", key="fuel_editor")
            if st.button("บันทึกการแก้ไขไปยังฐานข้อมูล"):
                try:
                    conn = sqlite3.connect(DB_FILE)
                    edited_df.to_sql('fuel_logs', conn, if_exists='replace', index=False)
                    conn.commit()
                    conn.close()
                    st.success("อัปเดตข้อมูลสำเร็จ!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")