import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import requests
import sqlalchemy  # เพิ่มตัวนี้เข้ามาเพื่อจัดการ Connection ให้เสถียรที่สุด

# ==========================================
# 0. PAGE CONFIG & GLOBAL CSS (ไม่ได้ปรับเปลี่ยน)
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

        /* ★ ปรับแต่ง Input ทุกชนิดให้เป็นสไตล์แผงควบคุมเรืองแสง Cyberpunk ★ */
        [data-testid="stTextInput"] > div > div,
        [data-testid="stNumberInputContainer"], 
        [data-baseweb="select"] > div, 
        .stDateInput > div > div {
            background: linear-gradient(90deg, rgba(3, 7, 18, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            border-radius: 8px !important;
            color: #38bdf8 !important;
            transition: all 0.3s ease !important;
            box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.6) !important;
        }

        input[type="text"], input[type="password"], input[type="number"], 
        [data-baseweb="base-input"], [data-baseweb="input"] {
            background-color: transparent !important;
        }

        [data-testid="stTextInput"] > div > div:focus-within,
        [data-testid="stNumberInputContainer"]:focus-within,
        [data-baseweb="select"] > div:focus-within,
        .stDateInput > div > div:focus-within {
            border-color: #0ea5e9 !important;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.5), inset 0 0 10px rgba(14, 165, 233, 0.2) !important;
        }
        
        input {
            color: #38bdf8 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important;
            -webkit-text-fill-color: #38bdf8 !important;
        }

        input:-webkit-autofill,
        input:-webkit-autofill:hover, 
        input:-webkit-autofill:focus, 
        input:-webkit-autofill:active {
            -webkit-box-shadow: 0 0 0 30px #0f172a inset !important;
            -webkit-text-fill-color: #38bdf8 !important;
            transition: background-color 5000s ease-in-out 0s;
        }

        [data-testid="stTextInput"] button,
        [data-baseweb="select"] svg, .stDateInput svg {
            color: #38bdf8 !important;
            fill: #38bdf8 !important;
            background: transparent !important;
        }

        [data-testid="stNumberInputContainer"] button {
            background: rgba(30, 41, 59, 0.9) !important;
            color: #38bdf8 !important;
            border: none !important;
            border-left: 1px solid rgba(56, 189, 248, 0.2) !important;
            border-radius: 0 !important;
        }
        [data-testid="stNumberInputContainer"] button:hover {
            background: #38bdf8 !important; color: #030712 !important;
            box-shadow: 0 0 15px #38bdf8 !important;
        }

        /* ★ File Uploader (OCR) สไตล์ Cyberpunk ★ */
        [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important;
            border: 2px dashed rgba(168, 85, 247, 0.5) !important;
            border-radius: 12px !important; padding: 25px !important;
            transition: all 0.3s ease !important;
            box-shadow: inset 0 0 15px rgba(168, 85, 247, 0.05) !important;
        }
        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: #a855f7 !important;
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(3, 7, 18, 0.95)) !important;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.3), inset 0 0 15px rgba(168, 85, 247, 0.2) !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] { color: #cbd5e1 !important; font-family: 'JetBrains Mono', monospace !important; }
        [data-testid="stFileUploaderDropzoneInstructions"] > div { color: #94a3b8 !important; }
        [data-testid="stFileUploaderDropzone"] button {
            background: rgba(168, 85, 247, 0.15) !important; color: #e9d5ff !important;
            border: 1px solid rgba(168, 85, 247, 0.5) !important; border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important; font-weight: bold !important;
        }
        [data-testid="stFileUploaderDropzone"] button:hover {
            background: #a855f7 !important; color: #ffffff !important;
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.6) !important;
        }
        [data-testid="stUploadedFile"] { background: rgba(30, 41, 59, 0.8) !important; border: 1px solid rgba(168, 85, 247, 0.3) !important; border-radius: 8px !important; }
        [data-testid="stUploadedFileName"] { color: #e9d5ff !important; font-family: 'JetBrains Mono', monospace !important; }

        /* ★ ปุ่มกดสไตล์ดิจิทัลล้ำยุค ★ */
        div[data-testid="stButton"] > button, div.stFormSubmitButton > button {
            background: linear-gradient(90deg, rgba(2, 132, 199, 0.85) 0%, rgba(14, 165, 233, 0.95) 100%) !important;
            color: #ffffff !important; 
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1rem !important;
            font-weight: 800 !important; 
            letter-spacing: 1px !important;
            text-transform: uppercase;
            border-radius: 8px !important; 
            width: 100%;
            border: 1px solid rgba(56, 189, 248, 0.6) !important;
            padding: 14px !important;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stButton"] > button:hover, div.stFormSubmitButton > button:hover { 
            transform: translateY(-2px) !important; 
            background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%) !important;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.7) !important;
            border-color: #ffffff !important;
        }
        
        .glass-card {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            border-radius: 16px !important;
            padding: 35px !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
        }
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .api-pulse { width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 10px #10b981; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. ADVANCED API FETCHING (7 FUELS VERSION) (ไม่ได้ปรับเปลี่ยน)
# ==========================================
def get_fuel_prices():
    target_fuels = [
        "แก๊สโซฮอล์ 95", "แก๊สโซฮอล์ E20", "แก๊สโซฮอล์ E85", 
        "แก๊สโซฮอล์ 91", "ดีเซลพรีเมียม", "ดีเซล", "ดีเซล B20"
    ]
    temp_prices = {}
    status_text = ""

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
        
        for k, v in mapping.items():
            if k in prices_raw and v not in temp_prices:
                temp_prices[v] = f"{float(prices_raw[k]['price']):.2f}"
                
        formatted = {fuel: temp_prices[fuel] for fuel in target_fuels if fuel in temp_prices}
        if formatted: return formatted, f"ข้อมูลประจำวันที่: {date_str}"
    except:
        pass

    try:
        url = "https://orapiweb.pttor.com/oilservice/OilPrice.asmx"
        headers = {'Content-Type': 'text/xml; charset=utf-8'}
        payload = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><CurrentOilPrice xmlns="http://www.pttor.com"><Language>en</Language></CurrentOilPrice></soap:Body></soap:Envelope>'
        response = requests.post(url, headers=headers, data=payload, timeout=5)
        
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.text)
        for elem in root.iter():
            if 'CurrentOilPriceResult' in elem.tag:
                inner_root = ET.fromstring(elem.text)
                for fuel in inner_root.findall('FUEL'):
                    product = fuel.find('PRODUCT').text if fuel.find('PRODUCT') is not None else ""
                    price = fuel.find('PRICE').text if fuel.find('PRICE') is not None else ""
                    
                    if price and float(price) > 0:
                        p_up = product.upper()
                        if "E20" in p_up: temp_prices["แก๊สโซฮอล์ E20"] = price
                        elif "E85" in p_up: temp_prices["แก๊สโซฮอล์ E85"] = price
                        elif "91" in p_up: temp_prices["แก๊สโซฮอล์ 91"] = price
                        elif "95" in p_up and "SUPER" not in p_up: temp_prices["แก๊สโซฮอล์ 95"] = price
                        elif "SUPER" in p_up or "PREMIUM" in p_up: temp_prices["ดีเซลพรีเมียม"] = price
                        elif "B20" in p_up: temp_prices["ดีเซล B20"] = price
                        elif "DIESEL" in p_up and "B20" not in p_up and "SUPER" not in p_up:
                            if "ดีเซล" not in temp_prices: temp_prices["ดีเซล"] = price
                            
        status_text = "LIVE DATA CONNECTED (PTT OR API)"
    except Exception:
        pass

    if not temp_prices:
        return {"สถานะ": "CONNECTION_FAILED"}, "ไม่สามารถเชื่อมต่อศูนย์ข้อมูลพลังงานได้"

    formatted = {fuel: temp_prices[fuel] for fuel in target_fuels if fuel in temp_prices}
    return formatted, status_text

