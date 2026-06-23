import time
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================================
# АВТОНОМНЫЙ РОБОТ-БУФЕР WEBSCYE (ПУЛЕНЕПРОБИВАЕМАЯ АВТОМАТИЗАЦИЯ)
# ============================================================================
CRM_URL = "https://annekovakra.github.io/WebScyeCRM/users.htmlзш"

print("🤖 Запуск робота-буфера WebScye...")

# Запускаем браузер в фоновом (скрытом) режиме, чтобы он не мешал работать
options = webdriver.ChromeOptions()
options.add_argument("--headless") 
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def inject_to_crm(client_name):
    """Робот мгновенно вшивает скопированного клиента в твою CRM на GitHub Pages"""
    try:
        driver.get(CRM_URL)
        time.sleep(3) # Даем матовому стеклу надежно прогрузиться
        
        # Генерируем уникальную техническую ссылку для CRM
        vk_link = f"://vk.com{int(time.time())}"
        
        # Вызываем JS-функцию на твоем сайте напрямую
        script = f"return window.addLeadFromBot('{client_name}', '{vk_link}', 'Professional', 11120);"
        result = driver.execute_script(script)
        
        if result == "OK":
            print(f"   [УСПЕХ] Робот оцифровал лида: '{client_name}' | 11120 \u20bd")
    except Exception as e:
        print(f"❌ [ОШИБКА ИНЖЕКЦИИ] {e}")


def monitor_clipboard():
    print("🤖 Робот активен! Слушаю буфер обмена (Ctrl + C)...")
    print("💡 ИНСТРУКЦИЯ: Просто выдели имя фотографа или название группы в ВК и нажми Ctrl+C!")
    
    # Запоминаем текущее содержимое буфера, чтобы не спамить
    last_copied = pyperclip.paste().strip()
    
    while True:
        try:
            # Каждую секунду проверяем, что лежит в буфере обмена
            current_copied = pyperclip.paste().strip()
            
            # Если в буфер попал новый текст и это не пустая строка
            if current_copied != last_copied and current_copied != "":
                # Защита: если скопирована ссылка на сам ВК, игнорируем
                if "vk.com" not in current_copied and len(current_copied) < 60:
                    print(f"🔥 Обнаружен новый клиент в буфере: '{current_copied}'")
                    
                    # Мгновенно отправляем данные в твою CRM на гитхаб
                    inject_to_crm(current_copied)
                
                last_copied = current_copied
                
            time.sleep(1) # Опрос буфера раз в секунду
        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    try:
        monitor_clipboard()
    except KeyboardInterrupt:
        driver.quit()
        print("\n🤖 Робот остановлен.")
