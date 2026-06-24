import time
import re
import json
import os
import vk_api

# ============================================================================
# АВТОНОМНЫЙ API-КОНВЕЙЕР WEBSCYE (ЛОКАЛЬНАЯ ВЕЧНАЯ БАЗА ДАННЫХ)
# ============================================================================
# 1. Твой рабочий токен ВК
VK_USER_TOKEN = "vk1.a.6mvBrZiZVyLLcKaNKQmnQEtGQ8f4cQgz3nu1oby1BpFrZ4sibLuBh0BnBFY9pn-iVBk4SSowvumU8nl0"

# Путь к локальному файлу базы данных в папке твоего проекта
JSON_DB_PATH = "database.json"

def save_to_local_db(name, email, role):
    """Бот напрямую записывает анкету клиента в локальный JSON-файл"""
    try:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        now = time.localtime()
        date_str = f"{months[now.tm_mon - 1]} {now.tm_mday}, {now.tm_year}"
        
        # Считываем текущую базу, если файл уже существует
        current_db = []
        if os.path.exists(JSON_DB_PATH):
            with open(JSON_DB_PATH, "r", encoding="utf-8") as f:
                try:
                    current_db = json.load(f)
                except:
                    current_db = []
                    
        # Проверка на дубликаты клиентов по контактам
        if any(u.get('email') == email for u in current_db):
            return

        # Формируем чистый пакет анкетной информации
        new_user = {
            "id": int(time.time()),
            "name": name,
            "email": email, # Почта или ссылка на переписку
            "role": role,
            "status": "Active",
            "date": date_str
        }
        
        current_db.append(new_user)
        
        # Перезаписываем локальный файл
        with open(JSON_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(current_db, f, ensure_ascii=False, indent=4)
            
        print(f"   [УСПЕХ] Контакт оцифрован в локальную базу: '{name}' | Контакт: {email} | Категория: {role}")
    except Exception as e:
        print(f"❌ [ОШИБКА ЗАПИСИ] {e}")

def main():
    print("🤖 Робот WebScye CRM успешно подключен к серверам ВК...")
    
    try:
        vk_session = vk_api.VkApi(token=VK_USER_TOKEN)
        vk = vk_session.get_api()
    except Exception as e:
        print(f"❌ [ОШИБКА ВК] Авторизация провалена: {e}")
        return

    print("🤖 Шаг 1. Глобальное сканирование истории сообщений ВК...")
    try:
        conversations = vk.messages.getConversations(count=200, filter="all")
        print(f"🤖 Проанализировано {len(conversations['items'])} активных диалогов. Запуск парсинга...")
        
        for item in conversations['items']:
            peer = item['conversation']['peer']
            peer_id = peer['id']
            
            if peer['type'] == 'user':
                history = vk.messages.getHistory(peer_id=peer_id, count=20)
                
                for msg in history['items']:
                    if msg['out'] == 1 or msg['from_id'] == item['conversation']['current_id']:
                        text = msg['text']
                        text_lower = text.lower()
                        
                        if "тариф" in text_lower:
                            user_data = vk.users.get(user_ids=peer_id)[0]
                            client_name = f"{user_data['first_name']} {user_data['last_name']}"
                            
                            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                            client_contact = email_match.group(0).lower() if email_match else f"://vk.com{peer_id}"
                            
                            role = "Professional"
                            if "фото" in text_lower or "свад" in text_lower: role = "Starter"
                            elif "строит" in text_lower or "ремонт" in text_lower: role = "Enterprise"
                            
                            save_to_local_db(client_name, client_contact, role)
                            break
    except Exception as e:
        print(f"❌ [ОШИБКА СБОРА] {e}")

    print("\n🤖 Шаг 2. Исторический сбор завершен. База оцифрована локально.")
    print("🤖 Робот слушает новые исходящие сообщения в реальном времени...")
    
    from vk_api.longpoll import VkLongPoll, VkEventType
    longpoll = VkLongPoll(vk_session)
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.from_me:
            text = event.text
            text_lower = text.lower()
            
            if "тариф" in text_lower:
                print(f"🔥 Новый запрос зафиксирован в переписке с ID: {event.peer_id}!")
                try:
                    user_data = vk.users.get(user_ids=event.peer_id)[0]
                    client_name = f"{user_data['first_name']} {user_data['last_name']}"
                except:
                    client_name = f"B2B Клиент #{event.peer_id}"
                
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                client_contact = email_match.group(0).lower() if email_match else f"://vk.com{event.peer_id}"
                
                role = "Professional"
                if "фото" in text_lower or "свад" in text_lower: role = "Starter"
                elif "строит" in text_lower or "ремонт" in text_lower: role = "Enterprise"
                
                save_to_local_db(client_name, client_contact, role)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🤖 Робот остановлен.")
