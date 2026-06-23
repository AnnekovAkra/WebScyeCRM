import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# АВТОНОМНЫЙ ИНФОРМАЦИОННЫЙ КОНВЕЙЕР WEBSCYE (ПРОМЫШЛЕННЫЙ СБОР)
# ============================================================================
VK_IM_URL = "https://vk.com"
CRM_URL = "https://github.io"

print("🤖 Инициализация интеллектуального робота WebScye CRM...")

# Настройка стабильного браузера Chrome
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True) # Не закрывает браузер при ошибках

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def inject_to_crm(name, email, role):
    """Прямая и чистая инжекция анкетных данных во вторую открытую вкладку CRM"""
    try:
        # Открываем CRM в новой вкладке через стандартный переход браузера
        driver.execute_script(f"window.open('{CRM_URL}', '_blank');")
        time.sleep(2.5) # Даем матовому стеклу надежно прогрузиться
        
        # Переключаемся на вкладку с CRM
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        
        # Инжектируем чистый JS-шлюз прямо в память открытой вкладки в обход кэша
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
        
        # Вызываем функцию инжекции анкетных данных БЕЗ передачи параметров цены
        script = f"return window.addLeadFromBot('{name}', '{email}', '{role}');"
        result = driver.execute_script(script)
        
        if result == "OK":
            print(f"   [УСПЕХ] Данные импортированы: '{name}' | Контакт/Email: {email} | Направление: {role}")
            
        # Закрываем вкладку CRM и возвращаемся в ВК
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except Exception as e:
        print(f"❌ [ОШИБКА ИНЖЕКЦИИ] {e}")
        if len(driver.window_handles) > 0:
            driver.switch_to.window(driver.window_handles[0])

def parse_all_dialogs():
    """Глобальное автоматическое сканирование всех диалогов ВК"""
    print("\n🤖 Шаг 1. Ожидание авторизации... Войдите в свой ВК в открывшемся окне.")
    
    # Железное ожидание перехода в мессенджер по URL-адресу
    WebDriverWait(driver, 300).until(lambda d: "/im" in d.current_url)
    print("🤖 Авторизация подтверждена. Начинаю автоматическую выгрузку базы запросов...")
    time.sleep(4)
    
    # Сканнер аккуратно и плавно прокручивает левую панель, чтобы прогрузить все 350 диалогов
    print("🤖 Автоматическая прокрутка списка сообщений ВК...")
    for _ in range(25):
        try:
            # Скроллим левую панель диалогов средствами самого браузера Chrome
            driver.execute_script("document.querySelector('div[class*=\"dialogs_list\"]').scrollTop = 99999;")
            time.sleep(0.4)
        except:
            # Если первый селектор не сработал, пробуем альтернативный общий скролл
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.4)
            except:
                break

    processed_peers = set()

    while True:
        try:
            # Сбор данных по железным тегам ссылок переписок, которые ВК не может скрыть
            dialog_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='sel=']")
            
            for dialog in dialog_elements:
                try:
                    href = dialog.get_attribute("href")
                    peer_id_match = re.search(r'sel=(\d+|c\d+)', href)
                    if not peer_id_match:
                        continue
                        
                    peer_id = peer_id_match.group(1)
                    if peer_id in processed_peers:
                        continue
                        
                    # Вытаскиваем чистый сырой текст из блока диалога
                    raw_text = dialog.text.strip()
                    if not raw_text:
                        continue
                        
                    # Распиливаем текстовую массу (ВК всегда пишет Имя/Название на первой строчке)
                    text_lines = raw_text.split('\n')
                    client_name = text_lines[0].strip()
                    
                    # Проверяем, чтобы в имя не попал системный мусор или время сообщения
                    if any(x in client_name.lower() for x in ["вчера", "сегодня", "назад", "ч.", "м."]) or len(client_name) < 2:
                        continue
                        
                    # Ищем регулярным выражением Email внутри всего текста переписки на превью
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
                    # Если почты в тексте превью нет — пишем прямую ссылку на этот диалог для связи
                    client_contact = email_match.group(0) if email_match else f"://vk.com{peer_id}"
                    
                    # Умное автоматическое распределение направлений по ключевым словам для твоей CRM
                    role = "Professional"
                    lower_text = raw_text.lower()
                    if any(x in lower_text for x in ["фото", "свад", "съемк"]):
                        role = "Starter"
                    elif any(x in lower_text for x in ["строит", "ремонт", "бригад"]):
                        role = "Enterprise"
                        
                    # Отправляем чистый пакет анкетных данных в CRM на гитхаб
                    inject_to_crm(client_name, client_contact, role)
                    processed_peers.add(peer_id)
                except:
                    continue
                    
            # Бот засыпает на 4 секунды и проверяет появление абсолютно новых входящих/исходящих запросов
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
