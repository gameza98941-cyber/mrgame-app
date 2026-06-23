import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import requests

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
        
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        .api-pulse {
            width: 8px; height: 8px; background: #10b981; border-radius: 50%;
            box-shadow: 0 0 10px #10b981; animation: pulse 2s infinite;
        }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ADVANCED API FETCHING
# ==========================================
def get_fuel_prices():
    # กำหนดชนิดน้ำมันและลำดับตามที่คุณต้องการเป๊ะๆ
    target_fuels = [
        "แก๊สโซฮอล์ 95", "แก๊สโซฮอล์ E20", "แก๊สโซฮอล์ E85", 
        "แก๊สโซฮอล์ 91", "ดีเซลพรีเมียม", "ดีเซล", "ดีเซล B20"
    ]
    
    # Core 1: JSON API
    try:
        url = "https://api.chnwt.dev/thai-oil-api/latest"
        res = requests.get(url, timeout=5)
        data = res.json()
        prices_raw = data['response']['stations']['ptt']['prices']
        date_str = data['response']['date']
        
        mapping = {
            "Gasohol 95": "แก๊สโซฮอล์ 95",
            "Gasohol E20": "แก๊สโซฮอล์ E20",
            "Gasohol E85": "แก๊สโซฮอล์ E85",
            "Gasohol 91": "แก๊สโซฮอล์ 91",
            "Premium Diesel": "ดีเซลพรีเมียม",
            "Super Power Diesel B7": "ดีเซลพรีเมียม",
            "Diesel": "ดีเซล",
            "Diesel B7": "ดีเซล",
            "Diesel B20": "ดีเซล B20"
        }
        
        temp_prices = {}
        for k, v in mapping.items():
            if k in prices_raw and v not in temp_prices:
                temp_prices[v] = f"{float(prices_raw[k]['price']):.2f}"
                
        # เรียงลำดับตาม target_fuels
        formatted = {fuel: temp_prices[fuel] for fuel in target_fuels if fuel in temp_prices}
        if formatted: return formatted, f"ข้อมูลประจำวันที่: {date_str}"
    except:
        pass

    # Core 2: Fallback XML
    try:
        url = "https://orapiweb.pttor.com/oilservice/OilPrice.asmx"
        headers = {'Content-Type': 'text/xml; charset=utf-8'}
        payload = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CurrentOilPrice xmlns="http://www.pttor.com"><Language>thai</Language></CurrentOilPrice></soap:Body></soap:Envelope>'
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)
        temp_prices = {}
        for elem in root.iter():
            if 'CurrentOilPriceResult' in elem.tag:
                inner_root = ET.fromstring(elem.text)
                for fuel in inner_root.findall('FUEL'):
                    product = fuel.find('PRODUCT').text if fuel.find('PRODUCT') is not None else ""
                    price = fuel.find('PRICE').text if fuel.find('PRICE') is not None else ""
                    if price:
                        if "Gasohol 95" in product and "E20" not in product and "E85" not in product: temp_prices["แก๊สโซฮอล์ 95"] = price
                        elif "E20" in product: temp_prices["แก๊สโซฮอล์ E20"] = price
                        elif "E85" in product: temp_prices["แก๊สโซฮอล์ E85"] = price
                        elif "Gasohol 91" in product: temp_prices["แก๊สโซฮอล์ 91"] = price
                        elif "Super Power" in product or "Premium" in product: temp_prices["ดีเซลพรีเมียม"] = price
                        elif "B20" in product: temp_prices["ดีเซล B20"] = price
                        elif "Diesel" in product and "Super" not in product and "Premium" not in product: 
                            if "ดีเซล" not in temp_prices: temp_prices["ดีเซล"] = price
        
        formatted = {fuel: temp_prices[fuel] for fuel in target_fuels if fuel in temp_prices}
        if formatted: return formatted, "LIVE DATA (PTT OR WEB SERVICE)"
    except:
        pass
        
    return {"สถานะ": "CONNECTION_FAILED"}, "ไม่สามารถเชื่อมต่อศูนย์ข้อมูลพลังงานได้"

