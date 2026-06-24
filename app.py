import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
from sqlalchemy import create_engine, text

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS
# ==========================================
st.set_page_config(page_title="MrGame | AI Telemetry", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Prompt:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Prompt', 'Outfit', sans-serif !important; }
        .stApp { background-color: #030712; color: #f1f5f9 !important; }
        .glass-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important; backdrop-filter: blur(20px) !important; border: 1px solid rgba(14, 165, 233, 0.2) !important; border-radius: 16px !important; padding: 35px !important; }
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE CONNECTION (Robust Engine)
# ==========================================
def get_db_engine():
    try:
        # ดึงจาก Secrets
        db_url = st.secrets["connections"]["supabase"]["url"]
        # สร้าง Engine พร้อม Connection Pooling เพื่อป้องกัน timeout
        return create_engine(db_url, connect_args={"sslmode": "require"}, pool_size=5, max_overflow=0)
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
        st.stop()

# ==========================================
# 2. AUTHENTICATION & APP
# ==========================================
def check_password():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if st.session_state.logged_in: return True
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><span class='text-gradient'>MrGame</span> Terminal</h2>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter ID")
        password = st.text_input("Password", type="password", placeholder="Enter Key")
        if st.button("SECURE LOGIN"):
            if username == "mrgame" and password == "Game2541$!!":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    return False

if check_password():
    engine = get_db_engine()

    # ดึงข้อมูล
    try:
        logs_df = pd.read_sql("SELECT * FROM fuel_logs ORDER BY date DESC, odometer DESC", engine)
        vehicles_df = pd.read_sql("SELECT name, fuel_type FROM vehicles", engine)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        st.stop()

    st.markdown("<h1 style='font-size: 2.2rem;'>ศูนย์วิเคราะห์ข้อมูลอัจฉริยะ <span class='text-gradient'>(Telemetry Center)</span></h1>", unsafe_allow_html=True)
    tab_entry, tab_dashboard, tab_records, tab_price = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_CLOUD", "[04] ราคาน้ำมันวันนี้"])

    with tab_entry:
        col_form, col_ocr = st.columns([1.2, 1])
        with col_form:
            with st.form(key='nexus_form'):
                form_date = st.date_input("วันเวลา", datetime.now())
                form_vehicle = st.selectbox("เลือกยานพาหนะ", vehicles_df['name'].tolist())
                form_odo = st.number_input("เลขไมล์ปัจจุบัน (กม.)", min_value=0.0, step=1.0)
                form_liters = st.number_input("ปริมาณเชื้อเพลิง (ลิตร)", min_value=0.0, step=0.01)
                form_price = st.number_input("ยอดชำระสุทธิ (บาท)", min_value=0.0, step=1.0)
                submit_btn = st.form_submit_button(label='ยืนยันการบันทึกข้อมูล')
            
            if submit_btn:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO fuel_logs (date, vehicle_name, odometer, liters, total_price) VALUES (:date, :v_name, :odo, :liters, :price)"), 
                                     {"date": form_date, "v_name": form_vehicle, "odo": form_odo, "liters": form_liters, "price": form_price})
                    st.success("บันทึกข้อมูลสำเร็จ!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"บันทึกข้อมูลล้มเหลว: {e}")

        with col_ocr:
            st.markdown('<div class="glass-card"><h4># ระบบอ่านใบเสร็จอัตโนมัติ (OCR)</h4></div>', unsafe_allow_html=True)

    with tab_dashboard:
        st.write("แดชบอร์ดสรุปข้อมูล")

    with tab_records:
        if not logs_df.empty:
            edited_df = st.data_editor(logs_df, use_container_width=True, key="fuel_editor")
            if st.button("บันทึกการแก้ไขไปยังฐานข้อมูล Cloud"):
                edited_df.to_sql('fuel_logs', engine, if_exists='replace', index=False)
                st.success("ซิงค์สำเร็จ!"); st.rerun()

    with tab_price:
        st.write("ข้อมูลราคาพลังงาน")