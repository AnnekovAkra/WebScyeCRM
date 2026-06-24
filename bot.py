import time
import os
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# КОМБАЙН ЛИДОГЕНЕРАЦИИ WEBSCYE: TARGETHUNTER ПАРСЕР + ВК РАССЫЛЬЩИК
# ============================================================================

# Твой продающий оффер студии WebScye
OFFER_TEXT = "Здравствуйте! Я ведущий разработчик холдинга WebScye. Мы подготовили готовое ИТ-решение для автоматизации и привлечения клиентов конкретно под ваше направление. Если вам актуально масштабирование бизнеса, напишите нам."

TARGETS_FILE = "targets.txt"
HISTORY_FILE = "sent_history.txt"

print("🤖 Инициализация промышленного комбайна WebScye...")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_history(group_id):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{group_id}\n")

def harvest_target_hunter_ids():
    """Бот автоматически выкачивает все ID групп прямо из открытого окна TargetHunter"""
    print("\n🕵️ Шаг 1. Сбор базы в TargetHunter.")
    print("💡 ИНСТРУКЦИЯ: Откройте вкладку TargetHunter, выполните нужный поиск фотографов.")
    print("💡 Когда на экране появится список найденных групп, вернитесь в терминал и нажмите ENTER...")
    input("⌨️ Нажмите [ENTER] для перехвата ID с экрана...")
    
    print("🤖 Сканирую страницу TargetHunter на наличие системных ID сообществий...")
    
    # Робот вытаскивает весь HTML-код страницы, чтобы найти ID групп
    page_source = driver.page_source
    
    # Ищем любые упоминания ссылок на группы ://vk.com или ://vk.com, либо чистые ID
    # Регулярное выражение нацелено на поиск ID сообществ в интерфейсе TargetHunter
    found_ids = re.findall(r'(?:club|public|group|id|vk\.com\/|-)(\d{5,15})', page_source)
    
    # Убираем дубликаты и пустые значения
    unique_ids = sorted(list(set(found_ids)))
    
    if len(unique_ids) == 0:
        print("⚠️ Робот не смог найти ID на этой странице. Попробуем собрать по ссылкам...")
        # Альтернативный поиск по тегам ссылок <a> в интерфейсе TH
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'vk.com')]")
        for link in links:
            href = link.get_attribute("href")
            match = re.search(r'(?:club|public|-\s*)(\d+)', href)
            if match:
                unique_ids.append(match.group(1))
        unique_ids = sorted(list(set(unique_ids)))

    if len(unique_ids) == 0:
        print("❌ База пуста! Убедитесь, что на экране в TargetHunter открыт результат поиска.")
        return False
        
    print(f"🔥 УСПЕХ! Робот WebScye автоматически перехватил {len(unique_ids)} ID фотографов!")
    
    # Записываем свежие ID в файл мимо ручной работы
    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
        for gid in unique_ids:
            f.write(f"{gid}\n")
    return True

def run_vk_delivery():
    """Запуск веерной рассылки по собранным ID"""
    print("\n🚀 Шаг 2. Запуск веерной рассылки офферов по собранной базе...")
    
    if not os.path.exists(TARGETS_FILE):
        print("❌ Ошибка: Файл базы не найден.")
        return

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        group_ids = [line.strip() for line in f if line.strip()]

    history = load_history()
    print(f"🤖 В очереди на отправку: {len(group_ids)} сообществ. Исключено старых: {len(history)}.")

    for group_id in group_ids:
        if group_id in history:
            continue

        direct_chat_url = f"https://vk.com{group_id}"
        print(f"👉 Открываю диалог с сообществом ID: {group_id}")
        
        try:
            driver.get(direct_chat_url)
            time.sleep(3.5) # Даем чату прогрузиться, чтобы фокус встал в поле ввода
            
            # Пишем оффер напрямую в активный элемент (в поле ввода диалога)
            active_element = driver.switch_to.active_element
            active_element.send_keys(OFFER_TEXT)
            time.sleep(0.5)
            
            # Физически нажимаем Enter для отправки
            active_element.send_keys(Keys.ENTER)
            print(f"✅ Оффер успешно доставлен в сообщество ID: {group_id}")
            
            save_to_history(group_id)
        except Exception as e:
            print(f"❌ Ошибка отправки в ID {group_id}: {e}")
            
        # БИЗНЕС-ПАУЗА: случайный интервал, имитирующий человека
        sleep_time = random.randint(15, 25)
        print(f"⏳ Безопасная пауза: {sleep_time} секунд...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        # Сначала открываем TargetHunter, чтобы ты залогинился и вывел результат поиска фотографов
        print("🤖 Открываю TargetHunter. Авторизуйтесь и откройте таблицу результатов поиска...")
        driver.get("https://targethunter.ru") # Или используй точный URL панели, если сидишь на старой версии
        
        # Запускаем автоматический сбор ID с экрана
        if harvest_target_hunter_ids():
            # Переходим на ВК для выполнения рассылки в этой же сессии браузера
            print("\n🤖 Теперь переходим в ВК. Авторизуйтесь в своем аккаунте...")
            driver.get("https://vk.com")
            WebDriverWait(driver, 300).until(lambda d: "vk.com" in d.current_url)
            
            # Погнали рассылать
            run_vk_delivery()
            
    except KeyboardInterrupt:
        print("\n🤖 Робот остановлен.")
