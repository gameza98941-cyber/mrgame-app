import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time

# ==========================================
# 1. AUTHENTICATION (ระบบล็อกอิน)
# ==========================================
def check_password():
    """Returns True if the user had the correct password."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    # หน้า Login
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 80vh;">
            <div class="glass-card" style="width: 400px;">
                <h2 style="text-align: center; color: #38bdf8;">🔐 MrGame Access</h2>
                <p style="text-align: center; color: #64748b; font-size: 0.8rem; margin-bottom: 20px;">กรุณายืนยันตัวตนก่อนเข้าสู่ศูนย์ปฏิบัติการ</p>
    """, unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("เข้าสู่ระบบ"):
        # --- ปรับแก้ Username และ Password ตรงนี้ครับ ---
        if username == "mrgame" and password == "Game2541$!!":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    return False

# ==========================================
# 2. CORE SYSTEM & AI UI ENGINE
# ==========================================
st.set_page_config(page_title="MrGame | AI Telemetry", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# ถ้าล็อกอินผ่านแล้วค่อยแสดงเนื้อหาทั้งหมด
if check_password():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Prompt:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700;800&display=swap');
            
            html, body, [class*="css"] { 
                font-family: 'Prompt', 'Outfit', sans-serif !important; 
            }
            
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
            
            .tech-font {
                font-family: 'JetBrains Mono', monospace !important;
                letter-spacing: -0.5px;
            }

            [data-testid="stForm"], .glass-card {
                background: linear-gradient(145deg, rgba(15, 23, 42, 0.6), rgba(3, 7, 18, 0.8)) !important;
                backdrop-filter: blur(20px) !important;
                border: 1px solid rgba(14, 165, 233, 0.15) !important;
                border-radius: 16px !important;
                padding: 35px !important;
                box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            
            [data-testid="stForm"]:hover, .glass-card:hover {
                border: 1px solid rgba(14, 165, 233, 0.4) !important;
                box-shadow: 0 30px 60px -15px rgba(14, 165, 233, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
                transform: translateY(-5px);
            }
            
            [data-baseweb="input"], [data-baseweb="select"] > div {
                background-color: rgba(0, 0, 0, 0.6) !important;
                border: 1px solid rgba(14, 165, 233, 0.2) !important;
                border-radius: 8px !important; 
                color: #38bdf8 !important;
                font-family: 'JetBrains Mono', monospace !important;
                transition: all 0.3s ease !important;
            }
            
            [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
                border: 1px solid #0ea5e9 !important;
                box-shadow: 0 0 20px rgba(14, 165, 233, 0.3) !important;
            }
            
            div.stButton > button {
                background: linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%) !important;
                color: #ffffff !important; 
                font-weight: 700 !important; 
                font-size: 1.1rem !important;
                letter-spacing: 1px !important;
                text-transform: uppercase;
                border: 1px solid rgba(255, 255, 255, 0.2) !important; 
                border-radius: 8px !important; 
                width: 100%;
                box-shadow: 0 0 15px rgba(14, 165, 233, 0.4), inset 0 2px 4px rgba(255,255,255,0.3) !important; 
                transition: all 0.3s ease !important;
                position: relative;
                overflow: hidden;
            }
            
            div.stButton > button:hover { 
                transform: scale(1.02) !important; 
                box-shadow: 0 0 30px rgba(14, 165, 233, 0.8) !important;
            }
            
            .stTabs [data-baseweb="tab-list"] {
                background: rgba(3, 7, 18, 0.6); 
                backdrop-filter: blur(16px);
                border-radius: 16px; 
                padding: 8px; 
                gap: 12px; 
                border: 1px solid rgba(14, 165, 233, 0.3); 
                margin-bottom: 30px;
                box-shadow: 0 10px 30px -10px rgba(14, 165, 233, 0.2), inset 0 0 20px rgba(14, 165, 233, 0.05);
            }
            
            .stTabs [data-baseweb="tab"] { 
                background: rgba(15, 23, 42, 0.5); 
                border: 1px solid transparent !important; 
                color: #64748b; 
                font-weight: 700; 
                font-size: 1rem; 
                letter-spacing: 1px;
                border-radius: 10px;
                padding: 10px 24px;
                font-family: 'JetBrains Mono', 'Prompt', sans-serif !important;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            
            .stTabs [data-baseweb="tab-highlight"] {
                background-color: transparent !important;
                display: none !important;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(14, 165, 233, 0.1);
                color: #e2e8f0;
                border: 1px solid rgba(14, 165, 233, 0.3) !important;
                transform: translateY(-2px);
            }
            
            .stTabs [aria-selected="true"] { 
                background: linear-gradient(135deg, rgba(2, 132, 199, 0.4) 0%, rgba(14, 165, 233, 0.1) 100%) !important;
                color: #38bdf8 !important; 
                border: 1px solid rgba(56, 189, 248, 0.6) !important; 
                box-shadow: 0 0 20px rgba(14, 165, 233, 0.4), inset 0 0 10px rgba(56, 189, 248, 0.2) !important;
                text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
            }
            
            .text-gradient { 
                background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
            }
            
            [data-testid="stSidebar"] { 
                background: rgba(3, 7, 18, 0.85) !important; 
                backdrop-filter: blur(25px) !important; 
                border-right: 1px solid rgba(14, 165, 233, 0.15) !important; 
            }
            
            @keyframes pulse-glow {
                0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
                70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
                100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
            }
            .ai-status {
                animation: pulse-glow 2s infinite;
            }
        </style>
    """, unsafe_allow_html=True)

    # ... (เนื้อหาโค้ดเดิมของคุณทั้งหมดที่เหลือ วางไว้ตรงนี้ต่อลงมาได้เลยครับ)
    # ผมย่อเนื้อหาในส่วนนี้ไว้ แต่คุณวางโค้ดเดิมทั้งหมดต่อจากบรรทัดนี้ได้เลยครับ
    
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
        if not df.empty:
            return df.iloc[0]['odometer'], df.iloc[0]['date']
        return 0.0, None

    def calculate_realtime_metrics(vehicle_name, current_odo, current_liters, current_price):
        prev_odo, _ = get_latest_data(vehicle_name)
        if prev_odo > 0 and current_odo > prev_odo:
            distance = current_odo - prev_odo
            return distance / current_liters, current_price / distance, distance
        return None, None, None

    # ... (ส่วนที่เหลือของโค้ดเดิมคุณทั้งหมด วางต่อได้เลยครับ)
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
                    <span style='color: #64748b; font-size: 0.7rem; font-family: "JetBrains Mono", monospace;'>Latency: 12ms | Port: 8501</span>
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
            <p style='color: #64748b; font-size: 0.9rem; font-family: "JetBrains Mono", monospace; margin-top: 5px;'>// เริ่มต้นโปรโตคอลวิเคราะห์ข้อมูลแบบเรียลไทม์</p>
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
            <br>
            """, unsafe_allow_html=True)
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพใบเสร็จ", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                st.image(uploaded_file, use_column_width=True)
                with st.spinner('กำลังสกัดข้อมูลเวกเตอร์...'):
                    time.sleep(1.5)
                st.success("สกัดข้อมูลเสร็จสิ้น (โหมดจำลอง)")

    with tab_dashboard:
        if not logs_df.empty:
            st.markdown("<h4 style='color: #c084fc; font-weight: 600; margin-bottom: 20px; font-family: \"JetBrains Mono\", monospace;'>// อัลกอริทึมพยากรณ์</h4>", unsafe_allow_html=True)
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
                                <p style="color: #64748b; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; margin:0;">คาดการณ์รายจ่าย 30 วัน</p>
                                <h2 class="tech-font" style="color: #f8fafc; font-weight: 800; margin: 5px 0;">฿ {est_monthly_cost:,.0f}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 25px;">
                            <h5 style="color: #64748b; margin: 0 0 5px 0;">{v_name}</h5>
                            <p style="color: #475569; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; margin:0;">ข้อผิดพลาด: ข้อมูลไม่เพียงพอ (ขั้นต่ำ 3 รายการ)</p>
                        </div>
                        """, unsafe_allow_html=True)
            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 35px 0;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #38bdf8; font-weight: 600; margin-bottom: 20px; font-family: \"JetBrains Mono\", monospace;'>// สถิติแบบเรียลไทม์</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<p style='color: #64748b; font-size: 0.85rem; font-family: \"JetBrains Mono\", monospace;'>มาตรวัดประสิทธิภาพสูงสุด</p>", unsafe_allow_html=True)
                gauge_data = []
                for v in vehicles_df['name']:
                    vl = logs_df[logs_df['vehicle_name'] == v].sort_values('odometer')
                    if len(vl) >= 2:
                        dist = vl['odometer'].max() - vl['odometer'].min()
                        liters = vl['liters'].iloc[1:].sum()
                        if liters > 0:
                            gauge_data.append({'name': v, 'kml': dist/liters})
                if gauge_data:
                    best_v = max(gauge_data, key=lambda x: x['kml'])
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number", value = best_v['kml'],
                        title = {'text': f"{best_v['name']} (กม./ลิตร)", 'font': {'color': '#94a3b8', 'size': 14, 'family': 'Prompt'}},
                        number={'font': {'color': '#38bdf8', 'family': 'JetBrains Mono'}},
                        gauge = {
                            'axis': {'range': [0, 60], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
                            'bar': {'color': "#0ea5e9"}, 'bgcolor': "rgba(15, 23, 42, 0.4)",
                            'steps': [{'range': [0, 15], 'color': "rgba(225, 29, 72, 0.2)"}, {'range': [15, 35], 'color': "rgba(217, 119, 6, 0.2)"}, {'range': [35, 60], 'color': "rgba(16, 185, 129, 0.2)"}],
                        }
                    ))
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(l=30, r=30, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                st.markdown("<p style='color: #64748b; font-size: 0.85rem; font-family: \"JetBrains Mono\", monospace;'>วิเคราะห์แนวโน้มค่าใช้จ่าย</p>", unsafe_allow_html=True)
                logs_copy = logs_df.copy()
                logs_copy['date'] = pd.to_datetime(logs_copy['date'])
                trend_df = logs_copy.groupby(['date', 'vehicle_name'])['total_price'].sum().reset_index()
                if len(trend_df) > 0:
                    fig2 = px.line(trend_df, x="date", y="total_price", color='vehicle_name', markers=True, color_discrete_sequence=['#0ea5e9', '#10b981', '#f43f5e'])
                    fig2.update_traces(line_shape='spline', line=dict(width=3), marker=dict(size=8, symbol="diamond"))
                    fig2.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.02)", color="#64748b", title="", tickfont=dict(family='JetBrains Mono')),
                        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#64748b", title="บาท (THB)", tickfont=dict(family='JetBrains Mono')),
                        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family='Prompt', color="#94a3b8")),
                        height=320, margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("รอการอัปโหลดข้อมูลเริ่มต้นในระบบ")

    with tab_records:
        if not logs_df.empty:
            st.markdown("<h4 style='color: #10b981; font-weight: 600; margin-bottom: 20px; font-family: \"JetBrains Mono\", monospace;'>// ฐานข้อมูล_SQLITE</h4>", unsafe_allow_html=True)
            display_df = logs_df.copy()
            display_df.columns = ['รหัส', 'วันเวลา', 'ยานพาหนะ', 'เลขไมล์ (กม.)', 'ปริมาณ (ลิตร)', 'ยอดชำระ (บาท)']
            st.dataframe(display_df, use_container_width=True, hide_index=True)