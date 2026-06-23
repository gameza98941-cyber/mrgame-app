import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
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
        
        html, body, [class*="css"] { font-family: 'Prompt', 'Outfit', sans-serif !important; }
        
        .stApp { 
            background-color: #030712;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.15) 0%, transparent 50%),
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), 
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
            color: #e2e8f0; 
        }
        
        #MainMenu, header, footer {visibility: hidden;}
        
        .tech-font { font-family: 'JetBrains Mono', monospace !important; letter-spacing: -0.5px; }

        [data-testid="stForm"], .glass-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(14, 165, 233, 0.15) !important;
            border-radius: 16px !important;
            padding: 35px !important;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        }
        
        [data-baseweb="input"], [data-baseweb="select"] > div {
            background-color: rgba(0, 0, 0, 0.6) !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            border-radius: 8px !important; 
            color: #38bdf8 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* แก้ไขปุ่ม: ครอบคลุมทั้งปุ่มปกติและปุ่ม Submit ใน Form */
        div.stButton > button, div.stFormSubmitButton > button {
            background: linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%) !important;
            color: #ffffff !important; 
            font-weight: 700 !important; 
            text-transform: uppercase;
            border-radius: 8px !important; 
            width: 100%;
            border: 1px solid rgba(56, 189, 248, 0.5) !important;
            padding: 10px !important;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3), inset 0 1px 0 rgba(255,255,255,0.2) !important;
        }
        
        div.stButton > button:hover, div.stFormSubmitButton > button:hover { 
            transform: translateY(-2px) !important; 
            box-shadow: 0 8px 25px rgba(14, 165, 233, 0.6) !important;
            border: 1px solid rgba(56, 189, 248, 0.8) !important;
        }
        
        .text-gradient { 
            background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
        }
        
        .stTabs [data-baseweb="tab-list"] { background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 16px; padding: 8px; gap: 12px; }
        .stTabs [data-baseweb="tab"] { background: rgba(15, 23, 42, 0.5); color: #64748b; border-radius: 10px; padding: 10px 24px; }
        .stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(2, 132, 199, 0.4) 0%, rgba(14, 165, 233, 0.1) 100%) !important; color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.6) !important; }
        .ai-status { animation: pulse-glow 2s infinite; }
        @keyframes pulse-glow { 0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); } 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. AUTHENTICATION
