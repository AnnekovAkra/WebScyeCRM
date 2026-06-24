import time
import os
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# МЕЖДУНАРОДНЫЙ КОМБАЙН WEBSCYE: АВТО-ПЕРЕВОД + РАССЫЛКА ПО ВСЕМУ МИРУ
# ============================================================================

# Шаблоны офферов на разных языках мира холдинга WebScye
OFFERS = {
    "ru": "Здравствуйте! Я ведущий разработчик холдинга WebScye. Мы подготовили готовое ИТ-решение для автоматизации и привлечения клиентов конкретно под ваше направление. Если вам актуально масштабирование бизнеса, напишите нам.",
    "en": "Hello! I am a lead developer at WebScye. We have prepared a turnkey IT solution to automate operations and attract more clients specifically for your photography business. If you are looking to scale, let us know.",
    "es": "¡Hola! Soy desarrollador principal en WebScye. Hemos preparado una solución tecnológica a medida para automatizar operaciones y captar más clientes específicamente para su negocio de fotografía. Si busca escalar, escríbanos.",
    "fr": "Bonjour! Je suis développeur principal chez WebScye. Nous avons préparé une solution informatique clé en main для автоматизации и привлечения клиентов для вашего фотобизнеса. Si vous souhaitez vous développer, contactez-nous.",
    "de": "Hallo! Ich bin Chefentwickler bei WebScye. Wir haben eine maßgeschneiderte IT-Lösung entwickelt, um Abläufe zu automatisieren und mehr Kunden speziell für Ihr Fotografie-Unternehmen zu gewinnen. Wenn Sie expandieren möchten, schreiben Sie uns.",
    "it": "Ciao! Sono uno sviluppatore principale di WebScye. Abbiamo preparato una soluzione IT su misura per automatizzare le operazioni e trovare più clienti specificamente per la tua attività di fotografia. Se vuoi scalare, scrivici."
}

TARGETS_FILE = "targets.txt"
HISTORY_FILE = "sent_history.txt"

print("🤖 Инициализация международного робота WebScye Global...")

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

def detect_language(text):
    """Умный лингвистический анализатор: определяет язык по названию группы"""
    text_low = text.lower()
    if any(w in text_low for w in ["photographe", "séance", "mariage"]): return "fr"
    if any(w in text_low for w in ["fotógrafo", "sesión", "bodas"]): return "es"
    if any(w in text_low for w in ["hochzeitsfotograf", "fotoshooting", "fotostudio"]): return "de"
    if any(w in text_low for w in ["servizio", "matrimoni", "fotografico"]): return "it"
    if any(w in text_low for w in ["photographer", "wedding", "photoshoot", "studio", "videographer", "portfolio"]): return "en"
    return "ru" # Если иностранных слов нет, шлем на русском

def harvest_target_hunter_ids():
    """Сбор ID групп и названий прямо из открытого окна TargetHunter"""
    print("\n🕵️ Шаг 1. Сбор базы в TargetHunter.")
    print("💡 ИНСТРУКЦИЯ: Выполните мировой поиск по нашему мультиязычному списку слов.")
    print("💡 Когда увидите таблицу результатов, вернитесь сюда...")
    input("⌨️ Нажмите [ENTER] в терминале для перехвата ID с экрана...")
    
    print("🤖 Сканирую HTML-код TargetHunter...")
    page_source = driver.page_source
    
    # Регулярка для сбора пар [ID группы, Название группы] из верстки TargetHunter
    # (Она аккуратно вытаскивает метаданные, чтобы мы знали, как называется группа)
    raw_pairs = re.findall(r'(?:club|public|group|id|vk\.com\/|-)(\d{5,15}).*?>(.*?)<\/a>', page_source)
    
    if len(raw_pairs) == 0:
        # ЕслиTH обновил верстку таблиц, собираем по общему списку элементов ссылок
        links = driver.find_elements(By.XPATH, "//a[contains(@href, 'vk.com')]")
        unique_data = {}
        for link in links:
            try:
                href = link.get_attribute("href")
                name = link.text.strip()
                match = re.search(r'(?:club|public|sel=-\s*)(\d+)', href)
                if match and name:
                    unique_data[match.group(1)] = name
            except:
                continue
    else:
        unique_data = {pid: name.strip() for pid, name in raw_pairs if name.strip()}

    if len(unique_data) == 0:
        print("❌ База пуста! Убедитесь, что на экране в TargetHunter открыт результат поиска.")
        return False
        
    print(f"🔥 УСПЕХ! Робот WebScye перехватил {len(unique_data)} мировых фотографов!")
    
    # Сохраняем базу в формате: ID ||| Название группы
    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
        for gid, gname in unique_data.items():
            f.write(f"{gid}|||{gname}\n")
    return True

def run_vk_delivery():
    """Запуск веерной рассылки с автоматическим определением языка"""
    print("\n🚀 Шаг 2. Запуск международной рассылки офферов...")
    
    if not os.path.exists(TARGETS_FILE):
        print("❌ Ошибка: Файл базы не найден.")
        return

    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if "|||" in line]

    history = load_history()
    successful_sends = 0

    for line in lines:
        group_id, group_name = line.split("|||", 1)
        
        if group_id in history:
            continue

        # Автоматически определяем язык группы по её названию
        lang = detect_language(group_name)
        chosen_offer = OFFERS[lang]

        direct_chat_url = f"https://vk.com{group_id}"
        print(f"\n👉 Открываю чат с ID: {group_id} | Группа: '{group_name}' | Язык оффера: [{lang.upper()}]")
        
        try:
            driver.get(direct_chat_url)
            time.sleep(3.5) # Ждем фокуса в окне диалога
            
            # Пишем переведенный текст оффера напрямую в поле ввода
            active_element = driver.switch_to.active_element
            active_element.send_keys(chosen_offer)
            time.sleep(0.5)
            
            # Отправка по Enter
            active_element.send_keys(Keys.ENTER)
            print(f"✅ Оффер на языке [{lang.upper()}] успешно доставлен!")
            successful_sends += 1
            
            save_to_history(group_id)
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            
        # БИЗНЕС-ПАУЗА ИМИТАЦИИ ЧЕЛОВЕКА
        sleep_time = random.randint(15, 25)
        print(f"⏳ Безопасная пауза: {sleep_time} секунд...")
        time.sleep(sleep_time)

    print(f"\n🏁 Глобальная мировая экспансия завершена! Оцифровано лидов: {successful_sends}")

if __name__ == "__main__":
    try:
        print("🤖 Открываю TargetHunter. Авторизуйтесь и запустите мировой поиск...")
        driver.get("https://targethunter.ru")
        
        if harvest_target_hunter_ids():
            print("\n🤖 Теперь переходим в ВК. Авторизуйтесь в своем аккаунте...")
            driver.get("https://vk.com")
            WebDriverWait(driver, 300).until(lambda d: "vk.com" in d.current_url)
            
            run_vk_delivery()
            
    except KeyboardInterrupt:
        print("\n🤖 Робот остановлен.")
