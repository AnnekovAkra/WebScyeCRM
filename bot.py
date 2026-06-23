import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# ============================================================================
# АВТОНОМНЫЙ API-РОБОТ ХОЛДИНГА WEBSCYE (РАБОТАЕТ БЕЗ БРАУЗЕРА)
# ============================================================================
# Вставь сюда свой скопированный токен из vkhost
VK_USER_TOKEN = "vk1.a.7AObYEBCRmsjPLc9iFJEIwFuxAwt3-01pSHl4GKwE9eWi_iIJ1-6xmjz-TTGRo43RTjSiPegWk6-z8-phGCqOoSog-8lUk6l55XtOYj3L2yqyFLanRFX06RCdr0_qfq2D7Db7w0KKB3A7WYgIV_9MOW-H_htUooMhgpLZzNhGeuLFxWlU70vFWU4_m-0je2X52tDJCw-kSuNGAFtlpzPew"

def main():
    print("🤖 Робот WebScye CRM запущен напрямую через API и слушает твои диалоги...")
    
    try:
        vk_session = vk_api.VkApi(token=VK_USER_TOKEN)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()
    except Exception as e:
        print(f"❌ Ошибка авторизации ВК токена: {e}")
        return

    # Бот уходит в бесконечное прослушивание твоей личной страницы
    for event in longpoll.listen():
        # Робот реагирует ТОЛЬКО на твои исходящие сообщения (когда продажник отправляет текст клиенту)
        if event.type == VkEventType.MESSAGE_NEW and event.from_me:
            text_lower = event.text.lower()
            
            # Наш единственный триггер — бот сработает, когда продажник пишет слово "тариф"
            if "тариф" in text_lower:
                print(f"🔥 Триггер обнаружен в диалоге: {event.peer_id}")
                
                try:
                    # Бот мгновенно запрашивает Имя и Фамилию клиента напрямую у серверов ВК по его ID
                    user_data = vk.users.get(user_ids=event.peer_id)[0]
                    client_name = f"{user_data['first_name']} {user_data['last_name']}"
                except:
                    client_name = f"B2B Клиент #{event.peer_id}"
                
                vk_link = f"://vk.com{event.peer_id}"
                
                # Автоматическое определение роли по контексту
                role = "Professional"
                if "фото" in text_lower or "свад" in text_lower:
                    role = "Starter"
                elif "строит" in text_lower or "ремонт" in text_lower:
                    role = "Enterprise"
                
                # ТАК КАК ХОСТИНГ GITHUB СТАТИЧЕСКИЙ, БОТ ПРОСТО ВЫВОДИТ ГОТОВЫЙ ШЛАНГ ДАННЫХ ДЛЯ CRM
                print(f"\n👉 [СКОПИРУЙ СТРОКУ НИЖЕ И ВСТАВЬ В СВОЮ CRM В ПОЛЕ SMART IMPORT]:")
                print(f"{client_name} | {vk_link} | {role}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🤖 Робот остановлен.")
