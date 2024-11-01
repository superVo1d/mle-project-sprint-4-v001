# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.
Для запуска сервиса рекомендаций последовательно выполните команды:
```
python3 -m venv env_recsys_start
source env_recsys_start/bin/activate
pip install -r requirements.txt

source env_recsys_start/bin/activate
uvicorn recommendations_service:app --host "0.0.0.0"  --port 3000

<Открыть новый терминал>
source env_recsys_start/bin/activate
uvicorn events_service:app --host "0.0.0.0"  --port 3001
```

## Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.
```
<Открыть новый терминал>
source env_recsys_start/bin/activate
pytest test_service.py > test_service.log 2>&1

```

**Примечание**

 Онлайн- и офлайн-рекомендации смешиваются путем чередования
 рекомендованных объектов по четным и нечетным позициям.
