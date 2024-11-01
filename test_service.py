import unittest
import requests
import logging

RECOMMENDATIONS_SERVICE_URL = "http://0.0.0.0:3000"
EVENTS_SERVICE_URL = "http://0.0.0.0:3001"
USER_ID = 0
ITEMS = [795836, 6705392, 32947997]
RECOMMENDATIONS_COUNT = 10
 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_service")

file_handler = logging.FileHandler("test_service.log", mode='w')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class TestRecommendationsService(unittest.TestCase):
    """
    Производит тестирования сервисов событий и рекомендаций
    """
    test_index = 1

    def log_response(self, test_name, response, expected_code, expected_data=None):
        """
        Настраивает логи для тестирования
        """
        logger.info(f"Test {self.test_index}: \"{test_name}\":")
        logger.info(f">>> Request URL: {response.request.url}")
        logger.info(f"<!> Expected: code={expected_code}, data={expected_data if expected_data is not None else '<any>'}")
        logger.info(f"<<< Response: code={response.status_code}, data={response.json()}")
        self.assertEqual(response.status_code, expected_code)
        if expected_data is not None:
            self.assertEqual(response.json(), expected_data)
        logger.info(f"Test {self.test_index} PASSED!")
        logger.info("----------------------------------------")
        TestRecommendationsService.test_index += 1

    def test_health_check_recommendations(self):
        """
        Тестируем работу сервиса рекомендаций
        """
        response = requests.get(f"{RECOMMENDATIONS_SERVICE_URL}/health", timeout=5)
        self.log_response("Health Check - Recommendations", response, 200, {"status": "ok"})

    def test_health_check_events(self):
        """
        Тестируем работу сервиса событий
        """
        response = requests.get(f"{EVENTS_SERVICE_URL}/health", timeout=5)
        self.log_response("Health Check - Events", response, 200, {"status": "ok"})

    def test_add_event(self):
        """
        Добавляет объект item_id в историю пользователя для тестирования онлайн-рекомендаций
        """
        for item_id in ITEMS:
            response = requests.post(
                f"{EVENTS_SERVICE_URL}/add", 
                json={"user_id": USER_ID, "item_id": item_id},
                timeout=5
            )

        response = requests.get(
            f"{EVENTS_SERVICE_URL}/get", 
            params={"user_id": USER_ID},
            timeout=5
        )
        self.log_response("Save Event History", response, 200)
        self.assertListEqual(response.json(), ITEMS)

    def test_get_cold_recommendations(self):
        """
        Получает персональные реклмендации для пользователя с исторей взаимодействия
        """
        response = requests.get(
            f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_cold",
            params={"k": RECOMMENDATIONS_COUNT},
            timeout=5
        )
        self.log_response("Get Cold Recommendations", response, 200)
        self.assertEqual(len(response.json()), RECOMMENDATIONS_COUNT)

    def test_get_online_recommendations(self):
        """
        Получает персональные реклмендации для пользователя с исторей взаимодействия
        """
        response = requests.get(
            f"{RECOMMENDATIONS_SERVICE_URL}/recommendations_online",
            params={"user_id": USER_ID, "k": RECOMMENDATIONS_COUNT},
            timeout=5
        )
        self.log_response("Get Online Recommendations", response, 200)
        self.assertEqual(len(response.json()), RECOMMENDATIONS_COUNT)

    def test_get_recommendations_missing_params(self):
        """
        Проверяет эндпоинт с рекомендациями для случая неправильного запроса
        """
        response = requests.get(
            f"{RECOMMENDATIONS_SERVICE_URL}/recommendations",
            timeout=5
        )
        self.log_response("Get Recommendations Missing Params", response, 422)

    def test_get_recommendations_wrong_user(self):
        """
        Проверяет эндпоинт с рекомендациями для случая несуществующего пользователя
        """
        response = requests.get(
            f"{RECOMMENDATIONS_SERVICE_URL}/recommendations",
            params={"user_id": -1, 'k': RECOMMENDATIONS_COUNT},
            timeout=5
        )
        self.log_response("Get Recommendations Wrong User", response, 200, [])

    def test_get_offline_recommendations(self):
        """
        Получает оффлайн рекомендации
        """
        response = requests.get(
            f"{RECOMMENDATIONS_SERVICE_URL}/offline_recommendations",
            params={"user_id": USER_ID, "k": RECOMMENDATIONS_COUNT},
            timeout=5
        )
        self.log_response("Get Offline Recommendations", response, 200)
        self.assertEqual(len(response.json()), RECOMMENDATIONS_COUNT)

if __name__ == "__main__":
    unittest.main()
