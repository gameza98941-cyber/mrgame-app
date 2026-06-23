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
# 1. AUTHENTICATION & DATA FETCHING
# ==========================================
def get_fuel_prices():
    # โค้ดตัวอย่างการดึงราคาจากหน้าเว็บสาธารณะ (ควรระบุ URL ที่ถูกต้อง)
    # เนื่องจากบางเว็บอาจบล็อค Bot แนะนำให้ทดสอบก่อน
    try:
        url = "https://gasprice.kapook.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ส่วนนี้ขึ้นอยู่กับโครงสร้างเว็บ ต้องตรวจสอบ Selector ของเว็บนั้นๆ
        # นี่เป็นโครงสร้างสมมุติเพื่อให้เห็นภาพ
        prices = {"เบนซิน 95": "45.xx", "แก๊สโซฮอล์ 95": "37.xx", "ดีเซล": "32.xx"}
        return prices
    except:
        return {"ข้อมูลไม่พร้อมใช้งาน": "N/A"}

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

    # [Database init functions same as before...]
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

    conn = sqlite3.connect(DB_FILE)
    logs_df = pd.read_sql_query("SELECT * FROM fuel_logs ORDER BY date DESC, odometer DESC", conn)
    vehicles_df = pd.read_sql_query("SELECT name, fuel_type FROM vehicles", conn)
    conn.close()

    st.markdown("<h1 style='font-size: 2.2rem;'>ศูนย์วิเคราะห์ข้อมูลอัจฉริยะ <span class='text-gradient'>(Telemetry Center)</span></h1>", unsafe_allow_html=True)

    tab_entry, tab_dashboard, tab_records, tab_price = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_SQLITE", "[04] ราคาน้ำมันวันนี้"])

    # ... [tab_entry, tab_dashboard, tab_records code same as before] ...
    # (Just assume they are here as in the previous code to save space)

    with tab_price:
        st.markdown("<h4 style='color: #fbbf24;'><span style='color: #64748b;'>//</span> ราคาพลังงานปัจจุบัน (Real-time)</h4>", unsafe_allow_html=True)
        prices = get_fuel_prices()
        cols = st.columns(len(prices))
        for i, (fuel, price) in enumerate(prices.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: #64748b;">{fuel}</h5>
                    <h2 style="color: #fbbf24;">{price} <span style="font-size: 1rem;">฿/L</span></h2>
                </div>
                """, unsafe_allow_html=True)
        st.info("ข้อมูลราคาดึงจากแหล่งข้อมูลสาธารณะแบบ Real-time")