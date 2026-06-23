import time
import re
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================================
# КОНФИГУРАЦИЯ ХОЛДИНГА WEBSCYE
# ============================================================================
# Токен группы ВК (берется в настройках группы -> Работа с API -> Создать токен)
VK_TOKEN = "vk1.a.7AObYEBCRmsjPLc9iFJEIwFuxAwt3-01pSHl4GKwE9eWi_iIJ1-6xmjz-TTGRo43RTjSiPegWk6-z8-phGCqOoSog-8lUk6l55XtOYj3L2yqyFLanRFX06RCdr0_qfq2D7Db7w0KKB3A7WYgIV_9MOW-H_htUooMhgpLZzNhGeuLFxWlU70vFWU4_m-0je2X52tDJCw-kSuNGAFtlpzPew" 
CRM_URL = "https://annekovakra.github.io/WebScyeCRM/"

# Настройка скрытого браузера Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless") # Бот работает незаметно в фоне
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def inject_to_crm(name, vk_link, role, price):
    """Робот открывает CRM и выполняет инжекцию данных во Flat-Files базу"""
    try:
        driver.get(CRM_URL)
        time.sleep(2) # Ждем загрузки матового стекла
        
        # Вызываем нашу JS-функцию напрямую в браузере
        script = f"return window.addLeadFromBot('{name}', '{vk_link}', '{role}', '{price}');"
        result = driver.execute_script(script)
        
        if result == "OK":
            print(f"🤖 [УСПЕХ] Робот оцифровал клиента: {name} | Тариф: {role} | {price} ₽")
    except Exception as e:
        print(f"❌ [ОШИБКА БОТА] Не удалось передать данные в CRM: {e}")

def main():
    print("🤖 Робот-интегратор WebScye запущен и слушает диалоги ВК...")
    
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    for event in longpoll.listen():
        # Бот перехватывает ОДНОТИПНЫЕ исходящие сообщения от твоего продажника
        if event.type == VkEventType.MESSAGE_NEW and event.from_me:
            text = event.text.lower()
            
            # Триггер: бот срабатывает только тогда, когда продажник пишет клиенту цену
            if "тариф" in text or "рублей" in text or "₽" in text:
                print(f"🤖 Фиксация активности продажника в диалоге: {event.peer_id}")
                
                try:
                    # Бот сам вытаскивает инфу о паблике/клиенте через VK API
                    peer_info = vk.messages.getConversationMembers(peer_id=event.peer_id)
                    # Вытаскиваем имя группы или ЛПР
                    group_data = vk.groups.getById(group_id=abs(event.peer_id))[0]
                    group_name = group_data['name']
                    vk_link = f"://vk.com{abs(event.peer_id)}"
                except:
                    group_name = f"Локальный клиент #{event.peer_id}"
                    vk_link = f"://vk.com{event.peer_id}"

                # УМНЫЙ ПАРСИНГ ЦЕНЫ: Бот ищет цифры в сообщении продажника
                prices = [int(s) for s in re.findall(r'\b\d+\b', event.text)]
                # Если продажник написал цену (например, 11120 или 7999), бот её заберет
                guessed_price = prices[0] if prices else 15000 
                
                # Авто-определение роли
                guessed_role = "Professional"
                if guessed_price < 8000: guessed_role = "Starter"
                if guessed_price > 20000: guessed_role = "Enterprise"

                # Моментальный перенос данных в твою CRM на GitHub Pages
                inject_to_crm(group_name, vk_link, guessed_role, guessed_price)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
      driver.quit()
    print("\n Робот остановлен.")
