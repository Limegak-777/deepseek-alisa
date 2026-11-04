import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.aiai.by/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.api_route("/", methods=["GET", "HEAD", "POST"])
async def main(request: Request):
    # Если пришел GET или HEAD запрос (проверка UptimeRobot), просто отвечаем OK
    if request.method in ["GET", "HEAD"]:
        return {"status": "ok"}

    # Обработка POST-запроса от Алисы
    try:
        body = await request.json()
        user_text = body["request"]["original_utterance"]
    except Exception:
        return {"status": "error", "message": "Invalid request format"}

    # Если Алиса прислала пустоту (например, при открытии навыка)
    if not user_text or user_text.strip() == "":
        return {
            "version": body.get("version", "1.0"),
            "session": body.get("session", {}),
            "response": {
                "end_session": False,
                "text": "Привет! Я готов к общению. Задай свой вопрос."
            }
        }

    # Запрос к AIAI.BY с быстрой моделью
    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "gpt-4o-mini",  # Быстрая модель, чтобы уложиться в лимит Алисы
                "messages": [{"role": "user", "content": user_text}],
                "max_tokens": 100  # Ограничиваем длину, чтобы ответ был быстрее
            },
            timeout=4  # Если AIAI.BY не ответит за 4 секунды, мы прервем запрос
        )
        
        data = response.json()
        
        # Извлекаем ответ (поддерживаем и список, и словарь)
        if isinstance(data, list):
            answer = data[0]["choices"][0]["message"]["content"]
        else:
            answer = data["choices"][0]["message"]["content"]
            
    except requests.exceptions.Timeout:
        answer = "Извини, я задумался. Попробуй спросить еще раз."
    except Exception as e:
        print("ОШИБКА:", e)
        print("СЫРОЙ ОТВЕТ:", response.text if 'response' in locals() else "Нет ответа")
        answer = "Извини, произошла ошибка. Попробуй позже."

    # Возвращаем ответ Алисе
    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {
            "end_session": False,
            "text": answer
        }
    }
