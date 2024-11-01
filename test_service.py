import requests

RECOMMENDATIONS_SERVICE_URL = "http://0.0.0.0:3000"
EVENTS_SERVICE_URL = "http://0.0.0.0:3001"

USER_ID = 0
ITEMS = [795836, 6705392, 32947997]

def test_add_event(user_id, item_id):
    """
    Добавляет объект item_id в историю пользователя для тестирования онлайн-рекомендаций
    """
    response = requests.post(
        f"{EVENTS_SERVICE_URL}/add", 
        json={"user_id": user_id, "item_id": item_id},
        timeout=5
    )
    print(response.json())

def test_get_cold_recommendations(k=10):
    """
    Получает персональные реклмендации для пользователя с исторей взаимодействия
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_cold",
        params={"k": k},
        timeout=5
    )
    print(response.json())

def test_get_recommendations(user_id, k=10):
    """
    Получает персональные реклмендации для пользователя с исторей взаимодействия
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations", 
        params={"user_id": user_id, "k": k},
        timeout=5
    )
    print(response.json())

def test_get_online_recommendations(user_id, k=10):
    """
    Получает онлайн рекомендации
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_online", 
        params={"user_id": user_id, "k": k},
        timeout=5
    )
    print(response.json())

def test_get_offline_recommendations(user_id, k=10):
    """
    Получает оффлайн рекомендации
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/offline_recommendations", 
        params={"user_id": user_id, "k": k},
        timeout=5
    )
    print(response.json())

if __name__ == "__main__":
    print('Рекомендации холодного старта:')
    test_get_cold_recommendations()

    print('Оффлайн-рекомендации:')
    test_get_offline_recommendations(USER_ID)

    print('Добавляем объекты в историю пользователя:')
    for item in ITEMS:
        test_add_event(USER_ID, item)

    print('Онлайн-рекомендации:')
    test_get_online_recommendations(USER_ID)

    print('Рекомендации на основе оффлайн- и онлайн-истории:')
    test_get_recommendations(USER_ID)
