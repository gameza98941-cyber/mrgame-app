from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

print("Starting the wake-up process...")

# ตั้งค่า Chrome ให้ทำงานแบบซ่อนหน้าต่าง (Headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# โหลดหน้าเว็บ Streamlit
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://mrgame-app-rtved3uysqcefntelqpshr.streamlit.app/")

# หน่วงเวลา 15 วินาที เพื่อให้ Streamlit โหลด JavaScript และ React จนเสร็จ (หลอกว่าเป็นคนจริงๆ)
time.sleep(15)

print("Successfully loaded the app. Streamlit is now awake!")
driver.quit()
