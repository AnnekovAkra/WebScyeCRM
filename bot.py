import time
import re
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# АВТОНОМНЫЙ КОНВЕЙЕР WEBSCYE (ЛОКАЛЬНАЯ ВЕЧНАЯ БАЗА ДАННЫХ БЕЗ API И ТОКЕНОВ)
# ============================================================================
VK_IM_URL = "https://vk.com"
JSON_DB_PATH = "database.json"

print("🤖 Инициализация потокового процессора WebScye...")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

def save_to_local_db(name, email, role):
    """Бот напрямую записывает анкету клиента в локальный JSON-файл в твоей папке"""
    try:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        now = time.localtime()
        date_str = f"{months[now.tm_mon - 1]} {now.tm_mday}, {now.tm_year}"
        
        current_db = []
        if os.path.exists(JSON_DB_PATH):
            with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
                try:
                    current_db = json.load(f)
                except:
                    current_db = []
                    
        if any(u.get('email') == email for u in current_db):
            return

        new_user = {
            "id": int(time.time()),
            "name": name,
            "email": email,
            "role": role,
            "status": "Active",
            "date": date_str
        }
        
        current_db.append(new_user)
        
        with open(JSON_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(current_db, f, ensure_ascii=False, indent=4)
            
        print(f"   [УСПЕХ] Контакт оцифрован в локальную базу: '{name}' | Контакт: {email}")
    except Exception as e:
        print(f"❌ [ОШИБКА ЗАПИСИ] {e}")

def parse_visible_dialogs():
    print("\n🤖 Ожидание входа... Войдите в ВК и откройте сообщения.")
    
    WebDriverWait(driver, 300).until(lambda d: "/im" in d.current_url)
    print("🤖 Соединение установлено! Включаю мгновенный перехват видимого экрана...")
    time.sleep(2)

    processed_peers = set()

    while True:
        try:
            # Цепляемся за теги ссылок, которые ВК не может скрыть
            dialog_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'sel=')]")
            
            for link in dialog_links:
                try:
                    href = link.get_attribute("href")
                    peer_id_match = re.search(r'sel=(\d+|c\d+)', href)
                    if not peer_id_match:
                        continue
                        
                    peer_id = peer_id_match.group(1)
                    if peer_id in processed_peers:
                        continue
                        
                    raw_text = link.text.strip()
                    if not raw_text:
                        continue
                        
                    # Берем Имя (первая строчка блока диалога)
                    client_name = raw_text.split('\n')[0].strip()
                    
                    if any(x in client_name.lower() for x in ["вчера", "сегодня", "назад", "ч.", "м."]) or len(client_name) < 2:
                        continue
                        
                    vk_link = f"://vk.com{peer_id}"
                    
                    # Ищем email внутри превью сообщения
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
                    client_contact = email_match.group(0) if email_match else vk_link
                    
                    role = "Professional"
                    if any(x in raw_text.lower() for x in ["фото", "свад", "съемк"]):
                        role = "Starter"
                    elif any(x in raw_text.lower() for x in ["строит", "ремонт", "бригад"]):
                        role = "Enterprise"
                        
                    save_to_local_db(client_name, client_contact, role)
                    processed_peers.add(peer_id)
                except:
                    continue
                    
            time.sleep(1.5) # Сканируем экран каждые 1.5 секунды
        except Exception as e:
            time.sleep(1.5)

if __name__ == "__main__":
    try:
        driver.get(VK_IM_URL)
        parse_visible_dialogs()
    except KeyboardInterrupt:
        driver.quit()
        print("\n🤖 Робот остановлен.")
