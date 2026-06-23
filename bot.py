import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================================================================
# АВТОНОМНЫЙ ИНФОРМАЦИОННЫЙ КОНВЕЙЕР WEBSCYE (БЕЗ УЧЕТА ФИНАНСОВ)
# ============================================================================
VK_IM_URL = "https://vk.com"
CRM_URL = "https://github.io"

print("🤖 Запуск чистого информационного робота WebScye CRM...")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def inject_to_crm(name, email, role):
    """Грамотная инжекция анкетных данных в CRM на GitHub Pages в обход кэша"""
    try:
        driver.execute_script(f"window.open('{CRM_URL}', '_blank');")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])
        
        # Пересоздаем чистый шлюз прямо в памяти открытой вкладки
        js_gateway = """
        window.addLeadFromBot = function(name, email, role) {
            let users = [];
            if (localStorage.getItem('webscye_users')) { users = JSON.parse(localStorage.getItem('webscye_users')); }
            if (users.some(u => u.email === email)) { return "EXISTS"; }
            const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const now = new Date();
            users.push({ id: Date.now(), name: name, email: email, role: role, status: "Active", date: `${months[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}` });
            localStorage.setItem('webscye_users', JSON.stringify(users));
            return "OK";
        };
        """
        driver.execute_script(js_gateway)
        
        # Вызываем функцию БЕЗ передачи параметров цены
        script = f"return window.addLeadFromBot('{name}', '{email}', '{role}');"
        result = driver.execute_script(script)
        
        if result == "OK":
            print(f"   [УСПЕХ] Данные импортированы: '{name}' | Контакт: {email} | Направление: {role}")
            
        driver.close()
        driver.switch_to.window(driver.window_handles)
    except Exception as e:
        print(f"❌ [ОШИБКА ИНЖЕКЦИИ] {e}")
        if len(driver.window_handles) > 0:
            driver.switch_to.window(driver.window_handles)

def parse_all_dialogs():
    """Глобальное автоматическое сканирование 350 диалогов мессенджера ВК"""
    print("\n🤖 Шаг 1. Ожидание авторизации... Войдите в свой ВК.")
    
    # Ожидаем входа в мессенджер ВК
    WebDriverWait(driver, 300).until(EC.presence_of_element_id("im_dialogs"))
    print("🤖 Авторизация подтверждена. Начинаю автоматическую выгрузку базы запросов...")
    time.sleep(3)
    
    # Сканнер плавно прокручивает левую панель, чтобы прогрузить всю историю (350 диалогов)
    print("🤖 Автоматическая прокрутка списка сообщений...")
    for _ in range(20):
        try:
            driver.execute_script("document.querySelector('.im-page--dialogs-list').scrollTop = 99999;")
            time.sleep(0.4)
        except:
            break

    processed_peers = set()

    while True:
        try:
            # Находим все элементы запросов (диалогов) на экране
            dialogs = driver.find_elements(By.CSS_SELECTOR, ".im-page--dki")
            
            for dialog in dialogs:
                try:
                    peer_id = dialog.get_attribute("data-peer")
                    if not peer_id or peer_id in processed_peers:
                        continue
                        
                    # Вытаскиваем Имя / Название паблика бизнеса
                    name_el = dialog.find_element(By.CSS_SELECTOR, ".im-page--peer-name")
                    client_name = name_el.text.strip()
                    
                    # Читаем текст последнего сообщения для поиска почты
                    msg_body = dialog.find_element(By.CSS_SELECTOR, ".im-page--chat-body")
                    msg_text = msg_body.text
                    
                    # Ищем регулярным выражением Email внутри текста переписки
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', msg_text)
                    # Если почты в тексте нет — пишем прямую ссылку на этот диалог для связи
                    client_contact = email_match.group(0) if email_match else f"://vk.com{peer_id}"
                    
                    # Автоматическое распределение по ролям/категориям для CRM
                    role = "Professional"
                    lower_text = msg_text.lower()
                    if "фото" in lower_text or "свад" in lower_text or "галере" in lower_text:
                        role = "Starter"
                    elif "строит" in lower_text or "ремонт" in lower_text or "дом" in lower_text:
                        role = "Enterprise"
                    
                    # Отправляем чистый пакет данных в CRM
                    inject_to_crm(client_name, client_contact, role)
                    processed_peers.add(peer_id)
                except:
                    continue
            
            # Бот засыпает на 4 секунды и проверяет появление абсолютно новых запросов в ВК
            time.sleep(4)
        except Exception as e:
            time.sleep(4)

if __name__ == "__main__":
    try:
        driver.get(VK_IM_URL)
        parse_all_dialogs()
    except KeyboardInterrupt:
        driver.quit()
        print("\n🤖 Робот остановлен.")