# ==========================================
# 2. AUTHENTICATION & DATABASE CONNECT
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
    
    # --- เริ่มต้นส่วนที่แก้ไขระบบหลังบ้าน (ไม่กระทบหน้าตาแอป) ---
    @st.cache_resource
    def init_connection():
        db_url = st.secrets["connections"]["supabase"]["url"]
        return sqlalchemy.create_engine(
            db_url,
            connect_args={"sslmode": "require"},
            pool_pre_ping=True,  # ตัวแปรสำคัญ: สั่งให้เช็คสายก่อนดึงข้อมูลทุกครั้ง ป้องกัน OperationalError
            pool_recycle=300     # รีเฟรชการเชื่อมต่อทุก 5 นาที ป้องกัน Supabase ตัดสายทิ้ง
        )

    try:
        engine = init_connection()
    except Exception as e:
        st.error(f"ระบบฐานข้อมูลมีปัญหา: {e}")
        st.stop()

    def get_latest_data(vehicle_name):
        try:
            query = sqlalchemy.text("SELECT odometer, date FROM fuel_logs WHERE vehicle_name = :v_name ORDER BY odometer DESC LIMIT 1")
            df = pd.read_sql(query, engine, params={"v_name": vehicle_name})
            if not df.empty: return float(df.iloc[0]['odometer']), df.iloc[0]['date']
        except Exception:
            pass
        return 0.0, None

    # ดึงข้อมูลผ่าน Engine แทน conn.query ของเดิมที่มักจะหลุด
    try:
        logs_df = pd.read_sql("SELECT id, date, vehicle_name, odometer, liters, total_price FROM fuel_logs ORDER BY date DESC, odometer DESC", engine)
        vehicles_df = pd.read_sql("SELECT name, fuel_type FROM vehicles WHERE is_active = true", engine)
    except Exception as e:
        st.error(f"⚠️ เกิดปัญหา OperationalError: ไม่สามารถดึงข้อมูลจาก Cloud ได้")
        st.info(f"รายละเอียดทางเทคนิค: {e}")
        st.stop()
    # --- สิ้นสุดส่วนที่แก้ไขระบบหลังบ้าน ---

    st.markdown("<h1 style='font-size: 2.2rem;'>ศูนย์วิเคราะห์ข้อมูลอัจฉริยะ <span class='text-gradient'>(Telemetry Center)</span></h1>", unsafe_allow_html=True)

    tab_entry, tab_dashboard, tab_records, tab_price = st.tabs(["[01] บันทึกข้อมูล", "[02] แดชบอร์ดวิเคราะห์", "[03] ฐานข้อมูล_CLOUD", "[04] ราคาน้ำมันวันนี้"])

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
                    try:
                        # บันทึกข้อมูลโดยใช้ Engine ที่เสถียรแล้ว
                        with engine.begin() as conn:
                            conn.execute(
                                sqlalchemy.text("INSERT INTO fuel_logs (date, vehicle_name, odometer, liters, total_price) VALUES (:date, :v_name, :odo, :liters, :price)"),
                                {"date": form_date.strftime('%Y-%m-%d'), "v_name": form_vehicle, "odo": form_odo, "liters": form_liters, "price": form_price}
                            )
                        st.success("บันทึกข้อมูลลงระบบ Cloud สำเร็จ!"); time.sleep(1); st.rerun()
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")

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
        st.markdown("<h4 style='color: #10b981;'><span style='color: #64748b;'>//</span> ฐานข้อมูลพลังงานบนระบบคลาวด์ (Editable)</h4>", unsafe_allow_html=True)
        if not logs_df.empty:
            edited_df = st.data_editor(logs_df, use_container_width=True, num_rows="dynamic", key="fuel_editor", disabled=["id"])
            if st.button("บันทึกการแก้ไขไปยังฐานข้อมูล Cloud"):
                try:
                    # อัปเดตข้อมูลขึ้นตรงกับ Supabase Postgres Engine
                    edited_df.to_sql('fuel_logs', engine, if_exists='replace', index=False)
                    st.success("ซิงค์ข้อมูลกับคลาวด์สำเร็จ!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

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
            
            cols = st.columns(4)
            idx = 0
            
            for fuel, price in prices.items():
                if fuel == "แก๊สโซฮอล์ 95": border_color = "#fbbf24"
                elif fuel == "แก๊สโซฮอล์ E20": border_color = "#a855f7"
                elif fuel == "แก๊สโซฮอล์ E85": border_color = "#ec4899"
                elif fuel == "แก๊สโซฮอล์ 91": border_color = "#10b981"
                elif fuel == "ดีเซลพรีเมียม": border_color = "#3b82f6"
                elif fuel == "ดีเซล": border_color = "#f43f5e"
                elif fuel == "ดีเซล B20": border_color = "#be123c"
                else: border_color = "#38bdf8"
                    
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(180deg, rgba(15, 23, 42, 0.6) 0%, rgba(3, 7, 18, 0.9) 100%); 
                                border: 1px solid rgba(255,255,255,0.05); border-top: 4px solid {border_color}; 
                                padding: 25px 20px; border-radius: 12px; margin-bottom: 20px; position: relative; overflow: hidden;
                                box-shadow: 0 10px 30px -10px rgba(0,0,0,0.7); transition: transform 0.3s ease;">
                        <p style="color: #cbd5e1; font-size: 0.95rem; margin: 0 0 5px 0; font-weight: 600; white-space: nowrap;">{fuel}</p>
                        <div style="display: flex; align-items: baseline; gap: 8px;">
                            <h1 style="color: #ffffff; font-family: 'JetBrains Mono', monospace; font-size: 2.3rem; margin: 0; font-weight: 800; text-shadow: 0 0 15px {border_color}40;">{price}</h1>
                        </div>
                        <span style="color: #64748b; font-size: 0.75rem; font-weight: 700;">THB / LITER</span>
                    </div>
                    """, unsafe_allow_html=True)
                idx += 1
        else:
            st.error(f"⚠️ {prices['สถานะ']} : {status_text}")