import requests

RECOMMENDATIONS_SERVICE_URL = "http://0.0.0.0:3000"
EVENTS_SERVICE_URL = "http://0.0.0.0:3001"

USER_ID = 0
ITEMS = [795836, 6705392, 32947997]
RECOMMENDATIONS_COUNT = 10

def test_health_check_recommendations():
    """
    Тестируем работу сервиса рекомендаций
    """
    response = requests.get(f"{RECOMMENDATIONS_SERVICE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_check_events():
    """
    Тестируем работу сервиса событий
    """
    response = requests.get(f"{EVENTS_SERVICE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_add_event():
    """
    Добавляет объект item_id в историю пользователя для тестирования онлайн-рекомендаций
    """
    for item_id in ITEMS:
        response = requests.post(
            f"{EVENTS_SERVICE_URL}/add", 
            json={"user_id": USER_ID, "item_id": item_id},
            timeout=5
        )
        assert response.status_code == 200
        print(response.json())

    response = requests.get(
        f"{EVENTS_SERVICE_URL}/get", 
        params={"user_id": USER_ID},
        timeout=5
    )
    assert response.status_code == 200
    response = response.json()
    assert all(x == y for x, y in zip(ITEMS, response))
    print(response)

def test_get_cold_recommendations():
    """
    Получает персональные реклмендации для пользователя с исторей взаимодействия
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_cold",
        params={"k": RECOMMENDATIONS_COUNT},
        timeout=5
    )
    assert response.status_code == 200
    assert len(response.json()) == RECOMMENDATIONS_COUNT
    print(response.json())

def test_get_recommendations():
    """
    Получает персональные реклмендации для пользователя с исторей взаимодействия
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_online", 
        params={"user_id": USER_ID, "k": RECOMMENDATIONS_COUNT},
        timeout=5
    )
    assert response.status_code == 200
    assert len(response.json()) == RECOMMENDATIONS_COUNT
    print(response.json())

def test_get_recommendations_missing_params():
    """
    Проверяет эндпоинт с рекомендациями для случая неправильного запроса
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations", 
        timeout=5
    )
    assert response.status_code == 422
    print(response.json())

def test_get_recommendations_wrong_user():
    """
    Проверяет эндпоинт с рекомендациями для случая несуществующего пользователя
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations",
        params={"user_id": -1, 'k': RECOMMENDATIONS_COUNT},
        timeout=5
    )
    assert response.status_code == 200
    assert response.json() == []

def test_get_online_recommendations():
    """
    Получает онлайн рекомендации
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_online", 
        params={"user_id": USER_ID, "k": RECOMMENDATIONS_COUNT},
        timeout=5
    )
    assert response.status_code == 200
    assert len(response.json()) == RECOMMENDATIONS_COUNT
    print(response.json())

def test_get_offline_recommendations():
    """
    Получает оффлайн рекомендации
    """
    response = requests.get(
        f"{RECOMMENDATIONS_SERVICE_URL}/offline_recommendations", 
        params={"user_id": USER_ID, "k": RECOMMENDATIONS_COUNT},
        timeout=5
    )
    assert response.status_code == 200
    assert len(response.json()) == RECOMMENDATIONS_COUNT
    print(response.json())
