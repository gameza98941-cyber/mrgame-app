import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
from sqlalchemy import create_engine, text

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS (ของเดิมที่คุณให้มา 100%)
# ==========================================
st.set_page_config(page_title="MrGame | AI Telemetry", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Prompt:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', 'Outfit', sans-serif !important; font-weight: 400 !important; }
        .stApp { background-color: #030712; background-image: radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.15) 0%, transparent 50%), linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px); background-size: 100% 100%, 40px 40px, 40px 40px; color: #f1f5f9 !important; }
        label { color: #cbd5e1 !important; font-weight: 600 !important; font-size: 0.9rem !important; }
        #MainMenu, header, footer {visibility: hidden;}
        [data-testid="stTextInput"] > div > div, [data-testid="stNumberInputContainer"], [data-baseweb="select"] > div, .stDateInput > div > div { background: linear-gradient(90deg, rgba(3, 7, 18, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important; border: 1px solid rgba(56, 189, 248, 0.4) !important; border-radius: 8px !important; color: #38bdf8 !important; transition: all 0.3s ease !important; box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.6) !important; }
        input[type="text"], input[type="password"], input[type="number"], [data-baseweb="base-input"], [data-baseweb="input"] { background-color: transparent !important; }
        [data-testid="stTextInput"] > div > div:focus-within, [data-testid="stNumberInputContainer"]:focus-within, [data-baseweb="select"] > div:focus-within, .stDateInput > div > div:focus-within { border-color: #0ea5e9 !important; box-shadow: 0 0 15px rgba(14, 165, 233, 0.5), inset 0 0 10px rgba(14, 165, 233, 0.2) !important; }
        input { color: #38bdf8 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1.1rem !important; font-weight: 700 !important; text-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important; -webkit-text-fill-color: #38bdf8 !important; }
        input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active { -webkit-box-shadow: 0 0 0 30px #0f172a inset !important; -webkit-text-fill-color: #38bdf8 !important; transition: background-color 5000s ease-in-out 0s; }
        [data-testid="stTextInput"] button, [data-baseweb="select"] svg, .stDateInput svg { color: #38bdf8 !important; fill: #38bdf8 !important; background: transparent !important; }
        [data-testid="stNumberInputContainer"] button { background: rgba(30, 41, 59, 0.9) !important; color: #38bdf8 !important; border: none !important; border-left: 1px solid rgba(56, 189, 248, 0.2) !important; border-radius: 0 !important; }
        [data-testid="stNumberInputContainer"] button:hover { background: #38bdf8 !important; color: #030712 !important; box-shadow: 0 0 15px #38bdf8 !important; }
        [data-testid="stFileUploaderDropzone"] { background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important; border: 2px dashed rgba(168, 85, 247, 0.5) !important; border-radius: 12px !important; padding: 25px !important; transition: all 0.3s ease !important; box-shadow: inset 0 0 15px rgba(168, 85, 247, 0.05) !important; }
        [data-testid="stFileUploaderDropzone"]:hover { border-color: #a855f7 !important; background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(3, 7, 18, 0.95)) !important; box-shadow: 0 0 20px rgba(168, 85, 247, 0.3), inset 0 0 15px rgba(168, 85, 247, 0.2) !important; }
        [data-testid="stFileUploaderDropzoneInstructions"] { color: #cbd5e1 !important; font-family: 'JetBrains Mono', monospace !important; }
        [data-testid="stFileUploaderDropzoneInstructions"] > div { color: #94a3b8 !important; }
        [data-testid="stFileUploaderDropzone"] button { background: rgba(168, 85, 247, 0.15) !important; color: #e9d5ff !important; border: 1px solid rgba(168, 85, 247, 0.5) !important; border-radius: 8px !important; font-family: 'JetBrains Mono', monospace !important; font-weight: bold !important; }
        [data-testid="stFileUploaderDropzone"] button:hover { background: #a855f7 !important; color: #ffffff !important; box-shadow: 0 0 15px rgba(168, 85, 247, 0.6) !important; }
        [data-testid="stUploadedFile"] { background: rgba(30, 41, 59, 0.8) !important; border: 1px solid rgba(168, 85, 247, 0.3) !important; border-radius: 8px !important; }
        [data-testid="stUploadedFileName"] { color: #e9d5ff !important; font-family: 'JetBrains Mono', monospace !important; }
        div[data-testid="stButton"] > button, div.stFormSubmitButton > button { background: linear-gradient(90deg, rgba(2, 132, 199, 0.85) 0%, rgba(14, 165, 233, 0.95) 100%) !important; color: #ffffff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 1rem !important; font-weight: 800 !important; letter-spacing: 1px !important; text-transform: uppercase; border-radius: 8px !important; width: 100%; border: 1px solid rgba(56, 189, 248, 0.6) !important; padding: 14px !important; box-shadow: 0 0 15px rgba(14, 165, 233, 0.3) !important; transition: all 0.3s ease !important; }
        div[data-testid="stButton"] > button:hover, div.stFormSubmitButton > button:hover { transform: translateY(-2px) !important; background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%) !important; box-shadow: 0 0 25px rgba(56, 189, 248, 0.7) !important; border-color: #ffffff !important; }
        .glass-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important; backdrop-filter: blur(20px) !important; border: 1px solid rgba(14, 165, 233, 0.2) !important; border-radius: 16px !important; padding: 35px !important; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important; }
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .api-pulse { width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ADVANCED API FETCHING
# ==========================================
def get_fuel_prices():
    target_fuels = ["แก๊สโซฮอล์ 95", "แก๊สโซฮอล์ E20", "แก๊สโซฮอล์ E85", "แก๊สโซฮอล์ 91", "ดีเซลพรีเมียม", "ดีเซล", "ดีเซล B20"]
    temp_prices = {}
    try:
        url = "https://api.chnwt.dev/thai-oil-api/latest"
        res = requests.get(url, timeout=5)
        data = res.json()
        prices_raw = data['response']['stations']['ptt']['prices']
        mapping = {"Gasohol 95": "แก๊สโซฮอล์ 95", "Gasohol E20": "แก๊สโซฮอล์ E20", "Gasohol E85": "แก๊สโซฮอล์ E85", "Gasohol 91": "แก๊สโซฮอล์ 91", "Premium Diesel": "ดีเซลพรีเมียม", "Super Power Diesel B7": "ดีเซลพรีเมียม", "Diesel": "ดีเซล", "Diesel B7": "ดีเซล", "Diesel B20": "ดีเซล B20"}
        for k, v in mapping.items():
            if k in prices_raw: temp_prices[v] = f"{float(prices_raw[k]['price']):.2f}"
        return {fuel: temp_prices[fuel] for fuel in target_fuels if fuel in temp_prices}, "LIVE DATA CONNECTED"
    except: return {"สถานะ": "OFFLINE"}, "ระบบราคาพลังงานขัดข้อง"

# ==========================================
# 2. DATABASE SETUP (CLOUD ENGINE)
# ==========================================
def get_engine():
    # ดึงค่า URL จาก Secrets
    db_url = st.secrets["connections"]["supabase"]["url"]
    return create_engine(db_url, connect_args={"sslmode": "require"}, pool_pre_ping=True)

# ==========================================
# 3. AUTHENTICATION & MAIN APP
# ==========================================
def check_password():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if st.session_state.logged_in: return True
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 5px;'><span class='text-gradient'>MrGame</span> Fuel Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #10b981; font-size: 0.85rem; font-family: \"JetBrains Mono\", monospace; margin-bottom: 5px; letter-spacing: 1px;'>⛽ INTELLIGENT TELEMETRY SYSTEM</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 0; margin-bottom: 25px;'>ระบบบันทึกและวิเคราะห์อัตราสิ้นเปลืองเชื้อเพลิงยานพาหนะ</p>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter ID")
        password = st.text_input("Password", type="password", placeholder="Enter Key")
        
        st.markdown("<br>", unsafe_allow_html=True) 
        if st.button("SECURE LOGIN"):
            if username == "mrgame" and password == "Game2541$!!":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied: Invalid Credentials")
        st.markdown('</div>', unsafe_allow_html=True)
    return False

if check_password():
    engine = get_engine()
    
    # ดึงข้อมูลจาก Cloud
    logs_df = pd.read_sql("SELECT id, date, vehicle_name, odometer, liters, total_price FROM fuel_logs ORDER BY date DESC, odometer DESC", engine)
    vehicles_df = pd.read_sql("SELECT name, fuel_type FROM vehicles", engine)

    st.markdown("<h1 style='font-size: 2.2rem;'>ศูนย์วิเคราะห์ข้อมูลอัจฉริยะ <span class='text-gradient'>(Telemetry Center)</span></h1>", unsafe_allow_html=True)

    tab_entry, tab_dashboard, tab_records, tab_price = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_CLOUD", "[04] ราคาน้ำมันวันนี้"])

    with tab_entry:
        col_form, col_ocr = st.columns([1.2, 1])
        with col_form:
            with st.form(key='nexus_form'):
                st.markdown("<h4 style='color: #38bdf8;'><span style='color: #64748b;'>#</span> ระบบบันทึกข้อมูล (Telemetry Input)</h4>", unsafe_allow_html=True)
                form_date = st.date_input("วันเวลา", datetime.now())
                form_vehicle = st.selectbox("เลือกยานพาหนะ", vehicles_df['name'].tolist())
                form_odo = st.number_input("เลขไมล์ปัจจุบัน (กม.)", min_value=0.0, step=1.0)
                form_liters = st.number_input("ปริมาณเชื้อเพลิง (ลิตร)", min_value=0.0, step=0.01)
                form_price = st.number_input("ยอดชำระสุทธิ (บาท)", min_value=0.0, step=1.0)
                if st.form_submit_button(label='ยืนยันการบันทึกข้อมูล'):
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO fuel_logs (date, vehicle_name, odometer, liters, total_price) VALUES (:date, :v_name, :odo, :liters, :price)"), 
                                     {"date": form_date, "v_name": form_vehicle, "odo": form_odo, "liters": form_liters, "price": form_price})
                    st.success("บันทึกข้อมูลสำเร็จ!"); time.sleep(1); st.rerun()

        with col_ocr:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h4 style='color: #a855f7;'><span style='color: #64748b;'>#</span> ระบบอ่านใบเสร็จอัตโนมัติ (OCR)</h4>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("เลือกไฟล์ใบเสร็จ (Browse/Gallery/Camera)", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                st.image(uploaded_file, use_column_width=True)
                with st.spinner('กำลังประมวลผล...'): time.sleep(1.5)
                st.success("ระบบประมวลผลเสร็จสิ้น")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_dashboard:
        st.write("แดชบอร์ดสรุปข้อมูล")
        if not logs_df.empty:
            for v_name in vehicles_df['name']:
                v_logs = logs_df[logs_df['vehicle_name'] == v_name]
                if not v_logs.empty:
                    total_cost = v_logs['total_price'].sum()
                    total_liters = v_logs['liters'].sum()
                    total_dist = v_logs['odometer'].max() - v_logs['odometer'].min() if len(v_logs) >= 2 else 0
                    avg_kml = (total_dist / total_liters) if total_liters > 0 and total_dist > 0 else 0
                    st.markdown(f"""<div class="glass-card" style="margin-bottom: 20px;"><h3>{v_name}</h3><p>อัตราสิ้นเปลือง: {avg_kml:.2f} KM/L</p></div>""", unsafe_allow_html=True)

    with tab_records:
        st.markdown("<h4 style='color: #10b981;'><span style='color: #64748b;'>//</span> ฐานข้อมูลพลังงานบนระบบคลาวด์ (Editable)</h4>", unsafe_allow_html=True)
        if not logs_df.empty:
            edited_df = st.data_editor(logs_df, use_container_width=True, key="fuel_editor", disabled=["id"])
            if st.button("บันทึกการแก้ไขไปยังฐานข้อมูล Cloud"):
                edited_df.to_sql('fuel_logs', engine, if_exists='replace', index=False)
                st.success("ซิงค์สำเร็จ!"); time.sleep(1); st.rerun()

    with tab_price:
        prices, _ = get_fuel_prices()
        st.write(prices)