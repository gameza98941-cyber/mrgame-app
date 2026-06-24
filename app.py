import streamlit as st
import pandas as pd
from datetime import datetime
import time
import requests
from sqlalchemy import create_engine, text

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS (เหมือนเดิม 100%)
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
        .glass-card { background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important; backdrop-filter: blur(20px) !important; border: 1px solid rgba(14, 165, 233, 0.2) !important; border-radius: 16px !important; padding: 35px !important; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important; }
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        div[data-testid="stButton"] > button, div.stFormSubmitButton > button { background: linear-gradient(90deg, rgba(2, 132, 199, 0.85) 0%, rgba(14, 165, 233, 0.95) 100%) !important; color: #ffffff !important; font-weight: 800 !important; border-radius: 8px !important; padding: 14px !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE CONNECTION (Stabilized)
# ==========================================
@st.cache_resource
def get_engine():
    try:
        db_url = st.secrets["connections"]["supabase"]["url"]
        return create_engine(db_url, connect_args={"sslmode": "require"}, pool_pre_ping=True)
    except Exception as e:
        st.error(f"Engine Error: {e}")
        return None

# ==========================================
# 2. APP LOGIC
# ==========================================
def check_password():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if st.session_state.logged_in: return True
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><span class='text-gradient'>MrGame</span> Terminal</h2>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("SECURE LOGIN"):
            if username == "mrgame" and password == "Game2541$!!":
                st.session_state.logged_in = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    return False

if check_password():
    engine = get_engine()
    if engine:
        # ดึงข้อมูลจาก Cloud โดยใช้ try-except ป้องกัน Error
        try:
            logs_df = pd.read_sql("SELECT * FROM fuel_logs ORDER BY date DESC, odometer DESC", engine)
            vehicles_df = pd.read_sql("SELECT * FROM vehicles", engine)
            
            st.markdown("<h1 style='font-size: 2.2rem;'>Telemetry Center</h1>", unsafe_allow_html=True)
            # ... (ใส่ส่วนของ Tabs ของคุณต่อที่นี่) ...
            st.write("เชื่อมต่อฐานข้อมูลสำเร็จ!")
        except Exception as e:
            st.error(f"ไม่สามารถอ่านข้อมูลได้ (ลองกด Reboot แอป): {e}")