# ==========================================
def check_password():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        return True

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
            else:
                st.error("Access Denied: Invalid Credentials")
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

    def calculate_realtime_metrics(vehicle_name, current_odo, current_liters, current_price):
        prev_odo, _ = get_latest_data(vehicle_name)
        if prev_odo > 0 and current_odo > prev_odo:
            distance = current_odo - prev_odo
            return distance / current_liters, current_price / distance, distance
        return None, None, None

    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 25px 0;'>
                <div style='display: inline-block; padding: 10px 20px; border: 1px solid rgba(14, 165, 233, 0.4); border-radius: 8px; background: rgba(14, 165, 233, 0.05); margin-bottom: 15px; box-shadow: inset 0 0 20px rgba(14, 165, 233, 0.1);'>
                    <h2 style='color: #f8fafc; margin: 0; font-weight: 800; font-size: 1.8rem; letter-spacing: 2px;'>MrGame<span style='color: #38bdf8;'>_</span></h2>
                </div>
                <p style='color: #94a3b8; font-size: 0.75rem; font-family: "JetBrains Mono", monospace; letter-spacing: 1px;'>โหนดวิเคราะห์ข้อมูลยานพาหนะ</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <div style='background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(16, 185, 129, 0.3); padding: 15px; border-radius: 8px; display: flex; align-items: center; gap: 12px;'>
                <div class='ai-status' style='width: 10px; height: 10px; border-radius: 50%; background-color: #10b981;'></div>
                <div style='display: flex; flex-direction: column;'>
                    <span style='color: #10b981; font-size: 0.8rem; font-weight: 700; letter-spacing: 1px;'>ระบบ AI พร้อมทำงาน</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    conn = sqlite3.connect(DB_FILE)
    logs_df = pd.read_sql_query("SELECT * FROM fuel_logs ORDER BY date DESC, odometer DESC", conn)
    vehicles_df = pd.read_sql_query("SELECT name, fuel_type FROM vehicles", conn)
    conn.close()

    st.markdown("""
        <div style='padding-top: 10px; padding-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px;'>
            <h1 style='margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -1px;'><span class='text-gradient'>ศูนย์ควบคุม</span> หลัก</h1>
        </div>
    """, unsafe_allow_html=True)

    tab_entry, tab_dashboard, tab_records = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_SQLITE"])

    with tab_entry:
        col_form, col_ocr = st.columns([1.2, 1])
        with col_form:
            with st.form(key='nexus_form'):
                st.markdown("<h4 style='color: #f8fafc; font-weight: 600; margin-bottom: 25px; letter-spacing: 1px;'><span style='color: #38bdf8;'>#</span> นำเข้าข้อมูลอย่างปลอดภัย</h4>", unsafe_allow_html=True)
                form_date = st.date_input("วันและเวลาที่บันทึก", datetime.now())
                v_options = {row['name']: row['fuel_type'] for _, row in vehicles_df.iterrows()}
                form_vehicle = st.selectbox("เลือกยานพาหนะ", list(v_options.keys()))
                last_odo, _ = get_latest_data(form_vehicle)
                st.markdown(f"""
                    <div style='background: rgba(14, 165, 233, 0.05); border-left: 3px solid #0ea5e9; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px;'>
                        <span style='color: #64748b; font-size: 0.75rem; font-family: "JetBrains Mono", monospace;'>SYS.เลขไมล์ล่าสุด</span><br>
                        <span class='tech-font' style='color: #38bdf8; font-size: 1.3rem; font-weight: 700;'>{last_odo:,.1f} KM</span>
                    </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: form_odo = st.number_input("เลขไมล์ปัจจุบัน (กม.)", min_value=0.0, step=1.0)
                with c2: form_liters = st.number_input("ปริมาณเชื้อเพลิง (ลิตร)", min_value=0.0, step=0.01)
                form_price = st.number_input("ยอดชำระสุทธิ (บาท)", min_value=0.0, step=1.0)
                submit_btn = st.form_submit_button(label='ประมวลผลคำสั่ง')
            if submit_btn:
                if form_odo <= last_odo and last_odo > 0:
                    st.error(f"ข้อผิดพลาด: เลขไมล์ปัจจุบันต้องมากกว่าเลขไมล์เดิม ({last_odo:,.1f} กม.)")
                elif form_odo <= 0 or form_liters <= 0 or form_price <= 0:
                    st.error("ข้อผิดพลาด: ตรวจพบค่าว่างหรือศูนย์ในระบบ กรุณากรอกให้ครบถ้วน")
                else:
                    kml, cpkm, dist = calculate_realtime_metrics(form_vehicle, form_odo, form_liters, form_price)
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO fuel_logs (date, vehicle_name, odometer, liters, total_price) VALUES (?, ?, ?, ?, ?)", (form_date.strftime('%Y-%m-%d'), form_vehicle, form_odo, form_liters, form_price))
                    conn.commit()
                    conn.close()
                    st.success("บันทึกข้อมูลลงฐานข้อมูลเรียบร้อยแล้ว.")
                    time.sleep(1)
                    st.rerun()

        with col_ocr:
            st.markdown("<h4 style='color: #f8fafc; font-weight: 600; margin-bottom: 25px; letter-spacing: 1px;'><span style='color: #a855f7;'>#</span> ระบบสแกนใบเสร็จ_OCR</h4>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background: rgba(15, 23, 42, 0.4); border: 1px dashed rgba(168, 85, 247, 0.4); border-radius: 8px; padding: 25px; text-align: center;'>
                <div style='font-size: 30px; margin-bottom: 10px;'>📷</div>
                <p style='color: #94a3b8; font-size: 0.85rem; font-family: "JetBrains Mono", monospace;'>รอรับไฟล์ภาพเพื่อประมวลผลด้วย TESSERACT</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_dashboard:
        if not logs_df.empty:
            p_cols = st.columns(len(vehicles_df))
            for idx, row in vehicles_df.iterrows():
                v_name = row['name']
                v_logs = logs_df[logs_df['vehicle_name'] == v_name].sort_values('date')
                with p_cols[idx]:
                    if len(v_logs) >= 3:
                        v_logs['date'] = pd.to_datetime(v_logs['date'])
                        days_diff = (v_logs['date'].max() - v_logs['date'].min()).days
                        if days_diff > 0:
                            total_cost = v_logs['total_price'].sum()
                            est_monthly_cost = (total_cost / days_diff) * 30
                            st.markdown(f"""
                            <div class="glass-card" style="border-top: 3px solid #c084fc !important; padding: 25px !important;">
                                <h5 style="color: #e9d5ff; margin: 0 0 10px 0;">{v_name}</h5>
                                <h2 class="tech-font" style="color: #f8fafc; font-weight: 800; margin: 5px 0;">฿ {est_monthly_cost:,.0f}</h2>
                            </div>
                            """, unsafe_allow_html=True)

    with tab_records:
        if not logs_df.empty:
            display_df = logs_df.copy()
            display_df.columns = ['รหัส', 'วันเวลา', 'ยานพาหนะ', 'เลขไมล์ (กม.)', 'ปริมาณ (ลิตร)', 'ยอดชำระ (บาท)']
            st.dataframe(display_df, use_container_width=True, hide_index=True)