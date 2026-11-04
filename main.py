import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.aiai.by/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    if not user_text or user_text.strip() == "":
        return {
            "version": body["version"],
            "session": body["session"],
            "response": {
                "end_session": False,
                "text": "Привет! Я готов к общению. Задай свой вопрос."
            }
        }

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": user_text}],
        }
    )

    try:
        data = response.json()
        if isinstance(data, list):
            answer = data[0]["choices"][0]["message"]["content"]
        else:
            answer = data["choices"][0]["message"]["content"]
    except Exception as e:
        print("ОШИБКА ПАРСИНГА:", e)
        print("СЫРОЙ ОТВЕТ:", response.text)
        answer = "Извините, произошла ошибка при обработке ответа."

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
