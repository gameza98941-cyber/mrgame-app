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

        /* ------------------------------------------------------------- */
        /* ★ ปราบ Input ทุกชนิดในระบบ (ล็อกอิน, รหัสผ่าน, ตัวเลข, วันที่) ★ */
        /* ------------------------------------------------------------- */
        
        /* 1. บังคับให้ "ตัวกล่อง" เป็นสีกรมท่าไล่เฉด Cyberpunk ทั้งหมด */
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

        /* 2. ฆ่าสีขาวทึบที่ติดมากับ input ชั้นในสุดของ Streamlit */
        input[type="text"], input[type="password"], input[type="number"], 
        [data-baseweb="base-input"], [data-baseweb="input"] {
            background-color: transparent !important;
        }

        /* 3. เอฟเฟกต์เรืองแสงเวลาคลิกเข้าไปพิมพ์ */
        [data-testid="stTextInput"] > div > div:focus-within,
        [data-testid="stNumberInputContainer"]:focus-within,
        [data-baseweb="select"] > div:focus-within,
        .stDateInput > div > div:focus-within {
            border-color: #0ea5e9 !important;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.5), inset 0 0 10px rgba(14, 165, 233, 0.2) !important;
        }
        
        /* 4. จัดฟอนต์ตัวอักษรที่พิมพ์ให้เป็นสีฟ้าเรืองแสงแบบ Holographic */
        input {
            color: #38bdf8 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.4) !important;
            -webkit-text-fill-color: #38bdf8 !important;
        }

        /* 5. [สำคัญสุด] ป้องกัน Chrome Autofill เปลี่ยนพื้นหลังเป็นสีขาว/เหลือง */
        input:-webkit-autofill,
        input:-webkit-autofill:hover, 
        input:-webkit-autofill:focus, 
        input:-webkit-autofill:active {
            -webkit-box-shadow: 0 0 0 30px #0f172a inset !important;
            -webkit-text-fill-color: #38bdf8 !important;
            transition: background-color 5000s ease-in-out 0s;
        }

        /* เปลี่ยนสีไอคอน "ลูกตา" (ดูรหัสผ่าน) และ Dropdown ให้เป็นสีฟ้า */
        [data-testid="stTextInput"] button,
        [data-baseweb="select"] svg, .stDateInput svg {
            color: #38bdf8 !important;
            fill: #38bdf8 !important;
            background: transparent !important;
        }

        /* ปุ่ม + และ - ด้านหลังของ Number Input */
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

        /* ------------------------------------------------------------- */
        /* ★ อัปเกรด File Uploader (OCR) สไตล์ Cyberpunk ★ */
        /* ------------------------------------------------------------- */
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

        /* ------------------------------------------------------------- */
        /* ★ อัปเกรดปุ่มกดทุกชนิด ให้ล้ำยุค ★ */
        /* ------------------------------------------------------------- */
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
# 1. ADVANCED API FETCHING (7 FUELS VERSION)
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
                        elif "DIESEL" in p_up and "B20" not in p_up and "SUPER"