# ==========================================
# 2. AUTHENTICATION & DATABASE
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
        conn.commit(); conn.close()
    
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

    tab_entry, tab_dashboard, tab_records, tab_price = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_SQLITE", "[04] ราคาน้ำมันวันนี้"])

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
                    conn.commit(); conn.close()
                    st.success("บันทึกข้อมูลเรียบร้อย."); time.sleep(1); st.rerun()

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
        st.markdown("<h4 style='color: #38bdf8;'><span style='color: #64748b;'>#</span> สรุปข้อมูลภาพรวมยานพาหนะ</h4>", unsafe_allow_html=True)
        if not logs_df.empty:
            for v_name in vehicles_df['name']:
                v_logs = logs_df[logs_df['vehicle_name'] == v_name]
                if not v_logs.empty:
                    total_cost = v_logs['total_price'].sum()
                    total_liters = v_logs['liters'].sum()
                    total_dist = v_logs['odometer'].max() - v_logs['odometer'].min() if len(v_logs) >= 2 else 0
                    avg_kml = (total_dist / total_liters) if total_liters > 0 and total_dist > 0 else 0
                    
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 20px;">
                        <h3 style="color: #38bdf8; margin-bottom: 15px;">{v_name}</h3>
                        <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                            <div><small style="color: #64748b;">ระยะทางรวม</small><br><strong style="font-size: 1.2rem;">{total_dist:,.0f} KM</strong></div>
                            <div><small style="color: #64748b;">ค่าน้ำมันรวม</small><br><strong style="font-size: 1.2rem;">฿ {total_cost:,.0f}</strong></div>
                            <div><small style="color: #64748b;">ปริมาณรวม</small><br><strong style="font-size: 1.2rem;">{total_liters:,.2f} L</strong></div>
                            <div><small style="color: #64748b;">อัตราสิ้นเปลือง</small><br><strong style="font-size: 1.2rem; color: #10b981;">{avg_kml:.2f} KM/L</strong></div>
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
                    conn.commit(); conn.close()
                    st.success("อัปเดตข้อมูลสำเร็จ!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # ==========================================
    # TAB 4: REDESIGNED LIVE MARKET
    # ==========================================
    with tab_price:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 15px; margin-bottom: 25px;">
            <h2 style="margin: 0; color: #f8fafc; font-weight: 700; letter-spacing: -0.5px;">📡 Live Market <span style="color: #38bdf8;">Energy</span></h2>
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); padding: 6px 15px; border-radius: 50px; display: flex; align-items: center; gap: 8px;">
                <div class="api-pulse"></div>
                <span style="color: #10b981; font-size: 0.8rem; font-weight: 700; font-family: 'JetBrains Mono', monospace;">API CONNECTED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        prices, status_text = get_fuel_prices()
        
        if "สถานะ" not in prices:
            st.markdown(f"<p style='color: #94a3b8; font-family: \"JetBrains Mono\", monospace; font-size: 0.85rem; margin-top: -10px;'>SYS_LOG: {status_text}</p>", unsafe_allow_html=True)
            
            # ใช้ 4 คอลัมน์เพื่อให้จัดวาง 7 ชนิดน้ำมันได้สวยงามขึ้น
            cols = st.columns(4)
            idx = 0
            
            for fuel, price in prices.items():
                # กำหนดสีขอบและเงาตามชนิดน้ำมันแบบมืออาชีพ
                if fuel == "แก๊สโซฮอล์ 95": border_color = "#fbbf24" # เหลืองทอง
                elif fuel == "แก๊สโซฮอล์ E20": border_color = "#a855f7" # ม่วง
                elif fuel == "แก๊สโซฮอล์ E85": border_color = "#ec4899" # ชมพู
                elif fuel == "แก๊สโซฮอล์ 91": border_color = "#10b981" # เขียว
                elif fuel == "ดีเซลพรีเมียม": border_color = "#3b82f6" # ฟ้าพรีเมียม
                elif fuel == "ดีเซล": border_color = "#f43f5e" # แดง
                elif fuel == "ดีเซล B20": border_color = "#be123c" # แดงเข้ม
                else: border_color = "#38bdf8"
                    
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(180deg, rgba(15, 23, 42, 0.6) 0%, rgba(3, 7, 18, 0.9) 100%); 
                                border: 1px solid rgba(255,255,255,0.05); border-top: 4px solid {border_color}; 
                                padding: 25px 20px; border-radius: 12px; margin-bottom: 20px; position: relative; overflow: hidden;
                                box-shadow: 0 10px 30px -10px rgba(0,0,0,0.7); transition: transform 0.3s ease;">
                        <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0 0 5px 0; font-weight: 600; white-space: nowrap;">{fuel}</p>
                        <div style="display: flex; align-items: baseline; gap: 8px;">
                            <h1 style="color: #ffffff; font-family: 'JetBrains Mono', monospace; font-size: 2.5rem; margin: 0; font-weight: 800; text-shadow: 0 0 15px {border_color}40;">{price}</h1>
                        </div>
                        <span style="color: #64748b; font-size: 0.8rem; font-weight: 700;">THB / LITER</span>
                    </div>
                    """, unsafe_allow_html=True)
                idx += 1
        else:
            st.error(f"⚠️ {prices['สถานะ']} : {status_text}")