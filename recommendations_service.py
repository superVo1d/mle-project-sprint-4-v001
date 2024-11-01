import logging
import requests
from contextlib import asynccontextmanager
from typing import List
import pandas as pd
import random
from fastapi import FastAPI

logger = logging.getLogger("uvicorn.error")

EVENTS_SERVICE_URL = "http://0.0.0.0:3001"

class FeatureStore:
    def __init__(self):
        self._similar_items = None
        self._recommendations = None
        self._popular = None

    def load(self):
        """
        Загружаем данные из файлов
        """
        logger.info("Loading data...")

        self._similar_items = pd.read_parquet('similar.parquet')
        self._similar_items = self._similar_items[["item_id", "recomendations", "score"]]
        self._similar_items.set_index('item_id', inplace=True, drop=True)
        self._similar_items.rename(columns={"recomendations": "item_id"}, inplace=True)

        self._recommendations = pd.read_parquet('recommendations.parquet')
        self._recommendations = self._recommendations[["user_id", "item_id", "cb_score"]]
        self._recommendations.rename(columns={"cb_score": "score"}, inplace=True)
        self._recommendations.set_index('user_id', inplace=True, drop=True)

        self._popular = pd.read_parquet('top_popular.parquet')
        self._popular = self._popular[['item_id']]
        self._popular.reset_index(drop=True, inplace=True)
        self._popular['score'] = range(1, len(self._popular) + 1)

        logger.info("Data is loaded.")

    def get_similar_items(self, item_id: int, k: int = 10):
        """
        Возвращает список похожих объектов
        """
        try:
            i2i = self._similar_items.loc[item_id].head(min(k, 10))
            i2i = i2i[["item_id", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            i2i = {"item_id": [], "score": {}}

        return i2i

    def get_personal_recommendations(self, user_id: int, k: int = 10):
        """
        Возвращает персональные рекомендации для данного пользователя
        """
        try:
            recs = self._recommendations.loc[user_id].head(min(k, 10))
            recs = recs[["item_id", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            recs = {"item_id": [], "score": {}}

        return recs

    def get_popular_items(self, k: int = 10):
        """
        Возвращает наиболее популярные объекты
        """
        try:
            recs = self._popular.head(min(k, 10))
            recs = recs[["item_id", "score"]].to_dict(orient="list")
        except KeyError:
            logger.error("No recommendations found")
            recs = {"item_id": [], "score": {}}

        return recs

feature_store = FeatureStore()

@asynccontextmanager
async def lifespan(app: FastAPI):
    feature_store.load()
    logger.info("Ready!")
    yield


app = FastAPI(title="Recommendations Service", lifespan=lifespan)

@app.get("/recommendations")
async def mixed_recommendations(user_id: int, k: int = 10) -> List[int]:
    """
    Возвращает скисок рекомендаций длиной k для user_id
    на основе его истории и персональных рекомендаций
    """

    # Получим историю взаимодействий данного пользователя
    items = []
    try:
        params = {"user_id": user_id}
        response = requests.get(EVENTS_SERVICE_URL + "/get", params=params, timeout=5)
        items = response.json()
    except requests.exceptions.RequestException as e:
        print("Events service request error:", e)

    # Удалим повторяющиеся элементы
    items = list(set(items))

    # Достаем персональные рекомендации
    recommendations = feature_store.get_personal_recommendations(user_id, k).get("item_id")

    def blend_lists(list1, list2):
        """
        Смешивает два списка рекомендаций по порядку
        """
        max_len = len(list1) + len(list2)
        combined = []

        i = 0
        j = 0

        while len(combined) < max_len:
            if i < len(list1):
                if not list1[i] in combined:
                    combined.append(list1[i])
                i += 1

            if j < len(list2):
                if not list2[j] in combined:
                    combined.append(list2[j])
                j += 1

        return combined[:k]

    # Для каждого объекта в истории пользователя найдем похожие (выбререм случайные 10)
    similar_items = []
    for item_id in items:
        similar_item_id = feature_store.get_similar_items(item_id=item_id, k = k).get('item_id')
        similar_items.extend(similar_item_id)

    # Удалим дубликаты
    similar_items = list(set(similar_items))

    random.seed(42)

    # Смешаем оффлайн и онлайн рекомендации (выбререм случайные k)
    return blend_lists(recommendations, random.sample(similar_items, k))

@app.get("/recommendations_cold")
async def cold_recommendations(k: int = 10) -> List[int]:
    """
    Возвращает скисок рекомендаций длиной k для пользователя без истории взаимодействий
    """

    return feature_store.get_popular_items(k).get("item_id")

@app.get("/recommendations_online")
async def online_recommendations(user_id: int, k: int = 10) -> List[int]:
    """
    Возвращает скисок рекомендаций длиной k для user_id на основе его истории
    """

    # Получим историю взаимодействий данного пользователя
    items = []
    try:
        params = {"user_id": user_id}
        response = requests.get(EVENTS_SERVICE_URL + "/get", params=params, timeout=5)
        items = response.json()
    except requests.exceptions.RequestException as e:
        print("Events service request error:", e)

    # Удалим повторяющиеся элементы
    items = list(set(items))

    # Для каждого объекта в истории пользователя найдем похожие
    similar_items = []
    for item_id in items:
        similar_item_id = feature_store.get_similar_items(item_id=item_id, k = k).get('item_id')
        similar_items.extend(similar_item_id)

    # Удалим дубликаты
    similar_items = list(set(similar_items))
    
    random.seed(42)

    # Выбререм случайные k
    return random.sample(similar_items, k)

@app.get("/offline_recommendations")
async def offline_recommendations(user_id: int, k: int = 10) -> List[int]:
    """
    Возвращает скисок персональных рекомендаций длиной k для user_id
    """

    return feature_store.get_personal_recommendations(user_id, k).get("item_id")
